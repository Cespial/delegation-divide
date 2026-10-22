"""Carga y formato de cifras, compartido por articulo/generar_cifras.py (LaTeX) e informe/cifras.py (HTML).
Un solo formateador: el paper y el informe imprimen los mismos números. Movido desde generar_cifras.py sin cambios de lógica."""
import re, json, pathlib, math
R = pathlib.Path(__file__).resolve().parents[1]
CL = {}
DISENO = R / "salidas_diseno/claims_diseno.jsonl"
if not DISENO.exists(): print("aviso: falta salidas_diseno/claims_diseno.jsonl (correr analisis/claims_diseno.py); los \\cifra{diseno.*} saldrán como ??")
for ruta in (DISENO, R / "salidas/claims.jsonl"):
    if not ruta.exists(): continue
    for l in open(ruta):
        if l.strip(): d = json.loads(l); CL[d["id"]] = d
# robustez ESCO (analisis/robustez_esco.py): se añade después y nunca pisa un id ya emitido por indice.py
ESCO = R / "salidas_robustez/claims_esco.jsonl"
if ESCO.exists():
    for l in open(ESCO):
        if l.strip() and (d := json.loads(l))["id"] not in CL: CL[d["id"]] = d
# gradientes GEIH de Colombia (analisis/gradientes_geih.py, exploratorio): igual, sin pisar
GEIH = R / "salidas_microdatos/claims_geih.jsonl"
if GEIH.exists():
    for l in open(GEIH):
        if l.strip() and (d := json.loads(l))["id"] not in CL: CL[d["id"]] = d
SINT = any(d.get("sintetico") for d in CL.values())
UNO = ("pct", "l2", "l3", "share", "lo", "hi", "minutos", "millones")


def fmt(i, v, absoluto=False):
    if isinstance(v, str): return v
    if isinstance(v, bool): v = int(v)
    if absoluto: v = abs(v)
    partes = i.split("."); u = partes[-1]
    if u == "p" or re.fullmatch(r"p\d?", u) or u.endswith("_p"):
        s = "$<$0.001" if v < 0.001 else f"{v:.3f}"; return s
    if partes[0] in ("n", "cobertura") and float(v).is_integer() or (isinstance(v, int) and u not in UNO): s = f"{int(v):,}"
    elif u in UNO or partes[0] in ("titular", "pais", "gg", "tareas") or u.endswith("pct") or "empleo" in u: s = f"{v:,.1f}"
    elif u in ("r", "rho", "kappa", "alpha", "r2", "se", "b1", "b2") or partes[0] in ("h3", "agree", "h2") or u.startswith(("r_", "kappa")): s = f"{v:.2f}"
    else: s = f"{v:.2f}"
    return s.replace("-", "$-$") if not absoluto else s




def fmt_html(i, v, absoluto=False):
    """fmt() sin marcado LaTeX, para el informe HTML (signo menos tipográfico, < literal)."""
    return fmt(i, v, absoluto).replace("$<$", "<").replace("$-$", "\u2212")


def pval_html(v):
    return "p\u00a0<\u00a00.001" if v < 0.001 else f"p\u00a0=\u00a0{v:.3f}"
