"""ILOSTAT empleo por ISCO-08 a 2 dígitos (DF_EMP_TEMP_SEX_OC2_NB, dimensión OC2), país por país. Complemento de 02."""
import sys, time; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
import pandas as pd, requests
lg = log("02b_ilostat_oc2"); d = DATOS / "ilostat"; partes = d / "partes_emp2"; partes.mkdir(parents=True, exist_ok=True)
paises = pd.read_csv(DATOS / "worldbank/paises_ingreso.csv").iso3.tolist()
for iso in paises:
    p = partes / f"{iso}.csv"
    if p.exists(): continue
    for i in range(3):
        try:
            r = requests.get(f"https://sdmx.ilo.org/rest/data/ILO,DF_EMP_TEMP_SEX_OC2_NB,1.0/{iso}.A...?startPeriod=2010&format=csv",
                             headers={**UA, "Accept": "text/csv"}, timeout=120)
            if r.status_code in (404, 422) or (r.status_code == 200 and len(r.text) < 50): p.write_text(""); break
            r.raise_for_status(); p.write_text(r.text); break
        except Exception as e:
            lg.warning(f"{iso} intento {i+1}: {e}"); time.sleep(10 * (i + 1))
    time.sleep(0.4)
todo = pd.concat([pd.read_csv(f) for f in partes.glob("*.csv") if f.stat().st_size > 50], ignore_index=True)
todo.to_csv(d / "emp2_isco_todos.csv", index=False)
x = todo[(todo.SEX == "SEX_T") & todo.OC2.str.match(r"OC2_ISCO08_\d\d$")].groupby("REF_AREA").TIME_PERIOD.max()
msg = f"2 dígitos: {len(x)} países; ≥2019: {(x >= 2019).sum()}; ≥2022: {(x >= 2022).sum()}"
registrar(d / "emp2_isco_todos.csv", "ILOSTAT SDMX DF_EMP_TEMP_SEX_OC2_NB", nota=msg); lg.info(msg)
with open(d / "RESOLUCION.md", "a") as f: f.write(f"\n\n## Empleo a 2 dígitos (OC2)\n\n- {msg}\n")
