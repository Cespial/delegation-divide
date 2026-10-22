"""Receptor local temporal: guarda las imágenes que la pestaña de Midjourney envía por POST.
Uso: python receptor.py <carpeta>   → imprime un token; la pestaña lo envía en la cabecera X-Token.
Defensas: solo Origin https://www.midjourney.com, token por sesión (la cabecera propia fuerza preflight CORS),
extensiones de imagen, tope de 40 MB, nunca sobrescribe, escucha solo en 127.0.0.1."""
import sys, re, secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
DEST = Path(sys.argv[1]); DEST.mkdir(parents=True, exist_ok=True)
ORIGEN, TOKEN, TOPE = "https://www.midjourney.com", secrets.token_urlsafe(16), 40 * 1024 * 1024
EXT = (".jpeg", ".jpg", ".png", ".webp")
class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", ORIGEN)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers", "X-Token, Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
    def _no(self, cod, msg): self.send_response(cod); self._cors(); self.end_headers(); self.wfile.write(msg.encode())
    def do_OPTIONS(self):
        if self.headers.get("Origin") != ORIGEN: return self._no(403, "origen")
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        if self.headers.get("Origin") != ORIGEN or not secrets.compare_digest(self.headers.get("X-Token", ""), TOKEN): return self._no(403, "origen o token")
        n = re.sub(r"[^\w.-]", "_", self.path.strip("/"))[:80]
        largo = int(self.headers.get("content-length", 0) or 0)
        if not n.lower().endswith(EXT) or not 0 < largo <= TOPE: return self._no(400, "nombre o tamaño")
        f = DEST / n
        if f.exists(): return self._no(409, "ya existe")
        f.write_bytes(self.rfile.read(largo)); self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass
print(f"receptor en http://127.0.0.1:8765 → {DEST}  token: {TOKEN}", flush=True)
HTTPServer(("127.0.0.1", 8765), H).serve_forever()
