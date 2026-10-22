"""Datos del sitio web del ADI: convierte las salidas publicadas del índice en JSON que Next.js lee al construir (nada se calcula
en el navegador salvo filtros y comparador). Fuente única: las mismas tablas y claims del paper y del informe.
Escribe en sitio/datos/: resumen.json (cifras por id, como el informe), ocupaciones.json, grupos.json, paises.json (con el perfil de
informe/perfil.calcular para cada país), mapa.json (trazos SVG en proyección Equal Earth), colombia.json (desgloses GEIH), h4.json,
tareas/<isco>.json (tareas de cada ocupación con su nivel por modelo); copia la API estática a sitio/public/adi/v2026.1/, las tablas
pequeñas a sitio/public/data/, llms*.txt y el PDF limpio del informe si existe. Uso (desde la raíz): .venv/bin/python -I sitio/datos/exportar.py"""
import json, subprocess, re, sys, shutil, pathlib
import numpy as np, pandas as pd

R = pathlib.Path(__file__).resolve().parents[2]; OUT = R / "sitio/datos"; PUB = R / "sitio/public"
sys.path.insert(0, str(R / "informe")); import perfil as PF  # noqa: E402
(OUT / "tareas").mkdir(parents=True, exist_ok=True)
escribir = lambda nombre, obj: (OUT / nombre).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
r1 = lambda x, n=1: None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), n)
GG = {"1": "Managers", "2": "Professionals", "3": "Technicians and associate professionals", "4": "Clerical support workers",
      "5": "Service and sales workers", "6": "Skilled agricultural, forestry and fishery workers", "7": "Craft and related trades workers",
      "8": "Plant and machine operators and assemblers", "9": "Elementary occupations"}
INGRESO = {"high": "High income", "upper-middle": "Upper-middle income", "lower-middle": "Lower-middle income", "low": "Low income"}

# --- cifras: las mismas del informe (txt formateado, sin HTML), por id
C = json.loads((R / "informe/cifras.json").read_text())["cifras"]
cifras = {k: re.sub(r"<[^>]+>", "", e["txt"]) for k, e in C.items()}
est = R / "release/zenodo_informe.estado.json"
doi_informe = json.loads(est.read_text())["doi"] if est.exists() and not json.loads(est.read_text()).get("sandbox") else None
escribir("resumen.json", {"cifras": cifras, "version": "2026.1", "fecha": "2026-10-22", "doi_datos": "10.5281/zenodo.23552918",
                          "doi_datos_concepto": "10.5281/zenodo.23552917", "doi_prerregistro": "10.17605/OSF.IO/9ZNTF", "doi_informe": doi_informe})

# --- ocupaciones (433) con puestos, intervalos, barreras y comparadores en percentil
o = pd.read_csv(R / "salidas/indice_isco_detalle.csv", dtype={"isco08": str})
o["rank_l2"] = o.adi_l2.rank(ascending=False, method="min").astype(int); o["rank_l3"] = o.adi_l3.rank(ascending=False, method="min").astype(int)
o["rank_share"] = o.adi_share.rank(ascending=False, method="min").astype(int)
COMP = [("eloundou_beta", "Eloundou et al. (2024), GPT exposure β"), ("felten_aioe", "Felten et al. (2021), AI occupational exposure"),
        ("webb_pct_ai", "Webb (2020), AI patent exposure"), ("eisfeldt_genaiexp", "Eisfeldt et al. (2026), generative AI exposure"),
        ("aei_exposicion_obs", "Anthropic Economic Index, observed use")]
pct = {c: o[c].rank(pct=True) for c, _ in COMP}
ocup = []
for i, f in o.iterrows():
    ocup.append(dict(isco=f.isco08, titulo=f.titulo, gg=f.isco08[0], sub=f.isco08[:2], l2=r1(100 * f.adi_l2), l2_lo=r1(100 * f.l2_lo), l2_hi=r1(100 * f.l2_hi),
                     l3=r1(100 * f.adi_l3), l3_lo=r1(100 * f.l3_lo), l3_hi=r1(100 * f.l3_hi), s=r1(f.adi_share), s_lo=r1(f.ic_lo), s_hi=r1(f.ic_hi),
                     n=int(f.n_tareas), imp=bool(f.imputado), emp=r1(f.empleo_mundial / 1e6, 2),
                     b=[r1(100 * f[c]) for c in ("barrera_fisica", "barrera_responsabilidad", "barrera_confianza", "barrera_acceso")],
                     rk=int(f.rank_l2), rk3=int(f.rank_l3), rks=int(f.rank_share),
                     comp={c: (None if pd.isna(f[c]) else {"v": r1(f[c], 3), "p": int(round(100 * pct[c][i]))}) for c, _ in COMP}))
escribir("ocupaciones.json", {"comparadores": dict(COMP), "grupos": GG, "filas": ocup})

# --- grandes grupos (9)
g = pd.read_csv(R / "salidas/indice_gg.csv", dtype={"gg": str})
escribir("grupos.json", [dict(gg=f.gg, nombre=GG[f.gg], l2=r1(100 * f.adi_l2), lo=r1(100 * f.lo), hi=r1(100 * f.hi), l3=r1(100 * f.adi_l3, 2), s=r1(f.adi_share),
                              b=[r1(100 * f[c]) for c in ("barrera_fisica", "barrera_responsabilidad", "barrera_confianza", "barrera_acceso")],
                              emp=r1(f.empleo_mundial / 1e6), n=int(f.n_isco)) for _, f in g.iterrows()])

# --- tareas por ocupación: texto, peso en la ocupación, nivel de consenso y por modelo, minutos, barreras
t = pd.read_csv(R / "salidas/adi_tarea.csv").set_index("task_id")
p = pd.read_parquet(R / "datos/pares_isco_tarea.parquet").rename(columns={"Task ID": "task_id"})
p = p[p.task_id.isin(t.index[t.n_modelos.fillna(0) > 0])]
n_tareas = 0
for isco, d in p.groupby("isco08"):
    d = d.assign(w=d.peso / d.peso.sum()).sort_values("w", ascending=False); filas = []
    for f in d.itertuples():
        x = t.loc[f.task_id]
        filas.append(dict(id=int(f.task_id), t=f.texto, o=x.titulo, w=r1(100 * f.w, 2), n=int(x.nivel), s=r1(x.share, 0), m=r1(x.minutos, 0),
                          h=None if pd.isna(x.nivel_haiku) else int(x.nivel_haiku), so=None if pd.isna(x.nivel_sonnet) else int(x.nivel_sonnet),
                          b=[r1(x[c], 1) for c in ("barrera_fisica", "barrera_responsabilidad", "barrera_confianza", "barrera_acceso")], core=f.tipo == "Core"))
    (OUT / f"tareas/{isco}.json").write_text(json.dumps(filas, ensure_ascii=False, separators=(",", ":"))); n_tareas += len(filas)

# --- países (146) con el perfil del informe para cada uno
d = pd.read_csv(R / "salidas/indice_pais_detalle.csv"); d["region"] = d.region.str.strip()
d["rank_l2"] = d.adi_l2.rank(ascending=False, method="min").astype(int)
paises = []
for f in d.itertuples():
    pf = PF.calcular(f.iso3)
    paises.append(dict(iso3=f.iso3, nombre=pf["nombre"], region=f.region, region_nombre=pf["region_nombre"], ingreso=f.ingreso, ingreso_nombre=INGRESO.get(f.ingreso, f.ingreso),
                       anio=int(f.anio), res=int(f.resolucion), l2=r1(100 * f.adi_l2), lo=r1(100 * f.l2_lo), hi=r1(100 * f.l2_hi), l3=r1(100 * f.adi_l3, 2),
                       s=r1(f.adi_share), l2_iguales=r1(100 * f.adi_l2_iguales), emp=r1(f.empleo_total / 1e6, 2), pib=r1(f.pib_pc_ppp, 0),
                       inf=r1(f.informalidad_pct), uso=r1(f.usage_per_capita_index, 2), rk=int(f.rank_l2),
                       perfil=dict(hallazgo=pf["hallazgo"], hallazgo_fig=pf["hallazgo_fig"], n_region=pf["n_region"], region_l2=pf["region_l2"], mundo_l2=pf["mundo_l2"],
                                   filas=[dict(tema=tema, **{k: v for k, v in fl.items() if k != "v"}) for tema, fs in pf["grupos"] for fl in fs],
                                   barras=[[b[0], b[1], r1(b[2])] for b in pf["barras"]])))
escribir("paises.json", paises)

# --- mapa: Natural Earth 1:110m en Equal Earth, trazos simplificados por ISO3
import geopandas as gpd  # noqa: E402
m = gpd.read_file(R / "datos/geo/ne_110m_admin_0_countries.shp")
m["iso3"] = np.where(m.ISO_A3.str.match(r"^[A-Z]{3}$") & (m.ISO_A3 != "-99"), m.ISO_A3, m.ADM0_A3)
m = m[m.iso3 != "ATA"].to_crs("+proj=eqearth +datum=WGS84"); m["geometry"] = m.geometry.simplify(9000)
x0, y0, x1, y1 = m.total_bounds; ESC = 1000 / (x1 - x0); H = (y1 - y0) * ESC
def trazo(geom):
    polis = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    out = []
    for pg in polis:
        for anillo in [pg.exterior, *pg.interiors]:
            pts = [(round((x - x0) * ESC, 1), round((y1 - y) * ESC, 1)) for x, y in anillo.coords]
            out.append("M" + "L".join(f"{a},{b}" for a, b in pts) + "Z")
    return "".join(out)
# estados pequeños que la escala 1:110m no dibuja: un punto en la capital (lat, lon aproximadas)
PEQ = {"BRB": (13.1, -59.6), "CPV": (14.9, -23.5), "CUW": (12.1, -68.9), "GRD": (12.1, -61.7), "KIR": (1.3, 173.0), "LCA": (13.9, -61.0),
       "MDV": (4.2, 73.5), "MHL": (7.1, 171.4), "MLT": (35.9, 14.5), "MUS": (-20.2, 57.5), "NRU": (-0.5, 166.9), "PLW": (7.5, 134.6),
       "SGP": (1.35, 103.8), "SYC": (-4.6, 55.5), "TON": (-21.1, -175.2), "TUV": (-8.5, 179.2), "WSM": (-13.8, -171.8)}
from pyproj import Transformer  # noqa: E402
tr = Transformer.from_crs("EPSG:4326", "+proj=eqearth +datum=WGS84", always_xy=True)
puntos = []
for iso, (la, lo) in PEQ.items():
    x, y = tr.transform(lo, la); puntos.append(dict(iso3=iso, x=round((x - x0) * ESC, 1), y=round((y1 - y) * ESC, 1)))
escribir("mapa.json", {"ancho": 1000, "alto": round(H, 1), "paises": [dict(iso3=f.iso3, nombre=f.NAME, d=trazo(f.geometry)) for f in m.itertuples() if f.geometry is not None],
                       "puntos": puntos})
fuera = sorted(set(d.iso3) - set(m.iso3) - set(PEQ))

# --- Colombia por sexo, edad y formalidad (GEIH, exploratorio)
gc = pd.read_csv(R / "salidas_microdatos/gradientes_col.csv")
escribir("colombia.json", [dict(grupo=f.grupo, cat=f.categoria, l2=r1(f.adi_l2), lo=r1(f.l2_lo), hi=r1(f.l2_hi), l3=r1(f.adi_l3, 2), emp=r1(f.empleo_pct)) for f in gc.itertuples()])

# --- H4: curva logit preregistrada y proporciones observadas por veintiles de duración (como la Figura 4.3)
k = json.loads((R / "salidas/regresiones.json").read_text())["h4"]["coef"]
tt = t[(t.n_modelos.fillna(0) > 0) & t.minutos.notna()]; lm = np.log(np.clip(tt.minutos, 1, 4800)); y = (tt.nivel == 3).astype(float)
q = pd.qcut(lm, 20, duplicates="drop"); bins = pd.DataFrame({"lm": lm, "y": y}).groupby(q, observed=True).agg(lm=("lm", "median"), y=("y", "mean"))
xx = np.linspace(0, np.log(4800), 120); curva = 100 / (1 + np.exp(-(k["const"] + k["lmin"] * xx + k["lmin2"] * xx ** 2)))
escribir("h4.json", {"curva": [[r1(a, 3), r1(b, 2)] for a, b in zip(xx, curva)], "puntos": [[r1(a, 3), r1(100 * b, 2)] for a, b in zip(bins.lm, bins.y)],
                     "pico_lmin": r1(-k["lmin"] / (2 * k["lmin2"]), 3)})

# --- archivos públicos: API estática, tablas pequeñas, llms.txt, informe
api = PUB / "adi/v2026.1"
if api.exists(): shutil.rmtree(api)
shutil.copytree(R / "release/v2026.1/api", api)
(PUB / "data").mkdir(parents=True, exist_ok=True)
for f in ("adi_isco.csv", "adi_isco.parquet", "adi_pais.csv", "adi_pais.parquet", "adi_tarea.csv", "adi_tarea.parquet", "claims.jsonl", "DATA_DICTIONARY.md", "SHA256SUMS"): shutil.copy2(R / "release/v2026.1" / f, PUB / "data" / f)
pdf = R / "informe/out/limpio/delegation-divide-report-2026.pdf"
(PUB / "report").mkdir(exist_ok=True)
if pdf.exists(): shutil.copy2(pdf, PUB / "report" / pdf.name)
# portada del informe (página 1 rasterizada, sin metadatos): /report y su imagen OG
fuente = pdf if pdf.exists() else R / "informe/out/delegation-divide-report-2026.pdf"
if fuente.exists():
    base = OUT / "portada"
    subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-singlefile", "-scale-to-x", "900", "-scale-to-y", "-1", "-png", str(fuente), str(base)], check=True)
    subprocess.run(["cwebp", "-quiet", "-q", "82", "-metadata", "none", f"{base}.png", "-o", str(PUB / "report" / "cover.webp")], check=True)
    pathlib.Path(f"{base}.png").unlink()
    subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-singlefile", "-scale-to-x", "440", "-scale-to-y", "-1", "-jpeg", "-jpegopt", "quality=86",
                    str(fuente), str(OUT / "portada-og")], check=True)
paginas = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(fuente)], capture_output=True, text=True).stdout).group(1)) if fuente.exists() else None
escribir("informe.json", {"paginas": paginas, "pdf": pdf.exists(), "mb": round(pdf.stat().st_size / 1e6, 1) if pdf.exists() else None})
# llms-full.txt del repositorio: el sitio lo sirve reescribiendo la URL de Pages por la suya (app/llms-full.txt/route.ts)
shutil.copy2(R / "llms-full.txt", OUT / "llms-full.txt")
print(f"sitio/datos: {len(ocup)} ocupaciones, {len(paises)} países, {n_tareas:,} pares tarea-ocupación en {len(list((OUT / 'tareas').glob('*.json')))} archivos; "
      f"países del atlas sin trazo en el mapa: {fuera or 'ninguno'}; informe PDF {'copiado' if pdf.exists() else 'pendiente (falta la copia limpia)'}")
