"""Paso 7: informe de la noche a partir del manifiesto y los logs."""
import sys, json; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
from datetime import date
import pandas as pd
filas = [json.loads(l) for l in open(MANIFIESTO) if l.strip()] if MANIFIESTO.exists() else []
df = pd.DataFrame(filas)
out = RAIZ / "docs/noche" / date.today().isoformat(); out.mkdir(parents=True, exist_ok=True)
L = [f"# Informe de captura nocturna — {date.today().isoformat()}", ""]
if len(df):
    df = df.drop_duplicates("archivo", keep="last")
    L += [f"- Archivos capturados: **{int(df.ok.sum())}** OK, **{int((~df.ok).sum())}** fallidos", f"- Volumen: **{df.bytes.sum()/1e9:.2f} GB**", ""]
    L += ["## Por fuente", "", "| Fuente | archivos | GB | fallos |", "|---|---|---|---|"]
    for fu, g in df.groupby("fuente"):
        L.append(f"| {fu} | {len(g)} | {g.bytes.sum()/1e9:.3f} | {int((~g.ok).sum())} |")
    fa = df[~df.ok]
    if len(fa):
        L += ["", "## Fallos (acción humana)", ""] + [f"- `{r.archivo}` ← {r.url or r.fuente}: {r.nota}" for r in fa.itertuples()]
res = DATOS / "ilostat/RESOLUCION.md"
if res.exists(): L += ["", "## ILOSTAT", ""] + res.read_text().splitlines()[2:5]
t = DATOS / "tareas_unicas.parquet"
if t.exists(): L += ["", f"## Tareas", "", f"- Tareas únicas O*NET con CIUO: **{len(pd.read_parquet(t))}**"]
g = DATOS / "esco/isco08_grupos_unitarios.csv"
if g.exists(): L += [f"- Grupos unitarios ISCO-08 desde ESCO: **{len(pd.read_csv(g))}** (esperados 436)"]
for lg_ in sorted(LOGS.glob("0*.log")):
    err = [l.strip() for l in open(lg_) if " ERROR " in l]
    if err: L += ["", f"## Errores en {lg_.name}", ""] + [f"- {e}" for e in err[:30]]
(out / "INFORME-NOCHE.md").write_text("\n".join(L)); print("\n".join(L))
