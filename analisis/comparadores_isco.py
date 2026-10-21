"""Comparadores → ISCO-08 4 díg. con el mismo puente de construir_crosswalk.py (analisis/puente.py).
Medidas por tarea (Eloundou beta y GPT-4, penetración AEI) se agregan con los pesos de pares_isco_tarea; medidas por ocupación
O*NET o SOC (Eloundou occ_level, Felten AIOE, Webb, Eisfeldt, AEI job_exposure) con el peso de mapeo onet19→ISCO.
Salidas: datos/comparadores_isco.parquet, datos/comparadores_tarea.parquet, datos/aei_pais.csv (uso por país, H2)."""
import sys, re; sys.path.insert(0, "noche"); sys.path.insert(0, "analisis")
from comun import *
from puente import puente
import pandas as pd, numpy as np
lg = log("comparadores_isco"); K = DATOS / "comparadores"
pares = pd.read_parquet(DATOS / "pares_isco_tarea.parquet").rename(columns={"Task ID": "task_id"})
tareas = pd.read_parquet(DATOS / "tareas_unicas.parquet")
P = puente(); P["soc7"] = P.onet19.str[:7]
norm = lambda s: s.astype(str).str.lower().str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip()

# --- por tarea ---
T = tareas[["task_id"]].copy()
el = K / "eloundou/full_labelset.tsv"
if el.exists():
    e = pd.read_csv(el, sep="\t"); e["task_id"] = pd.to_numeric(e["Task ID"], errors="coerce")
    e["gpt4_beta"] = e.gpt4_exposure.map({"E0": 0.0, "E1": 1.0, "E2": 0.5})
    e = e.groupby("task_id")[["beta", "gpt4_beta"]].mean().rename(columns=lambda c: f"eloundou_{c}")
    T = T.merge(e, left_on="task_id", right_index=True, how="left")
    lg.info(f"Eloundou tareas: {len(e):,} en el archivo; emparejadas {T.eloundou_beta.notna().sum():,} de {len(T):,}")
tp = K / "anthropic_economic_index/labor_market_impacts/task_penetration.csv"
if tp.exists():
    a = pd.read_csv(tp); a["k"] = norm(a.task); a = a.groupby("k").penetration.mean()
    T["aei_penetracion"] = norm(tareas.texto).map(a).values
    lg.info(f"AEI task_penetration: {len(a):,} textos; emparejadas por texto normalizado {T.aei_penetracion.notna().sum():,} de {len(T):,}")
T.to_parquet(DATOS / "comparadores_tarea.parquet", index=False)
registrar(DATOS / "comparadores_tarea.parquet", "derivado: comparadores_isco.py", nota=f"{len(T)} tareas")

def por_tarea(col):
    d = pares.merge(T[["task_id", col]], on="task_id").dropna(subset=[col])
    return (d.peso * d[col]).groupby(d.isco08).sum() / d.peso.groupby(d.isco08).sum()

# --- por ocupación: valor en onet19 → ISCO con peso_map ---
def por_onet(valor_onet19):
    d = P.assign(v=P.onet19.map(valor_onet19)).dropna(subset=["v"])
    return (d.peso_map * d.v).groupby(d.isco08).sum() / d.peso_map.groupby(d.isco08).sum()

def soc_a_onet(serie_soc):
    """serie indexada por SOC 6 díg. (int) → valor por onet19: SOC 2010 original, luego rescatado, luego media del grupo amplio."""
    s = serie_soc.groupby(level=0).mean(); amplio = s.groupby(s.index // 10).mean()
    v = P.soc10_orig.map(s).fillna(P.soc10.map(s)).fillna((P.soc10_orig // 10).map(amplio))
    return v.groupby(P.onet19).mean()

def soc_int(x): return pd.to_numeric(pd.Series(x).astype(str).str.replace(r"\D", "", regex=True).str[:6], errors="coerce").values

R = {}
for c in [c for c in T.columns if c != "task_id"]: R[c] = por_tarea(c)
oc = K / "eloundou/occ_level.csv"
if oc.exists():
    o = pd.read_csv(oc).set_index("O*NET-SOC Code")
    for c in ("dv_rating_beta", "human_rating_beta"): R[f"eloundou_occ_{c.split('_')[0]}_beta"] = por_onet(o[c])
fe = K / "felten/AIOE_DataAppendix.xlsx"
if fe.exists():
    f = pd.read_excel(fe, sheet_name="Appendix A"); f.index = soc_int(f["SOC Code"]); R["felten_aioe"] = por_onet(soc_a_onet(f.AIOE.dropna()))
    lg.info(f"Felten AIOE: {len(f)} SOC 2010")
wb = K / "webb/autoScores.csv"
if wb.exists():
    w = pd.read_csv(wb); w = w[w.year == w.year.max()]; w.index = soc_int(w.simpleOcc)
    for c in ("pct_ai", "pct_software", "pct_robot"): R[f"webb_{c}"] = por_onet(soc_a_onet(w[c].dropna()))
    lg.info(f"Webb: año {int(w.year.max())}, {len(w)} SOC")
ei = K / "eisfeldt/genaiexp_scores.csv"
if ei.exists():
    g = pd.read_csv(ei); g.index = soc_int(g.soc2010); R["eisfeldt_genaiexp"] = por_onet(soc_a_onet(g.genaiexp_estz_total.dropna()))
je = K / "anthropic_economic_index/labor_market_impacts/job_exposure.csv"
if je.exists():
    j = pd.read_csv(je).groupby("occ_code").observed_exposure.mean()
    v = P.soc7.map(j); v = v.fillna(P.soc7.str[:6].map(j.groupby(j.index.str[:6]).mean()))   # SOC 2018 = prefijo de O*NET-SOC 2019
    R["aei_exposicion_obs"] = por_onet(v.groupby(P.onet19).mean())
ci = pd.DataFrame(R); ci.index.name = "isco08"; ci = ci.reset_index()
ci.to_parquet(DATOS / "comparadores_isco.parquet", index=False)
registrar(DATOS / "comparadores_isco.parquet", "derivado: comparadores_isco.py", nota=f"{len(ci)} ISCO × {len(R)} medidas")
n_isco = pares.isco08.nunique()
lg.info("cobertura ISCO-08 (de %d): " % n_isco + "; ".join(f"{c} {ci[c].notna().sum()}" for c in R))

# --- uso por país (H2): última release con geography=country y usage_per_capita_index ---
hall = []
for rel in sorted(K.glob("anthropic_economic_index/release_*"), reverse=True):
    for f in sorted(rel.rglob("aei_*claude_ai*.csv")):
        cab = open(f).readline()
        if "geo_level" not in cab and "geography" not in cab: continue
        d = pd.read_csv(f, usecols=lambda c: c in {"date_start", "date_end", "geo_id", "geo_level", "geography", "metric_id", "variable", "value", "category_name", "facet"}, low_memory=False)
        lv = "geo_level" if "geo_level" in d else "geography"; met = "metric_id" if "metric_id" in d else "variable"
        d = d[(d[lv] == "country") & d[met].isin(["usage_per_capita_index", "usage_pct"])]
        if "category_name" in d: d = d[d.category_name.isin(["overall"])]
        if d.empty: continue
        hall.append((rel.name, f.name, d.rename(columns={lv: "geo_level", met: "metric_id"}))); break
    if hall: break
if hall:
    rel, arch, d = hall[0]
    u = d.pivot_table(index="geo_id", columns="metric_id", values="value", aggfunc="mean").reset_index().rename(columns={"geo_id": "iso3"})
    u["meses"] = d.groupby("geo_id").date_start.nunique().reindex(u.iso3).values if "date_start" in d else 1
    u["release"] = rel; u["archivo"] = arch
    u.to_csv(DATOS / "aei_pais.csv", index=False); registrar(DATOS / "aei_pais.csv", f"derivado: comparadores_isco.py ({rel}/{arch})")
    lg.info(f"AEI por país: {rel}/{arch} → {len(u)} países con usage_per_capita_index (media de {d.date_start.nunique() if 'date_start' in d else 1} meses)")
else:
    lg.warning("AEI: ninguna release trae uso por país (geo_level=country); H2 no se puede estimar")
