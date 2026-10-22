"""claims (salidas/claims.jsonl + diseño + robustez ESCO) → informe/cifras.json, con el mismo formateador del paper
(analisis/formato_cifras.py). Cada id trae: txt (valor formateado), abs (valor absoluto), p («p = …» si es p-valor), v (crudo).
Uso: .venv/bin/python -I informe/cifras.py"""
import sys, json, math, re, pathlib
R = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R / "analisis"))
from formato_cifras import CL, SINT, fmt_html, pval_html
out = {}
for i, d in sorted(CL.items()):
    v = d["valor"]
    if isinstance(v, float) and not math.isfinite(v): v = "--"
    e = {"txt": fmt_html(i, v), "v": v}
    if not isinstance(v, str):
        e["abs"] = fmt_html(i, v, True)
        u = i.split(".")[-1]
        if u == "p" or re.fullmatch(r"p\d?", u): e["p"] = pval_html(v)
    out[i] = e
(R / "informe/cifras.json").write_text(json.dumps({"sintetico": SINT, "cifras": out}, ensure_ascii=False, indent=1))
print(f"{len(out)} cifras → informe/cifras.json{' (SINTÉTICAS)' if SINT else ''}")
