"""Paso 1: O*NET 30.2 + matriz ocupación×tarea de AHC → tareas únicas con CIUO/ISCO y pesos."""
import sys, zipfile; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
import pandas as pd
lg = log("01_onet")
raw = DATOS / "onet"; raw.mkdir(parents=True, exist_ok=True)

# 1. O*NET 30.2 (la copia de AHC; si falla, la 30.0 oficial)
z = raw / "db_30_2_text.zip"
if not copiar(AHC / "data/raw/onet/db_30_2_text.zip", z, "O*NET 30.2 (copia AHC)", lg):
    z = raw / "db_30_0_text.zip"
    descargar("https://www.onetcenter.org/dl_files/database/db_30_0_text.zip", z, "O*NET 30.0", lg)
if z.exists():
    with zipfile.ZipFile(z) as zf:
        for n in zf.namelist():
            b = n.split("/")[-1]
            if b in ("Task Statements.txt", "Task Ratings.txt", "Occupation Data.txt", "Task Categories.txt", "Emerging Tasks.txt"):
                (raw / b).write_bytes(zf.read(n)); registrar(raw / b, "O*NET", nota=f"de {z.name}")
    lg.info("extraídos Task Statements / Ratings / Occupation Data")

# 2. Matriz ocupación×tarea de AHC (CIUO-08 4 díg. × SOC × tarea con pesos)
m = DATOS / "crosswalks/occupation_task_matrix.parquet"
copiar(AHC / "data/processed/occupation_task_matrix.parquet", m, "AHC occupation_task_matrix", lg)
copiar(AHC / "data/processed/occupation_task_summary.parquet", DATOS / "crosswalks/occupation_task_summary.parquet", "AHC occupation_task_summary", lg)
for f in ("ahc_index_by_occupation.csv", "raw_llm_scores.jsonl", "sonnet_validation_scores.jsonl"):
    copiar(AHC / "data/indices" / f, DATOS / "comparadores/ahc" / f, "AHC índice previo", lg)

# 3. Tareas únicas: una fila por Task ID, con todas sus ocupaciones CIUO y el peso total
df = pd.read_parquet(m)
lg.info(f"matriz {df.shape}, CIUO únicos {df['CIUO_code'].nunique()}, tareas únicas {df['Task ID'].nunique()}")
tareas = (df.groupby("Task ID").agg(texto=("Task", "first"), soc=("SOC_code", "first"), n_ciuo=("CIUO_code", "nunique"),
          ciuo=("CIUO_code", lambda s: ",".join(sorted(set(s.astype(str))))), importancia=("importance", "mean"),
          frecuencia=("frequency", "mean"), peso=("weight", "sum")).reset_index().rename(columns={"Task ID": "task_id"}))
tareas.to_parquet(DATOS / "tareas_unicas.parquet", index=False); tareas.to_csv(DATOS / "tareas_unicas.csv", index=False)
registrar(DATOS / "tareas_unicas.parquet", "derivado: 01_onet.py", nota=f"{len(tareas)} tareas únicas")
# Pares ocupación-tarea con peso (para agregar el índice)
pares = df[["CIUO_code", "SOC_code", "Task ID", "importance", "frequency", "weight"]].drop_duplicates()
pares.to_parquet(DATOS / "pares_ciuo_tarea.parquet", index=False); registrar(DATOS / "pares_ciuo_tarea.parquet", "derivado: 01_onet.py", nota=f"{len(pares)} pares")
# Ocupaciones CIUO con título (base del mapa CIUO→ISCO)
occ = df.groupby("CIUO_code").agg(titulo=("occupation_title", "first") if "occupation_title" in df else ("SOC_code", "first"), n_tareas=("Task ID", "nunique")).reset_index()
occ.to_csv(DATOS / "crosswalks/ciuo_ocupaciones.csv", index=False)
lg.info(f"tareas únicas {len(tareas)}, pares {len(pares)}, ocupaciones CIUO {len(occ)}")
