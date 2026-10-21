"""Lote vs. llamada individual sobre las 300 tareas del piloto. Regla fijada antes de mirar: κ cuadrático ≥ 0,80 → lote 25."""
import json, sys; from pathlib import Path
import numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score
R = Path(__file__).resolve().parents[1] / "scoring/salidas"
lee = lambda p: pd.DataFrame([json.loads(l) for l in open(p) if "error" not in l]).drop_duplicates("task_id", keep="last").set_index("task_id")
L = ["# Piloto: formato por lotes vs. individual", ""]
for m in ("sonnet", "haiku"):
    a, b = lee(R / f"piloto/{m}.jsonl"), lee(R / f"piloto_lote/{m}.jsonl"); c = a.index.intersection(b.index)
    k = cohen_kappa_score(a.loc[c, "level"], b.loc[c, "level"], weights="quadratic")
    L += [f"- **{m}**: n={len(c)} · acuerdo exacto {np.mean(a.loc[c,'level']==b.loc[c,'level']):.1%} · κ cuadrático {k:.3f} · "
          f"Δ share medio {np.mean(b.loc[c,'share_delegable']-a.loc[c,'share_delegable']):+.1f} pp · nivel medio {a.loc[c,'level'].mean():.2f} → {b.loc[c,'level'].mean():.2f} · "
          f"decisión {'lote 25' if k >= 0.80 else 'NO PASA → lote 10'}"]
rr = R / "piloto/sonnet_r2.jsonl"
if rr.exists():
    a, b = lee(R / "piloto/sonnet.jsonl"), lee(rr); c = a.index.intersection(b.index)
    L.append(f"- **test-retest sonnet (individual)**: n={len(c)} · exacto {np.mean(a.loc[c,'level']==b.loc[c,'level']):.1%} · κ {cohen_kappa_score(a.loc[c,'level'], b.loc[c,'level'], weights='quadratic'):.3f}")
a, b = lee(R / "piloto/sonnet.jsonl"), lee(R / "piloto/haiku.jsonl"); c = a.index.intersection(b.index)
L.append(f"- **sonnet vs haiku (individual)**: n={len(c)} · κ {cohen_kappa_score(a.loc[c,'level'], b.loc[c,'level'], weights='quadratic'):.3f}")
(R / "piloto/INFORME.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
