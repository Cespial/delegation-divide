"""Paso 10: insumos del atlas por país. ILOSTAT empleo por ISCO-08 a 1 y 2 dígitos (último año ≥ 2019), informalidad, salario,
sexo×edad; Banco Mundial ingreso y PIB pc PPA. Salida: datos/atlas/paises.parquet (largo: iso3, anio, resolucion, grupo, empleo)
+ datos/atlas/paises_meta.csv + datos/atlas/COBERTURA.md (Tabla 2)."""
import sys; sys.path.insert(0, "noche")
from comun import *
import pandas as pd, numpy as np
lg = log("10_atlas"); I = DATOS / "ilostat"; W = DATOS / "worldbank"; A = DATOS / "atlas"; A.mkdir(exist_ok=True)
ANIO_MIN = 2019

def ultimo(df, col_ocu, patron):
    d = df[(df.SEX == "SEX_T") & df[col_ocu].astype(str).str.match(patron)].copy()
    d["grupo"] = d[col_ocu].str.split("_").str[-1]
    d = d[d.grupo != "X"]  # «no clasificado»
    anio = d.groupby("REF_AREA").TIME_PERIOD.max(); anio = anio[anio >= ANIO_MIN]
    d = d[d.TIME_PERIOD.eq(d.REF_AREA.map(anio))]
    return d[["REF_AREA", "TIME_PERIOD", "grupo", "OBS_VALUE"]].rename(columns={"REF_AREA": "iso3", "TIME_PERIOD": "anio", "OBS_VALUE": "empleo"})

e1 = ultimo(pd.read_csv(I / "emp_isco_todos.csv"), "OCU", r"OCU_ISCO08_[0-9X]$")
e2 = ultimo(pd.read_csv(I / "emp2_isco_todos.csv"), "OC2", r"OC2_ISCO08_[0-9X]{2}$") if (I / "emp2_isco_todos.csv").exists() else e1.iloc[0:0]
e1["resolucion"] = 1; e2["resolucion"] = 2
# Preferir 2 díg. donde el total cuadra con el de 1 díg. (±5 %) y hay ≥ 30 subgrupos
t1 = e1.groupby("iso3").empleo.sum(); t2 = e2.groupby("iso3").empleo.sum(); n2 = e2.groupby("iso3").grupo.nunique()
ok2 = [c for c in t2.index if c in t1.index and abs(t2[c] / t1[c] - 1) < 0.05 and n2[c] >= 30] + [c for c in t2.index if c not in t1.index and n2[c] >= 30]
largo = pd.concat([e2[e2.iso3.isin(ok2)], e1[~e1.iso3.isin(ok2)]], ignore_index=True)
largo = largo[~largo.grupo.str.startswith("0")]  # militares fuera
largo["empleo"] = largo.empleo * 1000  # ILOSTAT en miles
# Metadatos: ingreso, PIB pc, población, informalidad agregada, resolución
wb = pd.read_csv(W / "paises_ingreso.csv")
pib = pd.read_csv(W / "pib_pc_ppp.csv").dropna().sort_values("anio").drop_duplicates("iso3", keep="last").rename(columns={"valor": "pib_pc_ppp", "anio": "anio_pib"})
pob = pd.read_csv(W / "poblacion.csv").dropna().sort_values("anio").drop_duplicates("iso3", keep="last").rename(columns={"valor": "poblacion"})[["iso3", "poblacion"]]
meta = largo.groupby("iso3").agg(anio=("anio", "max"), resolucion=("resolucion", "max"), n_grupos=("grupo", "nunique"), empleo_total=("empleo", "sum")).reset_index()
meta = meta.merge(wb[["iso3", "pais", "region", "ingreso", "ingreso_id"]], on="iso3", how="left").merge(pib[["iso3", "pib_pc_ppp", "anio_pib"]], on="iso3", how="left").merge(pob, on="iso3", how="left")
inf = I / "informal_tasa_isco_todos.csv"
if inf.exists():
    f = pd.read_csv(inf); f = f[(f.SEX == "SEX_T") & (f.OCU == "OCU_ISCO08_TOTAL")].sort_values("TIME_PERIOD").drop_duplicates("REF_AREA", keep="last")
    meta = meta.merge(f[["REF_AREA", "OBS_VALUE"]].rename(columns={"REF_AREA": "iso3", "OBS_VALUE": "informalidad_pct"}), on="iso3", how="left")
largo.to_parquet(A / "paises.parquet", index=False); meta.to_csv(A / "paises_meta.csv", index=False)
registrar(A / "paises.parquet", "derivado: atlas_insumos.py", nota=f"{meta.iso3.nunique()} países"); registrar(A / "paises_meta.csv", "derivado: atlas_insumos.py")
# Tabla 2
L = ["# Cobertura del atlas (Tabla 2)", "", f"Países con empleo por ISCO-08 y dato ≥ {ANIO_MIN}: **{len(meta)}** · a 2 dígitos: **{(meta.resolucion == 2).sum()}** · a 1 dígito: **{(meta.resolucion == 1).sum()}**", "",
     "| Grupo de ingreso | Países | 2 díg. | Año mediano | Empleo (M) | Sin PIB pc |", "|---|---|---|---|---|---|"]
for g, d in meta.groupby(meta.ingreso.fillna("Sin clasificar")):
    L.append(f"| {g} | {len(d)} | {(d.resolucion == 2).sum()} | {int(d.anio.median())} | {d.empleo_total.sum() / 1e6:,.0f} | {d.pib_pc_ppp.isna().sum()} |")
L += ["", f"Total empleo cubierto: {meta.empleo_total.sum() / 1e6:,.0f} M personas.", "", "## Países excluidos (último dato < 2019 o sin ocupación)", ""]
todos = set(wb.iso3); L.append(", ".join(sorted(todos - set(meta.iso3))))
(A / "COBERTURA.md").write_text("\n".join(L)); lg.info("\n".join(L[:12]))
