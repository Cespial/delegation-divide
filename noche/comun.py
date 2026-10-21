"""Utilidades compartidas de la captura nocturna: descarga con reintentos, SHA-256, manifiesto, log."""
import hashlib, json, logging, os, shutil, sys, time
from datetime import datetime
from pathlib import Path
import requests

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
LOGS = RAIZ / "logs"
MANIFIESTO = DATOS / "MANIFIESTO.jsonl"
UA = {"User-Agent": "ADI-captura/0.1 (+https://github.com/Cespial/delegation-divide; cespinal@unal.edu.co)"}


def log(nombre: str) -> logging.Logger:
    LOGS.mkdir(exist_ok=True)
    lg = logging.getLogger(nombre)
    if not lg.handlers:
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S")
        for h in (logging.StreamHandler(sys.stdout), logging.FileHandler(LOGS / f"{nombre}.log")):
            h.setFormatter(fmt); lg.addHandler(h)
        lg.setLevel(logging.INFO)
    return lg


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def registrar(p: Path, fuente: str, url: str = "", nota: str = "", ok: bool = True):
    """Una línea por archivo capturado: procedencia para el Apéndice B del paper."""
    fila = {"archivo": str(p.relative_to(RAIZ)) if p.exists() else str(p), "fuente": fuente, "url": url,
            "bytes": p.stat().st_size if p.exists() else 0, "sha256": sha256(p) if p.exists() and p.is_file() else "",
            "capturado": datetime.now().isoformat(timespec="seconds"), "ok": ok, "nota": nota}
    with open(MANIFIESTO, "a") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")
    return fila


def descargar(url: str, destino: Path, fuente: str, lg, reintentos: int = 4, timeout: int = 600, minimo: int = 200, **kw) -> bool:
    """GET con reintentos exponenciales; omite si ya existe; registra en el manifiesto."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size >= minimo:
        lg.info(f"ya existe {destino.name} ({destino.stat().st_size:,} B)"); return True
    for i in range(reintentos):
        try:
            with requests.get(url, headers=UA, stream=True, timeout=timeout, **kw) as r:
                r.raise_for_status()
                tmp = destino.with_suffix(destino.suffix + ".parcial")
                with open(tmp, "wb") as f:
                    for ch in r.iter_content(1 << 20):
                        f.write(ch)
                if tmp.stat().st_size < minimo:
                    raise IOError(f"respuesta de {tmp.stat().st_size} B (< {minimo})")
                tmp.rename(destino)
            registrar(destino, fuente, url); lg.info(f"OK {destino.name} ({destino.stat().st_size:,} B)")
            return True
        except Exception as e:
            lg.warning(f"intento {i+1}/{reintentos} {url} → {e}"); time.sleep(2 ** (i + 1) * 5)
    registrar(destino, fuente, url, nota="FALLÓ", ok=False); lg.error(f"FALLÓ {url}")
    return False


def copiar(origen: Path, destino: Path, fuente: str, lg) -> bool:
    """Copia desde Drive (hidrata el archivo al leerlo) y registra."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 0:
        lg.info(f"ya existe {destino.name}"); return True
    try:
        shutil.copyfile(origen, destino)
        registrar(destino, fuente, f"file://{origen}"); lg.info(f"copiado {destino.name} ({destino.stat().st_size:,} B)")
        return True
    except Exception as e:
        lg.error(f"no se pudo copiar {origen}: {e}"); registrar(destino, fuente, str(origen), nota=f"FALLÓ: {e}", ok=False)
        return False


AHC = Path.home() / "Library/CloudStorage/GoogleDrive-cristianjosue07@gmail.com/Mi unidad/Proyectos/Research/Cognitive Factor Economics (CFE)/augmented_human_capital"
