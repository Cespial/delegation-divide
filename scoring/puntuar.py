"""Puntuación ADI de tareas con la rúbrica congelada. Multi-proveedor, una tarea por llamada, temperatura 0,
checkpoint por (modelo, task_id) en JSONL. Basado en AHC scripts/03_ahc_index/20_score_tasks_llm.py.

Candados (preregistro):
  --piloto N   ≤ 300 tareas, salida a scoring/salidas/piloto/ (se descarta, solo ajusta redacción).
  corrida principal exige docs/OSF_DOI.txt y que el SHA-256 de la rúbrica coincida con docs/RUBRICA_SHA256.txt.
Claves: ~/.config/adi/.env (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, OPENROUTER_API_KEY). Nunca en el repo.

Uso: .venv/bin/python -I scoring/puntuar.py --modelo claude-sonnet-5-5 --piloto 300
     .venv/bin/python -I scoring/puntuar.py --modelo claude-sonnet-5-5            # principal
     .venv/bin/python -I scoring/puntuar.py --modelo claude-haiku-5-5 --lote      # Message Batches (−50 %)
"""
import argparse, hashlib, json, os, random, sys, time
from datetime import datetime
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]
RUBRICA = RAIZ / "scoring/prompts/rubrica_v1.md"
load_dotenv(Path.home() / ".config/adi/.env")
PROVEEDOR = {"claude-": "anthropic", "gpt": "openai", "o3": "openai", "o4": "openai", "gemini": "google",
             "deepseek": "deepseek", "kimi": "kimi", "moonshot": "kimi"}
# Modelos por CLI de Claude (suscripción, sin temperatura 0): sonnet | haiku | opus
CLI = {"sonnet", "haiku", "opus"}
CAMPOS = {"level": int, "share_delegable": int, "minutes_human": int, "barrier_physical": bool,
          "barrier_accountability": bool, "barrier_trust": bool, "barrier_access": bool, "confidence": str}


def prompt_de(rubrica: str) -> str:
    return rubrica[rubrica.index("You are rating"):]


def candado(piloto: int | None):
    sha = hashlib.sha256(RUBRICA.read_bytes()).hexdigest()
    if piloto:
        if piloto > 300: sys.exit("El piloto está limitado a 300 tareas (preregistro §0).")
        return sha
    doi, ref = RAIZ / "docs/OSF_DOI.txt", RAIZ / "docs/RUBRICA_SHA256.txt"
    if not doi.exists() or not doi.read_text().strip():
        sys.exit("Corrida principal bloqueada: registre el preregistro en OSF y escriba el DOI en docs/OSF_DOI.txt.")
    if not ref.exists() or ref.read_text().strip() != sha:
        sys.exit(f"La rúbrica cambió desde el registro (SHA {sha[:12]}…). Registre la desviación o restaure la v1.")
    return sha


def cliente(modelo: str):
    if modelo in CLI:
        return "cli", None
    prov = next((v for k, v in PROVEEDOR.items() if modelo.startswith(k)), "openrouter")
    import openai
    if prov == "deepseek":   # OpenAI-compatible; caché de prefijo automática (la rúbrica fija se cobra a precio de hit)
        return prov, openai.OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    if prov == "kimi":
        return prov, openai.OpenAI(api_key=os.environ["MOONSHOT_API_KEY"], base_url="https://api.moonshot.ai/v1")
    if prov == "anthropic":
        import anthropic; return prov, anthropic.Anthropic()
    if prov == "openai":
        import openai; return prov, openai.OpenAI()
    if prov == "google":
        import openai; return prov, openai.OpenAI(api_key=os.environ["GOOGLE_API_KEY"], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    import openai; return prov, openai.OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")


def llamar(prov, cli, modelo, texto) -> str:
    if prov == "cli":
        import llm_cli  # claude -p; registra cada llamada en docs/llm-llamadas.jsonl
        return llm_cli.llamar(texto, modelo=modelo, timeout=300, reintentos=2, etiqueta="adi")
    if prov == "anthropic":
        r = cli.messages.create(model=modelo, max_tokens=300, temperature=0, messages=[{"role": "user", "content": texto}])
        return r.content[0].text
    r = cli.chat.completions.create(model=modelo, temperature=0, max_tokens=300, messages=[{"role": "user", "content": texto}])
    return r.choices[0].message.content


def validar(txt: str) -> dict:
    j = json.loads(txt[txt.index("{"): txt.rindex("}") + 1])
    out = {k: (t(j[k]) if t is not bool else (j[k] is True or str(j[k]).lower() == "true")) for k, t in CAMPOS.items()}
    if out["level"] not in (0, 1, 2, 3) or not 0 <= out["share_delegable"] <= 100: raise ValueError("fuera de rango")
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--modelo", required=True); ap.add_argument("--piloto", type=int)
    ap.add_argument("--banco", default="onet", choices=["onet", "esco"]); ap.add_argument("--pausa", type=float, default=0.1)
    ap.add_argument("--repetir", type=int, default=1, help="pasadas por tarea (test-retest); la salida lleva sufijo _rN")
    ap.add_argument("--n", type=int, help="limita a las primeras n tareas pendientes (para el piloto)")
    a = ap.parse_args(); sha = candado(a.piloto)
    sys.path.insert(0, str(RAIZ / "scoring"))
    tareas = pd.read_parquet(RAIZ / "datos/tareas_unicas.parquet")
    if a.piloto: tareas = tareas.sample(a.piloto, random_state=20261020)
    sal = RAIZ / "scoring/salidas" / ("piloto" if a.piloto else a.banco); sal.mkdir(parents=True, exist_ok=True)
    for rep in range(1, a.repetir + 1):
        out = sal / (f"{a.modelo}.jsonl" if rep == 1 else f"{a.modelo}_r{rep}.jsonl")
        correr(a, out, tareas, sha)


def correr(a, out, tareas, sha):
    hechos = {json.loads(l)["task_id"] for l in open(out) if l.strip() and "error" not in l} if out.exists() else set()
    plantilla = prompt_de(RUBRICA.read_text()); prov, cli = cliente(a.modelo)
    pend = tareas[~tareas.task_id.isin(hechos)]
    if a.n: pend = pend.head(a.n)
    print(f"{a.modelo} → {out.name}: {len(hechos)} hechas, {len(pend)} pendientes")
    with open(out, "a") as f:
        for n, t in enumerate(pend.itertuples(), 1):
            texto = plantilla.format(occupation_title=t.titulo, task_text=t.texto)
            for i in range(5):
                try:
                    crudo = llamar(prov, cli, a.modelo, texto); fila = {"task_id": int(t.task_id), **validar(crudo)}; break
                except Exception as e:
                    fila = {"task_id": int(t.task_id), "error": str(e)[:200]}
                    time.sleep(min(120, 5 * 2 ** i) if "429" in str(e) or "overloaded" in str(e).lower() else 2)
            fila.update(modelo=a.modelo, rubrica_sha=sha[:16], ts=datetime.now().isoformat(timespec="seconds"))
            f.write(json.dumps(fila) + "\n"); f.flush(); time.sleep(a.pausa)
            if n % 250 == 0: print(f"  {n}/{len(pend)}")
    print("listo", out)


if __name__ == "__main__":
    main()
