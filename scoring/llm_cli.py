"""Envoltorio de `claude -p` para los bloques con IA de la corrida nocturna.

- Invoca el CLI fuera de la sesión de Claude Code (`env -u CLAUDECODE`).
- Pide salida JSON del CLI y extrae el campo `result`; de ahí saca el primer bloque JSON.
- Reintenta con espera creciente; deja una línea por llamada en `docs/llm-llamadas.jsonl`
  (modelo, hash del prompt, duración, éxito) para la declaración de uso de IA del manuscrito.
- Nunca decide nada: devuelve datos para que un humano los revise.
"""
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REGISTRO = RAIZ / "scoring" / "salidas" / "llm-llamadas.jsonl"
CLI_VERSION = None


def version_cli():
    global CLI_VERSION
    if CLI_VERSION is None:
        try:
            CLI_VERSION = subprocess.run(["claude", "--version"], capture_output=True, text=True,
                                         timeout=30).stdout.strip()
        except Exception:
            CLI_VERSION = "desconocida"
    return CLI_VERSION


def _env():
    e = dict(os.environ)
    e.pop("CLAUDECODE", None)
    e.pop("CLAUDE_CODE_ENTRYPOINT", None)
    return e


def disponible():
    try:
        r = llamar("Responde exactamente la palabra OK y nada más.", modelo="sonnet",
                   timeout=120, reintentos=1, etiqueta="prueba")
        return "OK" in (r or "")
    except Exception:
        return False


class TopeAlcanzado(RuntimeError):
    pass


def _contar():
    """Tope global de llamadas por noche: NOCHE_DIR/llamadas.txt y MAX_LLAMADAS (por defecto 500)."""
    d = os.environ.get("NOCHE_DIR")
    if not d:
        return
    p = Path(d) / "llamadas.txt"
    n = int(p.read_text().strip() or 0) if p.exists() else 0
    tope = int(os.environ.get("MAX_LLAMADAS", "500"))
    if n >= tope:
        raise TopeAlcanzado(f"tope de {tope} llamadas alcanzado")
    p.write_text(str(n + 1))


LIMITE = re.compile(r"usage limit|rate.?limit|limit reached|limit will reset|too many requests|\b429\b|overloaded", re.I)
ESPERA_MAX_S = int(os.environ.get("LLM_ESPERA_MAX_S", str(24 * 3600)))


def _espera_limite(texto):
    """Segundos a esperar si el CLI reporta límite de uso; None si no es un límite.
    El CLI suele traer «Claude AI usage limit reached|<epoch>»: se espera hasta ese instante + 2 min."""
    if not texto or not LIMITE.search(texto):
        return None
    m = re.search(r"\|(\d{10})\b", texto)
    if m:
        return max(60, int(m.group(1)) - int(time.time()) + 120)
    return 15 * 60


def _anotar_espera(seg, motivo):
    d = Path(os.environ.get("NOCHE_DIR") or RAIZ / "docs")
    with open(d / "llamadas-espera.log", "a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')} espera {seg}s · {motivo[:160]}\n")


def llamar(prompt, modelo=None, timeout=600, reintentos=3, etiqueta=""):
    """Devuelve el texto de respuesta (campo `result`) o lanza RuntimeError tras agotar reintentos.
    Si el CLI reporta límite de uso, duerme hasta el restablecimiento sin gastar reintentos (hasta 24 h)."""
    _contar()
    cmd = ["claude", "-p", "--output-format", "json"]
    if modelo:
        cmd += ["--model", modelo]
    h = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    ultimo = None
    esperado = 0
    intento = 0
    while intento < reintentos:
        intento += 1
        t0 = time.time()
        crudo = ""
        try:
            p = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               timeout=timeout, env=_env())
            dur = round(time.time() - t0, 1)
            crudo = (p.stdout or "") + " " + (p.stderr or "")
            if p.returncode == 0 and p.stdout.strip():
                salida = json.loads(p.stdout)
                res = salida.get("result") if isinstance(salida, dict) else None
                es_error = isinstance(salida, dict) and salida.get("is_error")
                if res and not es_error and not (len(res) < 300 and _espera_limite(res)):
                    _registrar(etiqueta, modelo, h, dur, True, intento, salida)
                    return res
                ultimo = f"sin result o error: {p.stdout[:200]}"
            else:
                ultimo = f"rc={p.returncode} {p.stderr[:300]} {p.stdout[:200]}"
        except subprocess.TimeoutExpired:
            dur = round(time.time() - t0, 1)
            ultimo = f"timeout {timeout}s"
        except json.JSONDecodeError as e:
            dur = round(time.time() - t0, 1)
            ultimo = f"json inválido del CLI: {e}"
        _registrar(etiqueta, modelo, h, dur, False, intento, {"error": ultimo})
        seg = _espera_limite(crudo)
        if seg and esperado + seg <= ESPERA_MAX_S:
            _anotar_espera(seg, ultimo)
            time.sleep(seg)
            esperado += seg
            intento -= 1  # el límite de uso no gasta reintentos
            continue
        time.sleep(20 * intento)
    raise RuntimeError(f"claude -p falló tras {reintentos} intentos: {ultimo}")


def extraer_json(texto):
    """Primer objeto o lista JSON dentro de un texto (tolera ```json ... ```)."""
    m = re.search(r"```(?:json)?\s*(.*?)```", texto, re.S)
    cuerpo = m.group(1) if m else texto
    ini = min((i for i in (cuerpo.find("{"), cuerpo.find("[")) if i >= 0), default=-1)
    if ini < 0:
        raise ValueError("sin JSON en la respuesta")
    for fin in range(len(cuerpo), ini, -1):
        try:
            return json.loads(cuerpo[ini:fin])
        except json.JSONDecodeError:
            continue
    raise ValueError("JSON no cerrado en la respuesta")


def llamar_json(prompt, **kw):
    return extraer_json(llamar(prompt, **kw))


def _registrar(etiqueta, modelo, h, dur, ok, intento, salida):
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    fila = {"ts": dt.datetime.now().isoformat(timespec="seconds"), "etiqueta": etiqueta,
            "modelo": modelo or "default", "cli": version_cli(), "prompt_sha256_16": h,
            "duracion_s": dur, "ok": ok, "intento": intento}
    if isinstance(salida, dict):
        for k in ("model", "cost_usd", "total_cost_usd", "duration_ms", "num_turns"):
            if k in salida:
                fila[k] = salida[k]
        if isinstance(salida.get("modelUsage"), dict):
            fila["modelos_usados"] = sorted(salida["modelUsage"])
        if "error" in salida:
            fila["error"] = salida["error"]
    with open(REGISTRO, "a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    print("CLI:", version_cli())
    print("disponible:", disponible())
