#!/bin/zsh
# Arma release/arxiv/delegation-divide-arxiv.tar.gz desde articulo/ y comprueba que compila en un directorio limpio.
# Contenido: main.tex (con \pdfoutput=1), secciones/, tablas/, fig/ (solo los PDF que se usan), cifras.tex, main.bbl.
# No incluye referencias.bib (arXiv usa main.bbl). Quita los comentarios % que contienen TODO, VERIFY o INTERPRETAR
# (respeta \% y los entornos verbatim). No sube nada: el envío a arXiv lo hace Cristian a mano.
# Uso: zsh release/arxiv/empaquetar.sh
set -eu -o pipefail
RAIZ=${0:A:h:h:h}
ART=$RAIZ/articulo
OUT=$RAIZ/release/arxiv
TAR=$OUT/delegation-divide-arxiv.tar.gz
PY=($RAIZ/.venv/bin/python -I)

[[ -f $ART/main.bbl ]] || { echo "falta articulo/main.bbl: compila antes el artículo (articulo/reproducir.sh)" >&2; exit 1; }
[[ -f $ART/cifras.tex ]] || { echo "falta articulo/cifras.tex" >&2; exit 1; }
if grep -q "sintetico\s*true\|\\\\sinteticotrue" $ART/cifras.tex; then
  echo "cifras.tex marca el índice como SINTÉTICO: no se empaqueta" >&2; exit 1
fi

ST=$(mktemp -d "${TMPDIR:-/tmp}/arxiv-stage.XXXXXX")
CK=$(mktemp -d "${TMPDIR:-/tmp}/arxiv-check.XXXXXX")
trap 'rm -rf $ST $CK' EXIT

# 1. copiar fuentes y figuras usadas, quitando comentarios marcados
$PY - "$ART" "$ST" <<'PYEOF'
import re, shutil, sys
from pathlib import Path

art, st = Path(sys.argv[1]), Path(sys.argv[2])
MARCA = re.compile(r"TODO|VERIFY|INTERPRETAR")
VERB_INI = re.compile(r"\\begin\{(verbatim\*?|Verbatim|lstlisting|minted)\}")
VERB_FIN = re.compile(r"\\end\{(verbatim\*?|Verbatim|lstlisting|minted)\}")

def comentario(linea: str) -> int:
    """Índice del primer % no escapado (número par de \\ antes), saltando \\verb<d>...<d>; -1 si no hay."""
    i = 0
    while i < len(linea):
        if linea.startswith("\\verb", i) and i + 5 < len(linea) and not linea[i + 5].isalpha():
            d = linea[i + 5]
            j = linea.find(d, i + 6)
            i = len(linea) if j < 0 else j + 1
            continue
        if linea[i] == "%":
            k, n = i - 1, 0
            while k >= 0 and linea[k] == "\\":
                n += 1; k -= 1
            if n % 2 == 0:
                return i
        i += 1
    return -1

quitados = []
def limpiar(src: Path, dst: Path):
    out, en_verb = [], False
    for n, l in enumerate(src.read_text(encoding="utf-8").splitlines(keepends=True), 1):
        if en_verb:
            out.append(l)
            if VERB_FIN.search(l): en_verb = False
            continue
        if VERB_INI.search(l) and not VERB_FIN.search(l):
            en_verb = True
            out.append(l); continue
        i = comentario(l)
        if i >= 0 and MARCA.search(l[i:]):
            quitados.append(f"{src.relative_to(art)}:{n}: {l[i:].strip()[:90]}")
            codigo = l[:i]
            if codigo.strip():
                out.append(codigo + "%\n")       # conserva el % para no introducir espacio
            continue                              # línea solo-comentario: se elimina (no aporta nada)
        out.append(l)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("".join(out), encoding="utf-8")

fuentes = [art / "main.tex", art / "cifras.tex", *sorted((art / "secciones").glob("*.tex")), *sorted((art / "tablas").glob("*.tex"))]
for f in fuentes:
    limpiar(f, st / f.relative_to(art))
main = st / "main.tex"
main.write_text("\\pdfoutput=1\n" + main.read_text(encoding="utf-8"), encoding="utf-8")
shutil.copyfile(art / "main.bbl", st / "main.bbl")

# figuras: solo las que se usan en \includegraphics
usadas = set()
for f in st.rglob("*.tex"):
    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", f.read_text(encoding="utf-8")):
        usadas.add(m.group(1))
for u in sorted(usadas):
    p = art / u
    p = p if p.suffix else p.with_suffix(".pdf")
    if not p.exists():
        sys.exit(f"figura usada pero ausente: {p}")
    (st / p.relative_to(art)).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(p, st / p.relative_to(art))
print(f"fuentes {len(fuentes)}, figuras {len(usadas)}, comentarios quitados {len(quitados)}")
for q in quitados: print("  -", q)
PYEOF

# 2. tarball determinista (orden fijo, sin metadatos de usuario)
mkdir -p $OUT
(cd $ST && find . -type f | LC_ALL=C sort | sed 's|^\./||' > ../arxiv-files.$$ && \
  COPYFILE_DISABLE=1 tar --uid 0 --gid 0 --uname "" --gname "" -czf $TAR -T ../arxiv-files.$$ ; rm -f ../arxiv-files.$$)
echo "tarball: $TAR ($(du -h $TAR | cut -f1), $(tar -tzf $TAR | wc -l | tr -d ' ') archivos)"
if tar -tzf $TAR | grep -q '\.bib$'; then echo "ERROR: el tarball trae .bib" >&2; exit 1; fi

# 3. compilar en un directorio limpio: pdflatex ×2, sin bibtex (usa main.bbl)
tar -xzf $TAR -C $CK
(cd $CK && pdflatex -interaction=nonstopmode -halt-on-error main.tex > pase1.txt 2>&1 && \
           pdflatex -interaction=nonstopmode -halt-on-error main.tex > pase2.txt 2>&1) || {
  echo "FALLO de compilación; últimas líneas:" >&2; tail -30 $CK/main.log >&2; exit 1; }
PAGS=$(pdfinfo $CK/main.pdf 2>/dev/null | awk '/^Pages/{print $2}')
UNDEF=$(grep -c "undefined" $CK/main.log || true)
OVER=$(grep -c "^Overfull" $CK/main.log || true)
QQ=$(pdftotext $CK/main.pdf - 2>/dev/null | grep -c "??" || true)
SYN=$(pdftotext $CK/main.pdf - 2>/dev/null | grep -ci "synthetic" || true)
echo "compila: OK · $PAGS páginas · PDF $(du -h $CK/main.pdf | cut -f1) · avisos 'undefined' $UNDEF · overfull $OVER · '??' $QQ · 'synthetic' $SYN"
cp $CK/main.pdf $OUT/prueba-compilacion.pdf
