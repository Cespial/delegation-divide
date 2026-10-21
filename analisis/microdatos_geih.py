"""Paso 13: GEIH 2024-01 → 2026-08 (DANE) → panel persona-mes de ocupados con CIUO-08 A.C. a 4 dígitos.
Variables: OFICIO_C8 (CIUO-08 A.C.), P6430 (posición ocupacional), P6920 (cotiza a pensión: 1 sí; informal = ≠1), INGLABO,
FEX_C18 (factor), DPTO, AREA, CLASE (1 cabecera); de «Características generales»: P3271 (sexo: 1 hombre, 2 mujer), P6040 (edad).
Salida: datos/microdatos/geih_panel.parquet + geih_ciuo_resumen.csv (empleo ponderado, informalidad y mediana de ingreso por CIUO)."""
import sys, zipfile, io, re; sys.path.insert(0, "noche")
from comun import *
import pandas as pd, numpy as np
lg = log("13_geih"); G = DATOS / "microdatos/geih"; MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12}

def leer(zf, nombre_sub, cols):
    n = next((n for n in zf.namelist() if ("CSV" in n.split("/")[:-1] or "/" not in n or n.count("/") == 1) and n.lower().endswith(".csv") and n.lower().split("/")[-1].startswith(nombre_sub)), None)
    if not n: raise FileNotFoundError(nombre_sub)
    raw = zf.read(n)
    for enc in ("latin-1", "utf-8"):
        try:
            head = raw[:5000].decode(enc); sep = ";" if head.count(";") > head.count(",") else ","
            d = pd.read_csv(io.BytesIO(raw), sep=sep, encoding=enc, usecols=lambda c: c.upper() in cols, dtype=str, low_memory=False)
            d.columns = [c.upper() for c in d.columns]; return d
        except UnicodeDecodeError: continue

partes = []
for z in sorted(G.glob("*.zip")):
    m = re.search(r"(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\w*[_ ]+(\d{4})", z.name.lower()); anio, mes = int(m.group(2)), MESES[m.group(1)]
    try:
        zf0 = zipfile.ZipFile(z); dentro = [n for n in zf0.namelist() if n.lower().endswith("csv.zip")]
        with (zipfile.ZipFile(io.BytesIO(zf0.read(dentro[0]))) if dentro and not any(n.lower().endswith(".csv") for n in zf0.namelist()) else zf0) as zf:
            o = leer(zf, "ocupados", {"DIRECTORIO", "SECUENCIA_P", "ORDEN", "OFICIO_C8", "P6430", "P6920", "INGLABO", "FEX_C18", "DPTO", "AREA", "CLASE", "P6800"})
            try: c = leer(zf, "caracter", {"DIRECTORIO", "SECUENCIA_P", "ORDEN", "P3271", "P6040"})
            except FileNotFoundError: c = leer(zf, "cap", {"DIRECTORIO", "SECUENCIA_P", "ORDEN", "P3271", "P6040"})
        d = o.merge(c, on=["DIRECTORIO", "SECUENCIA_P", "ORDEN"], how="left"); d["anio"], d["mes"] = anio, mes
        partes.append(d); lg.info(f"{z.name}: {len(o):,} ocupados, sexo/edad {d.P3271.notna().mean():.0%}")
    except Exception as e:
        lg.error(f"{z.name}: {e}")
p = pd.concat(partes, ignore_index=True)
for c in ("INGLABO", "P6800", "P6920", "P6430", "OFICIO_C8", "P3271", "P6040", "DPTO", "AREA", "CLASE"):
    if c not in p: p[c] = pd.NA; lg.warning(f"columna {c} ausente en todos los meses")
lg.info("cobertura por columna: " + ", ".join(f"{c} {p[c].notna().mean():.0%}" for c in ("OFICIO_C8", "INGLABO", "P6920", "P3271", "FEX_C18")))
for c in ("FEX_C18", "INGLABO", "P6040", "P6800"): p[c] = pd.to_numeric(p[c].str.replace(",", "."), errors="coerce")
p["ciuo4"] = p.OFICIO_C8.str.zfill(4); p["sexo"] = p.P3271.map({"1": "H", "2": "M"}); p["edad"] = p.P6040
p["informal"] = (p.P6920 != "1").astype(int); p["horas"] = p.P6800
p = p[["anio", "mes", "DPTO", "AREA", "CLASE", "ciuo4", "P6430", "sexo", "edad", "informal", "INGLABO", "horas", "FEX_C18"]].rename(columns={"INGLABO": "ingreso", "FEX_C18": "factor"})
p.to_parquet(DATOS / "microdatos/geih_panel.parquet", index=False); registrar(DATOS / "microdatos/geih_panel.parquet", "derivado: microdatos_geih.py", nota=f"{len(p):,} persona-mes, {p.anio.min()}-{p.anio.max()}")
w = p.dropna(subset=["factor"]); w = w[w.ciuo4.str.match(r"^\d{4}$")]
r = w.groupby("ciuo4").apply(lambda d: pd.Series({"empleo": d.factor.sum() / d.groupby(["anio", "mes"]).ngroups, "n_obs": len(d), "informal_pct": np.average(d.informal, weights=d.factor) * 100,
      "mujeres_pct": np.average(d.sexo == "M", weights=d.factor) * 100, "edad_media": np.average(d.edad.fillna(d.edad.median()), weights=d.factor),
      "ingreso_mediano": d.ingreso.median()}), include_groups=False).reset_index()
r.to_csv(DATOS / "microdatos/geih_ciuo_resumen.csv", index=False); registrar(DATOS / "microdatos/geih_ciuo_resumen.csv", "derivado: microdatos_geih.py", nota=f"{len(r)} CIUO")
lg.info(f"panel {len(p):,} filas; CIUO 4 díg. con datos: {len(r)}; empleo mensual medio {r.empleo.sum() / 1e6:.1f} M; informalidad {np.average(r.informal_pct, weights=r.empleo):.1f} %")
