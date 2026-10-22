#!/usr/bin/env python3
"""informe/informe.html (Paged.js) → out/delegation-divide-report-2026.pdf con Playwright + Chrome; espera el fin de la paginación,
reporta errores de consola y páginas desbordadas, fija metadatos y genera PNG de QA por página.
Adaptado de ~/tensor-propuestas/limnigrafo/render.py. Uso: python3 informe/render.py  (Python con playwright)."""
import os, sys, time, glob, subprocess, pathlib, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
INF = pathlib.Path(__file__).resolve().parent; os.chdir(INF)
PDF = "out/delegation-divide-report-2026.pdf"; os.makedirs("out/qa", exist_ok=True)
for f in glob.glob("out/qa/page-*.png"): os.remove(f)
msgs = []
# Paged.js lee el CSS por XHR: file:// lo bloquea (CORS). Se sirve la carpeta por HTTP local en un puerto libre.
class _S(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(_S, directory=str(INF))); PUERTO = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
DESBORDE = """() => [...document.querySelectorAll('.pagedjs_page')].map((p, i) => {
  const area = p.querySelector('.pagedjs_page_content'); if (!area) return null;
  const a = area.getBoundingClientRect(); let maxR = 0, maxB = 0, quien = '';
  area.querySelectorAll('*').forEach(e => { if ((e.closest('svg') && e.tagName !== 'svg') || e.closest('.motivo')) return; const r = e.getBoundingClientRect();
    if (r.width && r.height) { if (r.right > maxR) { maxR = r.right; quien = e.tagName + '.' + (e.className && e.className.baseVal === undefined ? e.className : ''); } maxB = Math.max(maxB, r.bottom); } });
  return {n: i + 1, der: Math.round(maxR - a.right), abajo: Math.round(maxB - a.bottom), quien: quien.slice(0, 40)};
}).filter(x => x && ((x.der > 2 && x.der < 400) || (x.abajo > 2 && x.abajo < 400)))"""
# huecos: páginas con más de 18 % del área de texto vacía al pie, y qué abre la página siguiente (para ubicar figuras y tablas a mano).
HUECOS = """() => { const P = [...document.querySelectorAll('.pagedjs_page')]; return P.map((p, i) => {
  const area = p.querySelector('.pagedjs_page_content'); if (!area || !area.querySelector('.cap, .cap-libre, .anexo')) return null;
  const a = area.getBoundingClientRect(); let maxB = a.top;
  area.querySelectorAll('p, li, h2, h3, figure, .fig, .tabla, .lat, .mensajes, pre, dl, .box, .tarjetas, table').forEach(e => { const r = e.getBoundingClientRect(); if (r.height) maxB = Math.max(maxB, r.bottom); });
  const sig = P[i + 1] && [...P[i + 1].querySelectorAll('.pagedjs_page_content section > *')].find(e => e.getBoundingClientRect().height > 0);
  const nombre = !sig ? '' : sig.matches('section.cap, section.cap-libre, section.anexo') ? '(nueva sección)' : (sig.id || sig.getAttribute('class') || sig.tagName) + ' «' + sig.textContent.trim().slice(0, 24) + '»';
  return {n: i + 1, hueco: Math.round(100 * (a.bottom - maxB) / a.height), sig: nombre};
}).filter(x => x && x.hueco > 18); }"""
# marcadores del PDF: cada elemento con data-outline (título limpio y nivel puestos por la plantilla), en orden y con su página
MARCADORES = """() => { const P = [...document.querySelectorAll('.pagedjs_page')], vistos = new Set();
  return [...document.querySelectorAll('[data-outline]:not([data-split-from])')].map(e => ({t: e.dataset.outline, n: +e.dataset.nivel, p: P.indexOf(e.closest('.pagedjs_page'))}))
    .filter(m => m.p >= 0 && !vistos.has(m.t) && vistos.add(m.t)); }"""  # los fragmentos que Paged.js parte heredan el atributo: cuenta solo el primero
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome"); pg = br.new_page()
    pg.on("console", lambda m: msgs.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    pg.on("response", lambda r: msgs.append(f"404: {r.url}") if r.status >= 400 else None)
    pg.on("pageerror", lambda e: msgs.append(f"pageerror: {e}"))
    pg.goto(f"http://127.0.0.1:{PUERTO}/informe.html")
    last, stable, n = -1, 0, 0
    for i in range(360):
        time.sleep(0.5); n = pg.evaluate("document.querySelectorAll('.pagedjs_page').length"); done = pg.evaluate("!!window.__pagedDone")
        stable = stable + 1 if n == last else 0; last = n
        if (done or stable >= 10) and n > 0: break
    pg.wait_for_timeout(800)
    malas = pg.evaluate(DESBORDE); huecos = pg.evaluate(HUECOS); marcadores = pg.evaluate(MARCADORES)
    # sin etiquetar (tagged): limpiadoc lee el árbol de estructura como rastro; los marcadores se arman abajo con pypdf
    pg.pdf(path=PDF, prefer_css_page_size=True, print_background=True); br.close()
print("páginas:", n)
print("\n".join(msgs[:20]) if msgs else "consola: sin errores")
print("desbordes:", malas if malas else "ninguno")
print("huecos >18 %:", " · ".join(f"p{h['n']} {h['hueco']}% → {h['sig']}" for h in huecos))
from pypdf import PdfReader, PdfWriter
w = PdfWriter(clone_from=PDF)
import json
est = pathlib.Path(__file__).resolve().parents[1] / "release/zenodo_informe.estado.json"
doi = json.loads(est.read_text())["doi"] if est.exists() and not json.loads(est.read_text()).get("sandbox") else None  # DOI propio del informe
w.add_metadata({"/Title": "The Delegation Divide: An Open Index of AI-Agent Delegability across Occupations and Countries",
                "/Author": "Cristian Espinal Maya; Santiago Jiménez Londoño",
                "/Subject": "ADI Report 2026.1 · Balam Labs" + (f" · doi:{doi}" if doi else ""),
                "/Keywords": "AI agents, delegation, labour markets, ISCO-08, ILOSTAT, ADI" + (f", doi:{doi}" if doi else "") + ", data doi:10.5281/zenodo.23552918",
                "/Creator": "", "/Producer": ""})
padres = {}
for m in marcadores:
    padres[m["n"]] = w.add_outline_item(m["t"], m["p"], parent=padres.get(m["n"] - 1) if m["n"] else None)
w.page_mode = "/UseOutlines"
w.write(PDF); srv.shutdown()
print("marcadores:", len(marcadores))
subprocess.run(["pdftoppm", "-r", "80", PDF, "out/qa/page", "-png"])
print("png:", len(glob.glob("out/qa/page-*.png")))
