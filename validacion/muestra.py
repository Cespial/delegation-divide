"""Muestra de validación humana (preregistro §5): 1.500 tareas estratificadas por gran grupo ISCO,
proporcional al peso de empleo del grupo (ILOSTAT mundial si ya existe; si no, uniforme), mínimo 60 por grupo.
Genera una hoja por evaluador con orden aleatorio propio y sin ninguna puntuación de modelo."""
import sys, random; from pathlib import Path
import pandas as pd
R = Path(__file__).resolve().parents[1]; SEM = 20261020; N = 1500; MIN = 60
pares = pd.read_parquet(R / "datos/pares_isco_tarea.parquet"); pares = pares[~pares.imputado]
tar = pd.read_parquet(R / "datos/tareas_unicas.parquet")
# gran grupo de cada tarea = el de mayor peso
g = pares.sort_values("peso", ascending=False).drop_duplicates("Task ID")[["Task ID", "isco08"]]
g["gg"] = g.isco08.str[0]; tar = tar.merge(g.rename(columns={"Task ID": "task_id"}), on="task_id")
emp = R / "datos/ilostat/emp_isco_todos.csv"; cuota = None
if emp.exists():
    e = pd.read_csv(emp, usecols=["SEX", "OCU", "TIME_PERIOD", "OBS_VALUE", "REF_AREA"])
    e = e[(e.SEX == "SEX_T") & e.OCU.str.match(r"OCU_ISCO08_\d$")]
    e = e.sort_values("TIME_PERIOD").drop_duplicates(["REF_AREA", "OCU"], keep="last")
    e["gg"] = e.OCU.str[-1]; w = e[e.gg != "0"].groupby("gg").OBS_VALUE.sum(); cuota = (w / w.sum())
if cuota is None:
    cuota = pd.Series(1 / 9, index=list("123456789"))
n = (cuota * (N - MIN * len(cuota))).round().astype(int) + MIN
disp = tar.gg.value_counts()
n = pd.concat([n, disp], axis=1, keys=["n", "d"]).fillna(0).astype(int).apply(lambda r: min(r.n, r.d), axis=1)
while n.sum() < N:  # el faltante va a los grupos con tareas de sobra, en proporción a su cuota
    holgura = (disp - n).clip(lower=0); k = (cuota.reindex(holgura.index).fillna(0) * (holgura > 0)).idxmax(); n[k] += 1
muestra = pd.concat([tar[tar.gg == k].sample(v, random_state=SEM) for k, v in n.items() if v > 0])
muestra = muestra[["task_id", "titulo", "texto", "gg", "isco08"]].reset_index(drop=True)
muestra.to_csv(R / "validacion/muestra_1500.csv", index=False)
print("por gran grupo:", muestra.gg.value_counts().sort_index().to_dict(), "| total", len(muestra), "| cuotas de", "ILOSTAT" if emp.exists() else "uniforme")
cols = ["level (0-3)", "share_delegable (0-100)", "minutes_human", "barrier_physical (S/N)", "barrier_accountability (S/N)",
        "barrier_trust (S/N)", "barrier_access (S/N)", "confidence (LOW/MEDIUM/HIGH)", "comentario"]
for ev in ("E1", "E2", "E3"):
    h = muestra[["task_id", "titulo", "texto"]].sample(frac=1, random_state=SEM + int(ev[1])).rename(columns={"titulo": "occupation", "texto": "task"})
    for c in cols: h[c] = ""
    with pd.ExcelWriter(R / f"validacion/hoja_{ev}.xlsx") as x:
        h.to_excel(x, sheet_name="tareas", index=False)
        pd.DataFrame({"rúbrica": (R / "scoring/prompts/rubrica_v1.md").read_text().splitlines()}).to_excel(x, sheet_name="rubrica", index=False)
print("hojas E1–E3 en validacion/")
