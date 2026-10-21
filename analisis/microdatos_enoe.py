"""Paso 15 (mejor esfuerzo): ENOE trimestral (INEGI) → panel persona de ocupados con ocupación SINCO 2011 (COE1.p3) y gran grupo ISCO-08.
No hay crosswalk SINCO→ISCO en disco: se agrega a 1 dígito ISCO con la tabla manual SINCO_ISCO1 (aproximada; documentada abajo).
SDEM: sex (1 H, 2 M), eda, clase2 (1 ocupado), emp_ppal (1 informal, 2 formal), ingocup, hrsocup, fac_tri (o fac). Sin .parcial.
Salida: datos/microdatos/enoe_panel.parquet + enoe_isco1_resumen.csv (formato de geih_ciuo_resumen.csv) + enoe_sinco_resumen.csv."""
import sys, zipfile, re; sys.path.insert(0, "noche")
from comun import *
import pandas as pd, numpy as np
lg = log("15_enoe"); D = DATOS / "microdatos/enoe"
# SINCO 2011 (2 díg.) → ISCO-08 gran grupo. 21–24 profesionistas → 2; 25–29 auxiliares y técnicos → 3; 3 auxiliares administrativos → 4;
# 4 comerciantes/ventas y 5 servicios personales y vigilancia → 5; 6 agropecuarios → 6; 7 artesanos y construcción → 7;
# 8 operadores y conductores → 8; 9 elementales → 9; 1 funcionarios y directores → 1. Aproximación: no separa 92 (peones agrícolas).
def sinco_isco1(c):
    if not isinstance(c, str) or not re.fullmatch(r"\d{4}", c) or c.startswith("99"): return None
    if c[0] == "2": return "2" if c[1] in "1234" else "3"
    return {"1": "1", "3": "4", "4": "5", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9"}.get(c[0])
CLAVE = ["cd_a", "ent", "con", "v_sel", "n_hog", "h_mud", "n_ren"]
zips = sorted(D.glob("*.zip"))
if not zips: lg.warning(f"ENOE: sin ZIP completo en {D}"); sys.exit(0)
partes = []
for z in zips:
    m = re.search(r"(\d{4})_trim(\d)", z.name); anio, tri = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    try:
        zf = zipfile.ZipFile(z); nombres = zf.namelist()
        sd = next(n for n in nombres if re.search(r"sdem", n, re.I) and n.lower().endswith(".csv"))
        co = next(n for n in nombres if re.search(r"coe1", n, re.I) and n.lower().endswith(".csv"))
        lee = lambda n, cols: pd.read_csv(zf.open(n), usecols=lambda c: c.lower() in cols, dtype=str, encoding="latin-1", low_memory=False).rename(columns=str.lower)
        s = lee(sd, set(CLAVE) | {"r_def", "c_res", "sex", "eda", "clase2", "emp_ppal", "ingocup", "hrsocup", "fac_tri", "fac"})
        c = lee(co, set(CLAVE) | {"p3"})
        for d in (s, c):
            for k in CLAVE:
                if k in d: d[k] = d[k].str.strip()
        s = s[(s.clase2.str.strip() == "1") & s.r_def.str.strip().isin(["0", "00"]) & s.c_res.str.strip().isin(["1", "3"])]
        d = s.merge(c, on=[k for k in CLAVE if k in s and k in c], how="left"); d["anio"], d["trimestre"] = anio, tri
        partes.append(d); lg.info(f"{z.name}: {len(s):,} ocupados; con p3 {d.p3.notna().mean():.0%}")
    except Exception as e:
        lg.error(f"{z.name}: {e}")
if not partes: lg.warning("ENOE: ningún trimestre legible"); sys.exit(0)
p = pd.concat(partes, ignore_index=True)
fac = p["fac_tri"] if "fac_tri" in p else p.get("fac")
p = pd.DataFrame({"anio": p.anio, "trimestre": p.trimestre, "ent": p.ent, "sinco4": p.p3.str.strip().str.zfill(4),
                  "sexo": p.sex.str.strip().map({"1": "H", "2": "M"}), "edad": pd.to_numeric(p.eda, errors="coerce"),
                  "informal": (p.emp_ppal.str.strip() == "1").astype(int), "ingreso": pd.to_numeric(p.ingocup, errors="coerce"),
                  "horas": pd.to_numeric(p.hrsocup, errors="coerce"), "factor": pd.to_numeric(fac, errors="coerce")})
p["isco1"] = p.sinco4.map(sinco_isco1)
p.to_parquet(DATOS / "microdatos/enoe_panel.parquet", index=False)
registrar(DATOS / "microdatos/enoe_panel.parquet", "derivado: microdatos_enoe.py", nota=f"{len(p):,} persona-trimestre")
per = p.groupby(["anio", "trimestre"]).ngroups
def resumen(d): return pd.Series({"empleo": d.factor.sum() / per, "n_obs": len(d), "informal_pct": np.average(d.informal, weights=d.factor) * 100,
      "mujeres_pct": np.average(d.sexo == "M", weights=d.factor) * 100, "edad_media": np.average(d.edad.fillna(d.edad.median()), weights=d.factor),
      "ingreso_mediano": d.ingreso[d.ingreso > 0].median()})
w = p.dropna(subset=["factor"])
for col, nombre in (("isco1", "enoe_isco1_resumen.csv"), ("sinco4", "enoe_sinco_resumen.csv")):
    r = w.dropna(subset=[col]).groupby(col).apply(resumen, include_groups=False).reset_index()
    r.to_csv(DATOS / "microdatos" / nombre, index=False); registrar(DATOS / "microdatos" / nombre, "derivado: microdatos_enoe.py", nota=f"{len(r)} grupos")
    lg.info(f"ENOE {col}: {len(r)} grupos; empleo medio {r.empleo.sum() / 1e6:.1f} M; informalidad {np.average(r.informal_pct, weights=r.empleo):.1f} %")
lg.info(f"ENOE: p3 mapeado a ISCO 1 díg. {p.isco1.notna().mean():.1%} de ocupados")
