"""Robustez exploratoria preregistrada (OSF 344-83): «robustness with ESCO essential skills instead of O*NET tasks».
Banco: datos/esco_banco.parquet + datos/esco_pares_isco.parquet (analisis/esco_banco.py), puntuado solo con Sonnet en modo neutro
(scoring/correr_esco.sh → scoring/salidas/esco/sonnet.jsonl; se leen también las particiones sonnet.p?.jsonl si aún no se unieron).

ADI_ESCO(ISCO 4 díg.) = media con pesos iguales por skill de 1[nivel ≥ 2]. País y mundo con EXACTAMENTE la maquinaria de
analisis/indice.py (importada, no copiada): atlas con la regla D3, pesos 4 díg. por ingreso D1 (OES para ingreso alto, GEIH resto).
Claims → salidas_robustez/claims_esco.jsonl (generar_cifras.py los lee después de salidas/claims.jsonl):
  robustez.esco.h1.pendiente / .h1.p (una cola, H1: pendiente > 0) / .h1.n · robustez.esco.titular.l2
  robustez.esco.r.isco      Pearson ADI_ESCO vs ADI O*NET solo Sonnet (scoring/salidas/main/sonnet.jsonl) a ISCO 4 díg.
  robustez.esco.h1.pendiente.gg6  pendiente H1 con el índice O*NET de consenso (salidas/indice_isco_detalle.csv) y ESCO solo en el gran grupo 6
  robustez.esco.n.skills / .n.isco / .cobertura.pct
Con menos del 80 % del banco puntuado, todos los resultados salen «--» (los conteos del banco sí se emiten)."""
import json, os, sys
from datetime import datetime
sys.path.insert(0, "analisis"); sys.path.insert(0, "noche")
from comun import *
import numpy as np, pandas as pd
import indice as ix   # cargar_atlas, vectores_peso, pesos_d1, matriz_paises, leer_union, leer_modelo

lg = log("robustez_esco")
SALR = RAIZ / "salidas_robustez"; SALR.mkdir(exist_ok=True)
ESC = RAIZ / "scoring/salidas/esco"; MIN_COB = float(os.environ.get("ESCO_MIN_COB", "0.80"))   # variable solo para probar el código
CL = []


def claim(i, v, nota=""):
    if isinstance(v, (np.floating, np.integer)): v = v.item()
    if isinstance(v, float) and not np.isfinite(v): v = "--"
    CL.append({"id": i, "valor": v, "t": datetime.now().isoformat(timespec="seconds"), "sintetico": False, **({"nota": nota} if nota else {})})


def escribir():
    with open(SALR / "claims_esco.jsonl", "w") as f:
        for c in CL: f.write(json.dumps(c, ensure_ascii=False) + "\n")
    registrar(SALR / "claims_esco.jsonl", "derivado: robustez_esco.py", nota=f"{len(CL)} claims")


def h1(adi_pais, pa):
    import statsmodels.api as sm
    from scipy import stats
    h = pa.assign(y=100 * adi_pais).dropna(subset=["pib_pc_ppp"])
    r = sm.OLS(h.y, sm.add_constant(np.log(h.pib_pc_ppp))).fit(); b, se = r.params.iloc[1], r.bse.iloc[1]
    return b, stats.t.sf(b / se, r.df_resid), int(r.nobs)


banco = pd.read_parquet(DATOS / "esco_banco.parquet"); pares = pd.read_parquet(DATOS / "esco_pares_isco.parquet")
claim("robustez.esco.n.skills", len(banco)); claim("robustez.esco.n.isco", int(pares.isco08.nunique()))
RES = ["robustez.esco.h1.pendiente", "robustez.esco.h1.p", "robustez.esco.h1.n", "robustez.esco.titular.l2", "robustez.esco.r.isco",
       "robustez.esco.h1.pendiente.gg6"]
rutas = ([ESC / "sonnet.jsonl"] if (ESC / "sonnet.jsonl").exists() else []) + sorted(ESC.glob("sonnet.p*.jsonl"))
pt = ix.leer_union(rutas) if rutas else pd.DataFrame(columns=ix.CAMPOS)
pt = pt[pt.index.isin(banco.task_id)]
cob = len(pt) / len(banco); claim("robustez.esco.cobertura.pct", 100 * cob)
lg.info(f"ESCO: {len(pt):,} de {len(banco):,} skills puntuadas ({cob:.1%}) en {[p.name for p in rutas]}")
if cob < MIN_COB:
    for i in RES: claim(i, "--", nota=f"banco ESCO puntuado al {100 * cob:.1f} % (< {100 * MIN_COB:.0f} %): correr scoring/correr_esco.sh")
    escribir(); lg.info("menos del 80 % puntuado: claims «--»"); sys.exit(0)

# --- ISCO 4 díg.: pesos iguales por skill entre las puntuadas
p = pares[pares.task_id.isin(pt.index)].copy(); p["l2"] = (pt.level.reindex(p.task_id).values >= 2).astype(float)
occ = p.groupby("isco08").apply(lambda d: np.average(d.l2, weights=d.peso), include_groups=False).rename("adi_esco")
isco = occ.index.values.astype(str); O = occ.values

# --- países y mundo con la maquinaria de indice.py
paises, meta = ix.cargar_atlas(); v_geih, v_oes = ix.vectores_peso(isco)
M, E = ix.matriz_paises(isco, paises, ix.pesos_d1(meta, v_geih, v_oes))
pa = pd.DataFrame({"iso3": sorted(paises.iso3.unique()), "adi_esco": M @ O, "empleo_total": E}).merge(meta[["iso3", "pib_pc_ppp"]], on="iso3", how="left")
wE = E / E.sum(); claim("robustez.esco.titular.l2", 100 * float(wE @ (M @ O)))
b, pv, n = h1(pa.adi_esco, pa); claim("robustez.esco.h1.pendiente", b); claim("robustez.esco.h1.p", pv); claim("robustez.esco.h1.n", n)
lg.info(f"ADI_ESCO: titular {100 * float(wE @ (M @ O)):.1f} % · H1 pendiente {b:.2f} (p={pv:.3g}, n={n}) · {len(isco)} ISCO")

# --- correlación con O*NET solo Sonnet a ISCO 4 díg. (mismos pesos de tarea que indice.py)
son = RAIZ / "scoring/salidas/main/sonnet.jsonl"
if son.exists():
    d, _ = ix.leer_modelo(son); po = pd.read_parquet(DATOS / "pares_isco_tarea.parquet").rename(columns={"Task ID": "task_id"})
    po = po[po.task_id.isin(d.index)].copy(); po["l2"] = (d.level.reindex(po.task_id).values >= 2).astype(float)
    on = po.groupby("isco08").apply(lambda g: np.average(g.l2, weights=g.peso), include_groups=False)
    j = pd.concat([occ, on.rename("onet")], axis=1, join="inner")
    claim("robustez.esco.r.isco", j.adi_esco.corr(j.onet)); claim("robustez.esco.n.isco.comun", len(j))
    lg.info(f"r(ADI_ESCO, ADI O*NET Sonnet) = {j.adi_esco.corr(j.onet):.3f} en {len(j)} ISCO")
else:
    claim("robustez.esco.r.isco", "--", nota="falta scoring/salidas/main/sonnet.jsonl")

# --- gran grupo 6 con ESCO, resto con el índice O*NET de consenso (salidas/indice_isco_detalle.csv de indice.py)
det = RAIZ / "salidas/indice_isco_detalle.csv"
if det.exists():
    oc = pd.read_csv(det, dtype={"isco08": str}).set_index("isco08").adi_l2
    mx = oc.copy(); g6 = mx.index.str.startswith("6"); mx[g6] = occ.reindex(mx.index[g6]).fillna(oc[g6]).values
    i2 = mx.index.values.astype(str); vg, vo = ix.vectores_peso(i2)
    M2, _ = ix.matriz_paises(i2, paises, ix.pesos_d1(meta, vg, vo))
    b6, _, _ = h1(pd.Series(M2 @ mx.values), pa); claim("robustez.esco.h1.pendiente.gg6", b6)
    lg.info(f"H1 con ESCO solo en el gran grupo 6: pendiente {b6:.2f}")
else:
    claim("robustez.esco.h1.pendiente.gg6", "--", nota="falta salidas/indice_isco_detalle.csv (correr analisis/indice.py)")
occ.rename_axis("isco08").reset_index().assign(n_skills=lambda x: x.isco08.map(p.groupby("isco08").size())).to_csv(SALR / "adi_esco_isco.csv", index=False)
escribir()
