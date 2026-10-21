"""Crosswalk tarea O*NET 30.2 → ISCO-08 4 díg. (reemplaza la matriz AHC, que colapsa 440 CIUO en 9 conjuntos de tareas).
Cadena: O*NET-SOC 2019 → O*NET-SOC 2010 (O*NET Center) → SOC 2010 6 díg. → ISCO-08 (IBS, Hardy-Keister-Lewandowski).
Pesos de tarea dentro de ocupación O*NET: importancia (IM) × frecuencia media (FT), como Acemoglu-Autor.
Una ocupación SOC que va a k grupos ISCO reparte su peso 1/k; cada grupo ISCO promedia sus SOC con peso de empleo
cuando se agregue (paso posterior); aquí se guarda el peso de mapeo."""
import sys; sys.path.insert(0, "noche")
from comun import *
import pandas as pd, numpy as np
lg = log("crosswalk"); C = DATOS / "crosswalks"; O = DATOS / "onet"

ts = pd.read_csv(O / "Task Statements.txt", sep="\t")
tr = pd.read_csv(O / "Task Ratings.txt", sep="\t")
ts = ts.merge(pd.read_csv(O / "Occupation Data.txt", sep="\t")[["O*NET-SOC Code", "Title"]], on="O*NET-SOC Code", how="left")
lg.info(f"Task Statements {ts.shape}; Task Ratings {tr.shape}; escalas {tr['Scale ID'].unique().tolist()}")
im = tr[tr["Scale ID"] == "IM"].groupby(["O*NET-SOC Code", "Task ID"])["Data Value"].mean().rename("importancia")
ft = tr[tr["Scale ID"] == "FT"].copy(); ft["c"] = pd.to_numeric(ft["Category"], errors="coerce")
ft = (ft.assign(p=ft["Data Value"] * ft["c"]).groupby(["O*NET-SOC Code", "Task ID"]).p.sum() / 100).rename("frecuencia")  # media en escala 1–7
t = ts.merge(im.reset_index(), on=["O*NET-SOC Code", "Task ID"], how="left").merge(ft.reset_index(), on=["O*NET-SOC Code", "Task ID"], how="left")
t["importancia"] = t.importancia.fillna(t.importancia.median()); t["frecuencia"] = t.frecuencia.fillna(t.frecuencia.median())
t["peso_tarea"] = t.importancia * t.frecuencia
t["peso_tarea"] /= t.groupby("O*NET-SOC Code").peso_tarea.transform("sum")

w = pd.read_csv(C / "onet_2010_to_2019.csv").rename(columns={"O*NET-SOC 2010 Code": "onet10", "O*NET-SOC 2019 Code": "onet19"})
w["soc10"] = w.onet10.str.replace(r"\D", "", regex=True).str[:6].astype(int)
x = pd.read_stata(C / "ibs/soc10_isco08.dta"); x["soc10"] = x.soc10.astype(int); x["isco08"] = x.isco08.astype(str).str.zfill(4)
x["peso_map"] = 1 / x.groupby("soc10").isco08.transform("nunique")
# Rescate: SOC 2010 que el IBS no trae (p. ej. 19-1020, 29-2055) → mismo grupo amplio (5 díg.), «all other» primero
conocidos = set(x.soc10)
def rescatar(c):
    if c in conocidos: return c
    for cand in [c // 10 * 10 + 9] + sorted(k for k in conocidos if k // 10 == c // 10) + sorted(k for k in conocidos if k // 100 == c // 100):
        if cand in conocidos: return cand
    return c
w["soc10"] = w.soc10.map(rescatar)
# O*NET-SOC 2019 sin antecesor 2010 (ocupaciones nuevas): equivalencia manual documentada en el Apéndice B
NUEVAS = {"15-1299.04": 151199, "15-1299.05": 151199, "15-1299.06": 151199, "15-1299.07": 151199}
w = pd.concat([w, pd.DataFrame([{"onet19": k, "soc10": v} for k, v in NUEVAS.items() if k not in set(w.onet19)])], ignore_index=True)
puente = w[["onet19", "soc10"]].drop_duplicates().merge(x, on="soc10")
puente["peso_map"] /= puente.groupby("onet19").soc10.transform("nunique")       # un O*NET 2019 con varios SOC 2010
m = t.rename(columns={"O*NET-SOC Code": "onet19"}).merge(puente, on="onet19", how="inner")
m["peso"] = m.peso_tarea * m.peso_map
sin = set(t["O*NET-SOC Code"]) - set(puente.onet19)
lg.info(f"O*NET-SOC con tareas: {t['O*NET-SOC Code'].nunique()}; sin puente a ISCO: {len(sin)} {sorted(sin)[:8]}")
pares = (m.groupby(["isco08", "Task ID"]).agg(peso=("peso", "sum"), texto=("Task", "first"), tipo=("Task Type", "first"),
         n_onet=("onet19", "nunique")).reset_index())
pares["peso"] /= pares.groupby("isco08").peso.transform("sum")
pares["imputado"] = False
# Grupos ISCO sin tareas propias (residuales «all other» de SOC): heredan las tareas de su grupo de 3 díg.; militares fuera
todos = set(x.isco08); faltan = sorted(todos - set(pares.isco08) - {"0110", "0210", "0310"})
extra = []
for g in faltan:
    h = pares[(pares.isco08.str[:3] == g[:3]) & ~pares.imputado]
    if h.empty: h = pares[(pares.isco08.str[:2] == g[:2]) & ~pares.imputado]
    h = h.groupby("Task ID").agg(peso=("peso", "sum"), texto=("texto", "first"), tipo=("tipo", "first"), n_onet=("n_onet", "max")).reset_index()
    h["peso"] /= h.peso.sum(); h["isco08"] = g; h["imputado"] = True; extra.append(h)
    lg.info(f"imputado {g} desde su grupo padre ({len(h)} tareas)")
if extra: pares = pd.concat([pares] + extra, ignore_index=True)
pares.to_parquet(DATOS / "pares_isco_tarea.parquet", index=False); registrar(DATOS / "pares_isco_tarea.parquet", "derivado: construir_crosswalk.py", nota=f"{len(pares)} pares")
tar = (t.groupby("Task ID").agg(texto=("Task", "first"), tipo=("Task Type", "first"), onet19=("O*NET-SOC Code", "first"),
       titulo=("Title", "first")).reset_index().rename(columns={"Task ID": "task_id"}))
tar = tar[tar.task_id.isin(pares["Task ID"])]
tar.to_parquet(DATOS / "tareas_unicas.parquet", index=False); tar.to_csv(DATOS / "tareas_unicas.csv", index=False)
registrar(DATOS / "tareas_unicas.parquet", "derivado: construir_crosswalk.py", nota=f"{len(tar)} tareas (reemplaza versión AHC)")
conj = pares.groupby("isco08")["Task ID"].apply(lambda s: hash(tuple(sorted(s))))
lg.info(f"ISCO-08 cubiertos: {pares.isco08.nunique()} de 436 | conjuntos de tareas distintos: {conj.nunique()} | tareas: {len(tar)} | pares: {len(pares)}")
lg.info(f"tareas por ISCO: {pares.groupby('isco08').size().describe()[['min','50%','max']].to_dict()}")
