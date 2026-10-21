"""Paso 2: ILOSTAT por SDMX, país por país: empleo, empleo informal y salarios por ocupación ISCO-08.
Produce emp_isco_todos.csv y RESOLUCION.md (cuántos países tienen ISCO-08 a 1 y 2 dígitos, año más reciente)."""
import sys, io, time; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
import pandas as pd, requests
lg = log("02_ilostat"); d = DATOS / "ilostat"; d.mkdir(parents=True, exist_ok=True)
FLUJOS = {"emp": "DF_EMP_TEMP_SEX_OCU_NB", "informal": "DF_EMP_NIFL_SEX_OCU_NB", "informal_tasa": "DF_EMP_NIFL_SEX_OCU_RT",
          "salario_mes": "DF_EAR_EMTM_SEX_OCU_NB", "salario_mes_moneda": "DF_EAR_EMTM_SEX_OCU_CUR_NB",
          "horas": "DF_HOW_TEMP_SEX_OCU_NB", "emp_sexo_edad": "DF_EMP_3EMP_SEX_AGE_OCU_NB"}
paises = pd.read_csv(DATOS / "worldbank/paises_ingreso.csv")["iso3"].tolist() if (DATOS / "worldbank/paises_ingreso.csv").exists() else []
if not paises:
    j = requests.get("https://api.worldbank.org/v2/country?format=json&per_page=400", headers=UA, timeout=60).json()[1]
    paises = [c["id"] for c in j if c["region"]["value"] != "Aggregates"]
lg.info(f"{len(paises)} países")

for clave, flujo in FLUJOS.items():
    salida = d / f"{clave}_isco_todos.csv"; partes = d / f"partes_{clave}"; partes.mkdir(exist_ok=True)
    for iso in paises:
        p = partes / f"{iso}.csv"
        if p.exists(): continue
        url = f"https://sdmx.ilo.org/rest/data/ILO,{flujo},1.0/{iso}.A...?startPeriod=2010&format=csv"
        for i in range(3):
            try:
                r = requests.get(url, headers={**UA, "Accept": "text/csv"}, timeout=120)
                if r.status_code == 404 or (r.status_code == 200 and len(r.text) < 50):
                    p.write_text(""); break          # sin datos para ese país
                r.raise_for_status(); p.write_text(r.text); break
            except Exception as e:
                lg.warning(f"{clave} {iso} intento {i+1}: {e}"); time.sleep(10 * (i + 1))
        time.sleep(0.4)
    frames = [pd.read_csv(f) for f in partes.glob("*.csv") if f.stat().st_size > 50]
    if frames:
        todo = pd.concat(frames, ignore_index=True); todo.to_csv(salida, index=False)
        registrar(salida, f"ILOSTAT SDMX {flujo}", "https://sdmx.ilo.org/rest/data/ILO,%s,1.0/" % flujo, nota=f"{todo.REF_AREA.nunique()} países, {len(todo)} filas")
        lg.info(f"{clave}: {todo.REF_AREA.nunique()} países, {len(todo):,} filas")
    else:
        lg.error(f"{clave}: sin datos")

# Informe de resolución (empleo)
e = pd.read_csv(d / "emp_isco_todos.csv")
e = e[e.OCU.astype(str).str.startswith("OCU_ISCO08_") & (e.SEX == "SEX_T")]
e["digitos"] = e.OCU.str.replace("OCU_ISCO08_", "").str.len()
e = e[e.digitos.isin([1, 2])]
res = e.groupby(["REF_AREA", "digitos"]).TIME_PERIOD.max().unstack()
lineas = ["# Resolución ISCO-08 por país en ILOSTAT (empleo por ocupación)", "",
          f"- Países con ISCO-08 a 1 dígito: **{res[1].notna().sum() if 1 in res else 0}** (≥2022: {(res[1] >= 2022).sum() if 1 in res else 0})",
          f"- Países con ISCO-08 a 2 dígitos: **{res[2].notna().sum() if 2 in res else 0}** (≥2022: {(res[2] >= 2022).sum() if 2 in res else 0})", "",
          "| País | último año 1 díg. | último año 2 díg. |", "|---|---|---|"]
for iso, fila in res.sort_index().iterrows():
    lineas.append(f"| {iso} | {int(fila.get(1)) if pd.notna(fila.get(1)) else '—'} | {int(fila.get(2)) if pd.notna(fila.get(2)) else '—'} |")
(d / "RESOLUCION.md").write_text("\n".join(lineas)); lg.info("\n".join(lineas[:5]))
