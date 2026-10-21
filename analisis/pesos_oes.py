"""Pesos de empleo a ISCO-08 4 díg. para países de ingreso alto (D1): BLS OES mayo 2024, empleo nacional por ocupación SOC 2018
detallada → O*NET-SOC 2019 (mismo prefijo de 6 díg.) → SOC 2010 → ISCO-08 por analisis/puente.py (el mismo puente del índice).
El empleo de un SOC se reparte por igual entre sus O*NET-SOC y luego con peso_map. Salida: datos/oes/oes_isco.csv (isco08, empleo)."""
import sys; sys.path.insert(0, "noche"); sys.path.insert(0, "analisis")
from comun import *
from puente import puente
import pandas as pd, zipfile
lg = log("pesos_oes"); Z = DATOS / "oes/oesm24nat.zip"
with zipfile.ZipFile(Z) as z:
    o = pd.read_excel(z.open(next(n for n in z.namelist() if n.endswith(".xlsx"))), dtype=str)
o.columns = [c.upper() for c in o.columns]
o = o[o.O_GROUP.str.lower().eq("detailed")].copy(); o["empleo"] = pd.to_numeric(o.TOT_EMP.str.replace(",", ""), errors="coerce")
o = o.dropna(subset=["empleo"]); lg.info(f"OES 2024: {len(o)} ocupaciones detalladas, {o.empleo.sum() / 1e6:.1f} M empleos")
p = puente(); p["soc18"] = p.onet19.str[:7]
m = o[["OCC_CODE", "empleo"]].rename(columns={"OCC_CODE": "soc18"}).merge(p[["soc18", "onet19", "isco08", "peso_map"]], on="soc18")
# SOC 2018 agregados en OES (p. ej. 13-1020, 29-2010, 31-1120) → todos los O*NET-SOC de su grupo de 5 díg.
falta = o[~o.OCC_CODE.isin(m.soc18)][["OCC_CODE", "empleo"]].rename(columns={"OCC_CODE": "soc18"}); falta["pref"] = falta.soc18.str[:6]
p["pref"] = p.onet19.str[:6]
m = pd.concat([m, falta.merge(p[["pref", "onet19", "isco08", "peso_map"]], on="pref").drop(columns="pref")], ignore_index=True)
m["n19"] = m.groupby("soc18").onet19.transform("nunique")
m["e"] = m.empleo / m.n19 * m.peso_map
r = m.groupby("isco08").e.sum().rename("empleo").reset_index()
sin = set(o.OCC_CODE) - set(m.soc18)
lg.info(f"SOC 2018 sin puente: {len(sin)} ({o[o.OCC_CODE.isin(sin)].empleo.sum() / o.empleo.sum():.1%} del empleo) {sorted(sin)[:10]}")
lg.info(f"ISCO con empleo OES: {len(r)}; empleo llevado: {r.empleo.sum() / o.empleo.sum():.1%}")
r.to_csv(DATOS / "oes/oes_isco.csv", index=False); registrar(DATOS / "oes/oes_isco.csv", "derivado: pesos_oes.py", nota=f"{len(r)} ISCO")
registrar(Z, "https://www.bls.gov/oes/special-requests/oesm24nat.zip", nota="BLS OES mayo 2024 nacional")
