"""Verifica el informe contra la fuente de verdad, sin pasar por cifras.json:
1) cada <span data-cifra> de informe.html imprime exactamente fmt_html(valor) leído ahora de los claims (detecta cifras.json viejo);
2) el texto del PDF contiene las cifras titulares; 3) todas las fuentes del PDF están embebidas;
4) el perfil de Colombia (Tabla 5.2, Figura 5.3) coincide con perfil.calcular() rehecho desde la tabla publicada.
Uso: .venv/bin/python -I informe/verificar.py"""
import re, sys, json, subprocess, pathlib, html as H
INF = pathlib.Path(__file__).resolve().parent; sys.path[:0] = [str(INF.parent / "analisis"), str(INF)]
from formato_cifras import CL, fmt_html, pval_html
h = (INF / "informe.html").read_text(); malas = []
spans = re.findall(r'<span class="cf" data-cifra="([^"]+)">(.*?)</span>', h)
for i, t in spans:
    v = CL[i]["valor"]; t = H.unescape(t)
    ok = {fmt_html(i, v)} | ({fmt_html(i, v, True), pval_html(v)} if not isinstance(v, str) else set())
    if t not in ok: malas.append((i, t, sorted(ok)))
print(f"1) {len(spans)} cifras en el HTML; {len(malas)} distintas de los claims" + (f": {malas[:5]}" if malas else ""))
pdf = INF / "out/delegation-divide-report-2026.pdf"
txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
claves = ["titular.global.l2", "titular.global.l3", "titular.ingreso.bajo.l2", "titular.ingreso.alto.l2", "h1.pendiente", "agree.kappa.humano.modelo", "cobertura.paises"]
faltan = [k for k in claves if fmt_html(k, CL[k]["valor"]) not in txt]
print(f"2) titulares en el PDF: {len(claves) - len(faltan)}/{len(claves)}" + (f"; faltan {faltan}" if faltan else ""))
f = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
no_emb = [l for l in f if l.split()[-5] != "yes"] if f else []
print(f"3) {len(f)} fuentes; no embebidas: {len(no_emb)}" + (f": {no_emb}" if no_emb else ""))
# 4) perfil de Colombia: se recalcula desde salidas/indice_pais_detalle.csv y cada valor de la Tabla 5.2 y de los hallazgos debe estar en el HTML
import perfil as PF
P = PF.calcular(); viejo = json.load(open(INF / "perfil.json")) != json.loads(json.dumps({k: v for k, v in P.items() if k != "barras"}))
m = re.search(r'<div class="perfil.*?</figure>', h, re.S); bloque = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", m[0]))) if m else ""
esperados = [P["hallazgo"], P["hallazgo_fig"]] + [f[c] for _, filas in P["grupos"] for f in filas for c in ("col", "puesto", "mejor", "region", "alto", "mundo")]
ausentes = [e for e in esperados if e not in bloque]
print(f"4) perfil: {len(esperados) - len(ausentes)}/{len(esperados)} valores recalculados presentes" + ("; perfil.json desactualizado" if viejo else "")
      + (f"; ausentes {ausentes[:4]}" if ausentes else ""))
sys.exit(1 if malas or faltan or no_emb or ausentes or viejo else 0)
