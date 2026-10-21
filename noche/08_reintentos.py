"""Paso 8 (segunda pasada): reintenta con curl reanudable (-C -) cada descarga que quedó fallida en el manifiesto.
Útil para servidores que cortan archivos grandes (INEGI, IBGE, INEI)."""
import sys, json, subprocess; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
lg = log("08_reintentos")
ultimo = {}
for l in open(MANIFIESTO):
    if l.strip(): r = json.loads(l); ultimo[r["archivo"]] = r
fallos = [r for r in ultimo.values() if not r["ok"] and r["url"].startswith("http")]
lg.info(f"{len(fallos)} descargas fallidas para reintentar")
for r in fallos:
    p = RAIZ / r["archivo"]; p.parent.mkdir(parents=True, exist_ok=True); tmp = p.with_suffix(p.suffix + ".parcial")
    cmd = ["curl", "-L", "-C", "-", "--retry", "8", "--retry-all-errors", "--retry-delay", "20", "--max-time", "5400",
           "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)", "-sS", "-o", str(tmp), r["url"]]
    res = subprocess.run(cmd, capture_output=True, text=True)
    ok = res.returncode == 0 and tmp.exists() and tmp.stat().st_size > 10_000 and not tmp.read_bytes()[:200].lower().lstrip().startswith(b"<")
    if ok:
        tmp.rename(p); registrar(p, r["fuente"], r["url"], nota="segunda pasada (curl -C -)"); lg.info(f"OK {p.name} ({p.stat().st_size:,} B)")
    else:
        lg.error(f"sigue fallando {r['url']}: código {res.returncode} {res.stderr[:120]}")
