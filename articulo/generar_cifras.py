"""Genera articulo/cifras.tex desde salidas_diseno/claims_diseno.jsonl (conteos de diseño, analisis/claims_diseno.py) y
salidas/claims.jsonl (resultados, analisis/indice.py), en ese orden; la última escritura de cada id gana. Adaptado del paper del sismo.
En el texto: \\cifra{id} imprime el valor formateado; \\cifraopc{id} imprime -- si falta; \\cifraabs{id} el valor absoluto;
\\pval{id} imprime «p = …». Un id inexistente imprime ??id en negrita y qa/texto.py lo detecta.
Formato por sufijo (último segmento del id): .pct, .l2/.l3/.share/.lo/.hi y titular.*/pais.*/gg.* → 1 decimal; .p/.p1/.p2 → 3 decimales
(0 → «<0.001»); .r/.rho/.kappa/.alpha/.r2/.b/.brecha → 2; conteos (n.*, cobertura.*, enteros) → miles con coma; resto → 2 decimales.
Si algún claim es sintético define \\sinteticotrue (main.tex pone la marca de agua)."""
import re, json, pathlib, math
R = pathlib.Path(__file__).resolve().parents[1]
CL = {}
DISENO = R / "salidas_diseno/claims_diseno.jsonl"
if not DISENO.exists(): print("aviso: falta salidas_diseno/claims_diseno.jsonl (correr analisis/claims_diseno.py); los \\cifra{diseno.*} saldrán como ??")
for ruta in (DISENO, R / "salidas/claims.jsonl"):
    if not ruta.exists(): continue
    for l in open(ruta):
        if l.strip(): d = json.loads(l); CL[d["id"]] = d
SINT = any(d.get("sintetico") for d in CL.values())
UNO = ("pct", "l2", "l3", "share", "lo", "hi", "minutos", "millones")


def fmt(i, v, absoluto=False):
    if isinstance(v, str): return v
    if isinstance(v, bool): v = int(v)
    if absoluto: v = abs(v)
    partes = i.split("."); u = partes[-1]
    if u == "p" or re.fullmatch(r"p\d?", u) or u.endswith("_p"):
        s = "$<$0.001" if v < 0.001 else f"{v:.3f}"; return s
    if partes[0] in ("n", "cobertura") and float(v).is_integer() or (isinstance(v, int) and u not in UNO): s = f"{int(v):,}"
    elif u in UNO or partes[0] in ("titular", "pais", "gg", "tareas") or u.endswith("pct") or "empleo" in u: s = f"{v:,.1f}"
    elif u in ("r", "rho", "kappa", "alpha", "r2", "se", "b1", "b2") or partes[0] in ("h3", "agree", "h2") or u.startswith(("r_", "kappa")): s = f"{v:.2f}"
    else: s = f"{v:.2f}"
    return s.replace("-", "$-$") if not absoluto else s


lineas = ["% generado por articulo/generar_cifras.py desde salidas_diseno/claims_diseno.jsonl y salidas/claims.jsonl — no editar a mano", r"\makeatletter",
          r"\providecommand{\cifra}{}\providecommand{\cifraopc}{}\providecommand{\cifraabs}{}\providecommand{\pval}{}",
          r"\renewcommand{\cifra}[1]{\@ifundefined{cf@#1}{\textbf{??\detokenize{#1}}}{\@nameuse{cf@#1}}}",
          r"\renewcommand{\cifraopc}[1]{\@ifundefined{cf@#1}{--}{\@nameuse{cf@#1}}}",
          r"\renewcommand{\cifraabs}[1]{\@ifundefined{cfa@#1}{\textbf{??\detokenize{#1}}}{\@nameuse{cfa@#1}}}",
          r"\renewcommand{\pval}[1]{\@ifundefined{cfp@#1}{\textbf{??\detokenize{#1}}}{\@nameuse{cfp@#1}}}"]
for i, d in sorted(CL.items()):
    v = d["valor"]
    if isinstance(v, float) and not math.isfinite(v): v = "--"
    lineas.append(r"\@namedef{cf@" + i + "}{" + fmt(i, v) + "}")
    if not isinstance(v, str): lineas.append(r"\@namedef{cfa@" + i + "}{" + fmt(i, v, True) + "}")
    u = i.split(".")[-1]
    if not isinstance(v, str) and (u == "p" or re.fullmatch(r"p\d?", u)):
        lineas.append(r"\@namedef{cfp@" + i + "}{" + ("$p<0.001$" if v < 0.001 else f"$p={v:.3f}$") + "}")
lineas.append(r"\makeatother")
lineas.append(r"\newif\ifsintetico" + ("\n\\sinteticotrue" if SINT else "\n\\sinteticofalse"))
(R / "articulo/cifras.tex").write_text("\n".join(lineas) + "\n")
print(f"{len(CL)} cifras → articulo/cifras.tex{' (SINTÉTICAS)' if SINT else ''}")
