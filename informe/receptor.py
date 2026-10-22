"""Receptor local temporal: guarda las imágenes que la pestaña de Midjourney envía por POST."""
import sys, re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
DEST = Path(sys.argv[1]); DEST.mkdir(parents=True, exist_ok=True)
class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "https://www.midjourney.com")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
    def do_OPTIONS(self): self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        n = re.sub(r"[^\w.-]", "_", self.path.strip("/"))[:80] or "img.bin"
        (DEST / n).write_bytes(self.rfile.read(int(self.headers.get("content-length", 0))))
        self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass
HTTPServer(("127.0.0.1", 8765), H).serve_forever()
