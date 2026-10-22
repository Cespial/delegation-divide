"""Paso 23 (exploratorio, preregistrado en OSF «Exploratory analysis»): gradientes de delegabilidad por sexo, edad e informalidad
en Colombia con la GEIH (DANE, ene-2024 a ago-2026, CIUO-08 A.C. a 4 dígitos, que se lee como ISCO-08 igual que analisis/indice.py).

ADI de un subgrupo s = Σ_o e_so · ADI_o / Σ_o e_so, con e_so el empleo GEIH del subgrupo en la ocupación o (factor de expansión,
promedio de los meses) y ADI_o el índice de ocupación publicado. Los intervalos salen del MISMO bootstrap del índice (tareas
remuestreadas dentro de ocupación, semilla 20261020, 1.000 réplicas): el script lo reproduce desde salidas/adi_tarea.csv y
datos/pares_isco_tarea.parquet y comprueba que las réplicas devuelven los intervalos de salidas/indice_isco_detalle.csv antes de seguir.
No hay incertidumbre muestral de la encuesta en los intervalos (son de la calificación); se declara en el texto.

Informal = no cotiza a pensión (P6920 ≠ 1), la variable del panel de analisis/microdatos_geih.py.
Escribe salidas_microdatos/gradientes_col.csv y salidas_microdatos/claims_geih.jsonl (ids geih.*; formato_cifras.py los lee
sin pisar ids existentes). Uso: .venv/bin/python -I analisis/gradientes_geih.py (desde la raíz del repo)."""
import json, sys
from datetime import datetime
sys.path.insert(0, "noche")
from comun import *
import numpy as np, pandas as pd

lg = log("23_gradientes_geih")
SAL = RAIZ / "salidas"; OUT = RAIZ / "salidas_microdatos"; OUT.mkdir(exist_ok=True)
SEMILLA, B, PASOS = 20261020, 1000, 50          # los de analisis/indice.py: mismas réplicas

# --- réplicas bootstrap de las ocupaciones (copia literal de la lógica de indice.py)
tareas = pd.read_parquet(DATOS / "tareas_unicas.parquet").reset_index(drop=True)
t = pd.read_csv(SAL / "adi_tarea.csv").set_index("task_id").reindex(tareas.task_id)
tid = tareas.task_id.values; pos = pd.Series(np.arange(len(tid)), index=tid)
nivel = t.nivel.values; share = t.share.values; rated = t.n_modelos.fillna(0).values > 0
pares = pd.read_parquet(DATOS / "pares_isco_tarea.parquet").rename(columns={"Task ID": "task_id"})
pares = pares[pares.task_id.isin(pos.index)]; pares["i"] = pos[pares.task_id].values
pares = pares[rated[pares.i.values]].sort_values(["isco08", "i"]).reset_index(drop=True)
isco = np.array(sorted(pares.isco08.unique())); gi = pd.Series(np.arange(len(isco)), index=isco)[pares.isco08].values
w = pares.peso.values; ti = pares.i.values
X = np.nan_to_num(np.stack([(nivel[ti] >= 2), (nivel[ti] == 3), share[ti] / 100], 1).astype(float))
den = np.bincount(gi, w, len(isco)); O = np.stack([np.bincount(gi, w * X[:, k], len(isco)) for k in range(3)], 1) / den[:, None]
starts = np.r_[0, np.flatnonzero(np.diff(gi)) + 1]; sizes = np.diff(np.r_[starts, len(gi)])
rng = np.random.default_rng(SEMILLA); OB = np.empty((B, len(isco), 3))
for b0 in range(0, B, PASOS):
    nb = min(PASOS, B - b0)
    dr = starts[gi][None, :] + np.floor(rng.random((nb, len(gi))) * sizes[gi][None, :]).astype(np.int64)
    Wd = w[dr]; dd = np.add.reduceat(Wd, starts, axis=1)
    for k in range(3): OB[b0:b0 + nb, :, k] = np.add.reduceat(Wd * X[dr, k], starts, axis=1) / dd

# control: las réplicas deben devolver el índice y los intervalos publicados
det = pd.read_csv(SAL / "indice_isco_detalle.csv", dtype={"isco08": str}).set_index("isco08").reindex(isco)
# el CSV publicado va redondeado a 4 decimales (indice.py, r4d): se compara redondeando igual
r4 = lambda x: np.round(x, 4)
pares_ctrl = [(O[:, 0], det.adi_l2), (O[:, 1], det.adi_l3), (np.percentile(OB[:, :, 0], 2.5, 0), det.l2_lo), (np.percentile(OB[:, :, 0], 97.5, 0), det.l2_hi),
              (np.percentile(OB[:, :, 1], 2.5, 0), det.l3_lo), (np.percentile(OB[:, :, 1], 97.5, 0), det.l3_hi)]
malas = sum(int((np.abs(r4(a) - b.values) > 1e-9).sum()) for a, b in pares_ctrl)
if malas: sys.exit(f"el bootstrap reproducido no coincide con indice_isco_detalle.csv en {malas} valores; no sigo")
lg.info(f"bootstrap reproducido: {B} réplicas; índice e intervalos de las {len(isco)} ocupaciones iguales a los publicados (4 decimales)")

# --- GEIH: empleo por subgrupo y ocupación
p = pd.read_parquet(DATOS / "microdatos/geih_panel.parquet", columns=["anio", "mes", "ciuo4", "sexo", "edad", "informal", "factor"])
p = p[p.factor.notna() & p.ciuo4.str.match(r"^\d{4}$", na=False)]
meses = p[["anio", "mes"]].drop_duplicates(); nmes = len(meses)
p["edad_g"] = pd.cut(p.edad, [14, 24, 54, 200], labels=["15_24", "25_54", "55_mas"])
dentro = p.ciuo4.isin(isco); cobertura = 100 * p.factor[dentro].sum() / p.factor.sum()
q = p[dentro]
GRUPOS = {"total": None, "sexo": ("sexo", {"mujeres": "M", "hombres": "H"}), "edad": ("edad_g", {"15_24": "15_24", "25_54": "25_54", "55_mas": "55_mas"}),
          "informal": ("informal", {"si": 1, "no": 0})}
ix = pd.Series(np.arange(len(isco)), index=isco)


def vector(d):
    e = d.groupby("ciuo4").factor.sum() / nmes
    v = np.zeros(len(isco)); v[ix[e.index].values] = e.values; return v


C, filas, R = [], [], {}
def claim(i, v): C.append({"id": "geih." + i, "valor": float(v) if isinstance(v, (float, np.floating)) else int(v), "t": datetime.now().isoformat(timespec="seconds"), "sintetico": False})
claim("n.obs", len(p)); claim("n.meses", nmes); claim("anio.desde", int(meses.anio.min())); claim("anio.hasta", int(meses.anio.max()))
claim("cobertura.empleo.pct", cobertura); claim("empleo.millones", q.factor.sum() / nmes / 1e6)
total = vector(q)
for g, spec in GRUPOS.items():
    cats = {"todos": None} if spec is None else spec[1]
    for nom, val in cats.items():
        d = q if spec is None else q[q[spec[0]] == val]
        v = vector(d); R[(g, nom)] = v
        pt = (v @ O[:, :2]) / v.sum(); bt = np.einsum("o,bok->bk", v, OB[:, :, :2]) / v.sum()
        lo, hi = np.percentile(bt, 2.5, 0), np.percentile(bt, 97.5, 0)
        base = "total" if spec is None else f"{g}.{nom}"
        for k, n in enumerate(("l2", "l3")):
            claim(f"{base}.{n}", 100 * pt[k]); claim(f"{base}.{n}.lo", 100 * lo[k]); claim(f"{base}.{n}.hi", 100 * hi[k])
        claim(f"{base}.empleo.pct", 100 * v.sum() / total.sum())
        filas.append(dict(grupo=g, categoria=nom, empleo_miles=v.sum() / 1e3, empleo_pct=100 * v.sum() / total.sum(), adi_l2=100 * pt[0], l2_lo=100 * lo[0],
                          l2_hi=100 * hi[0], adi_l3=100 * pt[1], l3_lo=100 * lo[1], l3_hi=100 * hi[1]))

# brechas con sus intervalos (misma réplica en ambos lados)
for nom, (a, b) in {"sexo": (("sexo", "mujeres"), ("sexo", "hombres")), "informal": (("informal", "si"), ("informal", "no")),
                    "edad": (("edad", "15_24"), ("edad", "55_mas"))}.items():
    va, vb = R[a], R[b]
    for k, n in enumerate(("l2", "l3")):
        d = (va @ O[:, k]) / va.sum() - (vb @ O[:, k]) / vb.sum(); db = (OB[:, :, k] @ va) / va.sum() - (OB[:, :, k] @ vb) / vb.sum()
        claim(f"brecha.{nom}.{n}", 100 * d); claim(f"brecha.{nom}.{n}.lo", 100 * np.percentile(db, 2.5)); claim(f"brecha.{nom}.{n}.hi", 100 * np.percentile(db, 97.5))

pd.DataFrame(filas).to_csv(OUT / "gradientes_col.csv", index=False)
with open(OUT / "claims_geih.jsonl", "w") as f:
    for c in C: f.write(json.dumps(c, ensure_ascii=False) + "\n")
lg.info(f"GEIH {len(p):,} persona-mes, {nmes} meses; {cobertura:.1f} % del empleo en ocupaciones del índice; {len(C)} claims → salidas_microdatos/")
for r in filas: lg.info(f"  {r['grupo']:>8} {r['categoria']:>8}: ADI {r['adi_l2']:.1f} [{r['l2_lo']:.1f}–{r['l2_hi']:.1f}]  ADI3 {r['adi_l3']:.2f}  ({r['empleo_pct']:.1f} % del empleo)")
