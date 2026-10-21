"""Paso 14 (mejor esfuerzo): PNAD Contínua trimestral (IBGE) → panel persona de ocupados con ocupación COD a 4 díg.
La COD (Classificação de Ocupações para Pesquisas Domiciliares) sigue la ISCO-08 a 4 dígitos salvo agregaciones; se usa tal cual.
Variables (input_PNADC_trimestral.txt): V4010 ocupación, V2007 sexo (1 H, 2 M), V2009 edad, VD4002 ocupado (1), VD4012 contribuye
a previsión (1 sí; informal = 2), VD4016 ingreso habitual, V4039 horas, V1028 factor. Sin ZIP completo (sufijo .parcial) sale con aviso.
Salida: datos/microdatos/pnadc_panel.parquet + pnadc_isco_resumen.csv."""
import sys, zipfile, io, re; sys.path.insert(0, "noche")
from comun import *
import pandas as pd, numpy as np
lg = log("14_pnadc"); D = DATOS / "microdatos/pnadc"
zips = sorted(z for z in D.glob("PNADC_*.zip"))
if not zips:
    lg.warning(f"PNADC: sin ZIP completo en {D} (parciales: {[p.name for p in D.glob('*.parcial')]}); se omite"); sys.exit(0)
dic = D / "Dicionario_e_input.zip"
if not dic.exists(): lg.warning("PNADC: falta Dicionario_e_input.zip (layout); se omite"); sys.exit(0)
txt = zipfile.ZipFile(dic).read("input_PNADC_trimestral.txt").decode("latin-1")
lay = {m.group(2): (int(m.group(1)) - 1, int(m.group(3) or m.group(4))) for m in re.finditer(r"@(\d+)\s+(\w+)\s+\$?(?:(\d+)\.|(\d+)\.\d*)", txt)}
VARS = ["Ano", "Trimestre", "UF", "V1028", "V2007", "V2009", "V4010", "VD4002", "VD4012", "VD4016", "V4039"]
faltan = [v for v in VARS if v not in lay]
if faltan: lg.error(f"layout sin {faltan}"); sys.exit(0)
partes = []
for z in zips:
    try:
        zf = zipfile.ZipFile(z); n = next(n for n in zf.namelist() if n.lower().endswith(".txt"))
        with zf.open(n) as f:
            d = pd.read_fwf(f, colspecs=[(lay[v][0], lay[v][0] + lay[v][1]) for v in VARS], names=VARS, dtype=str)
        d = d[d.VD4002 == "1"]; partes.append(d); lg.info(f"{z.name}: {len(d):,} ocupados")
    except Exception as e:
        lg.error(f"{z.name}: {e}")
if not partes: lg.warning("PNADC: ningún trimestre legible"); sys.exit(0)
p = pd.concat(partes, ignore_index=True)
p = pd.DataFrame({"anio": p.Ano.astype(int), "trimestre": p.Trimestre.astype(int), "uf": p.UF, "isco4": p.V4010.str.zfill(4),
                  "sexo": p.V2007.map({"1": "H", "2": "M"}), "edad": pd.to_numeric(p.V2009, errors="coerce"),
                  "informal": (p.VD4012 == "2").astype(int), "ingreso": pd.to_numeric(p.VD4016, errors="coerce"),
                  "horas": pd.to_numeric(p.V4039, errors="coerce"), "factor": pd.to_numeric(p.V1028, errors="coerce")})
p.to_parquet(DATOS / "microdatos/pnadc_panel.parquet", index=False)
registrar(DATOS / "microdatos/pnadc_panel.parquet", "derivado: microdatos_pnadc.py", nota=f"{len(p):,} personas")
w = p.dropna(subset=["factor"]); w = w[w.isco4.str.match(r"^\d{4}$")]
per = w.groupby(["anio", "trimestre"]).ngroups
r = w.groupby("isco4").apply(lambda d: pd.Series({"empleo": d.factor.sum() / per, "n_obs": len(d), "informal_pct": np.average(d.informal, weights=d.factor) * 100,
      "mujeres_pct": np.average(d.sexo == "M", weights=d.factor) * 100, "edad_media": np.average(d.edad.fillna(d.edad.median()), weights=d.factor),
      "ingreso_mediano": d.ingreso.median()}), include_groups=False).reset_index()
r.to_csv(DATOS / "microdatos/pnadc_isco_resumen.csv", index=False); registrar(DATOS / "microdatos/pnadc_isco_resumen.csv", "derivado: microdatos_pnadc.py", nota=f"{len(r)} ocupaciones")
lg.info(f"PNADC: {len(r)} ocupaciones COD; empleo medio {r.empleo.sum() / 1e6:.1f} M; informalidad {np.average(r.informal_pct, weights=r.empleo):.1f} %")
