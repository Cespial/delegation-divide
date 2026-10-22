"""Verifica el sitio contra la fuente de verdad, sin pasar por exportar.py:
1) cada cifra de datos/resumen.json es fmt_html(valor) leído ahora de los claims (sin HTML);
2) ocupaciones, grandes grupos, países y Colombia (GEIH) en datos/*.json coinciden con salidas/ y salidas_microdatos/;
3) el sitio construido (.next) tiene la portada del lab, el about y una página por ruta del ADI (/adi/…), sin «NaN», «undefined» ni «null%», y cada ficha muestra su ADI;
4) los archivos públicos (/data, /adi) son copias exactas de release/v2026.1.
Uso (desde la raíz, después de `npm run build` en sitio/): .venv/bin/python -I sitio/datos/verificar.py"""
import re, sys, json, filecmp, pathlib, html as H
R = pathlib.Path(__file__).resolve().parents[2]; S = R / "sitio"; D = S / "datos"
sys.path[:0] = [str(R / "analisis"), str(R / "informe")]
import pandas as pd
from formato_cifras import CL, fmt_html, pval_html

malas = []
def igual(etq, a, b, tol=0.051):
    if a is None or b is None or (isinstance(a, float) and pd.isna(a)):
        if not (a is None or (isinstance(a, float) and pd.isna(a))) or b is not None: malas.append((etq, a, b))
    elif abs(float(a) - float(b)) > tol: malas.append((etq, a, b))

# 1) cifras
sin_html = lambda s: H.unescape(re.sub(r"<[^>]+>", "", s))
r = json.loads((D / "resumen.json").read_text())
m1 = [(k, t) for k, t in r["cifras"].items() if t not in {sin_html(fmt_html(k, CL[k]["valor"]))} | ({sin_html(fmt_html(k, CL[k]["valor"], True)), sin_html(pval_html(CL[k]["valor"]))} if not isinstance(CL[k]["valor"], str) else set())]
print(f"1) {len(r['cifras'])} cifras del sitio; {len(m1)} distintas de los claims" + (f": {m1[:5]}" if m1 else ""))

# 2) registros
n0 = len(malas)
o = pd.read_csv(R / "salidas/indice_isco_detalle.csv", dtype={"isco08": str}).set_index("isco08")
oc = {x["isco"]: x for x in json.loads((D / "ocupaciones.json").read_text())["filas"]}
assert set(oc) == set(o.index), "ocupaciones distintas"
for k, x in oc.items():
    f = o.loc[k]
    for a, b in ((x["l2"], 100 * f.adi_l2), (x["l2_lo"], 100 * f.l2_lo), (x["l2_hi"], 100 * f.l2_hi), (x["l3"], 100 * f.adi_l3), (x["s"], f.adi_share)): igual(f"isco {k}", a, b)
    for a, c in zip(x["b"], ("barrera_fisica", "barrera_responsabilidad", "barrera_confianza", "barrera_acceso")): igual(f"isco {k} {c}", a, 100 * f[c])
    igual(f"isco {k} rk", x["rk"], int((o.adi_l2 > f.adi_l2).sum()) + 1, 0)
    if x["n"] != int(f.n_tareas): malas.append((f"isco {k} n", x["n"], f.n_tareas))
    t = json.loads((D / "tareas" / f"{k}.json").read_text())
    igual(f"isco {k} suma de pesos", sum(z["w"] for z in t), 100, 0.6)
    igual(f"isco {k} ADI desde tareas", sum(z["w"] for z in t if z["n"] >= 2), x["l2"], 0.6)
g = pd.read_csv(R / "salidas/indice_gg.csv", dtype={"gg": str}).set_index("gg")
for x in json.loads((D / "grupos.json").read_text()):
    igual(f"gg {x['gg']}", x["l2"], 100 * g.loc[x["gg"]].adi_l2); igual(f"gg {x['gg']} claim", x["l2"], CL[f"gg.{x['gg']}.l2"]["valor"])
p = pd.read_csv(R / "salidas/indice_pais_detalle.csv").set_index("iso3")
pa = json.loads((D / "paises.json").read_text())
assert {x["iso3"] for x in pa} == set(p.index), "países distintos"
import perfil as PF
for x in pa:
    f = p.loc[x["iso3"]]
    for a, b in ((x["l2"], 100 * f.adi_l2), (x["lo"], 100 * f.l2_lo), (x["hi"], 100 * f.l2_hi), (x["l3"], 100 * f.adi_l3), (x["s"], f.adi_share), (x["l2_iguales"], 100 * f.adi_l2_iguales)): igual(f"país {x['iso3']}", a, b)
    if x["perfil"]["hallazgo"] != PF.calcular(x["iso3"])["hallazgo"]: malas.append((f"país {x['iso3']} perfil", x["perfil"]["hallazgo"][:40], "recalculado distinto"))
gc = pd.read_csv(R / "salidas_microdatos/gradientes_col.csv")
co = {(x["grupo"], x["cat"]): x for x in json.loads((D / "colombia.json").read_text())}
for f in gc.itertuples():
    x = co[(f.grupo, f.categoria)]; igual(f"GEIH {f.grupo}/{f.categoria}", x["l2"], f.adi_l2); igual(f"GEIH {f.grupo}/{f.categoria} lo", x["lo"], f.l2_lo)
print(f"2) {len(oc)} ocupaciones (con sus tareas), {len(g)} grupos, {len(pa)} países, {len(co)} grupos GEIH; {len(malas) - n0} diferencias" + (f": {malas[n0:n0 + 5]}" if len(malas) > n0 else ""))

# 3) sitio construido
A = S / ".next/server/app"
if not A.exists(): print("3) falta el build: corra `npm run build` en sitio/"); sys.exit(1)
n1 = len(malas)
rutas = ["index", "about", "adi"] + [f"adi/{r}" for r in ("occupations", "countries", "compare", "methodology", "report", "data")] + [f"adi/occupations/{k}" for k in oc] + [f"adi/countries/{x['iso3']}" for x in pa]
for ru in rutas:
    h = A / f"{ru}.html"
    if not h.exists(): malas.append((ru, "sin HTML", "")); continue
    txt = H.unescape(re.sub(r"<script.*?</script>|<[^>]+>", " ", h.read_text(), flags=re.S))
    for mal in ("NaN", "undefined", "null%", "Infinity"):
        if re.search(rf"\b{mal}\b", txt): malas.append((ru, f"contiene {mal}", ""))
    if ru.startswith("adi/occupations/"): x = oc[ru.split("/")[2]]
    elif ru.startswith("adi/countries/"): x = next(y for y in pa if y["iso3"] == ru.split("/")[2])
    else: continue
    if f"{x['l2']:.1f}" not in txt: malas.append((ru, "no muestra su ADI", x["l2"]))
# titulares: la portada del ADI los muestra todos; la del lab, los tres que cita
for pag, ids in (("adi", ("titular.global.l2", "titular.global.l3", "titular.ingreso.bajo.l2", "titular.ingreso.alto.l2", "h1.pendiente", "agree.kappa.humano.modelo")),
                 ("index", ("titular.global.l2", "titular.global.l3", "titular.ingreso.bajo.l2", "titular.ingreso.alto.l2", "h4.pico.minutos"))):
    txt = H.unescape(re.sub(r"<[^>]+>", " ", (A / f"{pag}.html").read_text()))
    faltan = [k for k in ids if r["cifras"][k] not in txt]
    if faltan: malas.append((pag, "faltan titulares", faltan))
print(f"3) {len(rutas)} páginas revisadas; {len(malas) - n1} problemas" + (f": {malas[n1:n1 + 5]}" if len(malas) > n1 else ""))

# 4) archivos públicos
n2 = len(malas)
for f in ("adi_isco.csv", "adi_pais.csv", "adi_tarea.csv", "claims.jsonl", "DATA_DICTIONARY.md", "SHA256SUMS"):
    if not filecmp.cmp(S / "public/data" / f, R / "release/v2026.1" / f, shallow=False): malas.append((f"data/{f}", "distinto de release", ""))
def comparar(c, ruta="adi/v2026.1"):
    if c.left_only or c.right_only or c.diff_files: malas.append((ruta, c.left_only[:3] + c.right_only[:3], c.diff_files[:3]))
    for k, sub in c.subdirs.items(): comparar(sub, f"{ruta}/{k}")
comparar(filecmp.dircmp(S / "public/adi/v2026.1", R / "release/v2026.1/api"))
print(f"4) archivos públicos: {len(malas) - n2} diferencias con release/v2026.1")
sys.exit(1 if m1 or malas else 0)
