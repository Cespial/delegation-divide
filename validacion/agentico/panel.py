"""Adjudicación agéntica (D2): un agente con búsqueda web (Claude Opus 5.5 vía `claude -p`, distinto de los evaluadores Sonnet/Haiku)
investiga cada tarea de la muestra de validación y la califica con la misma rúbrica, citando evidencia. Es una validación NO humana
y se reporta aparte de la de Santiago. El agente no ve ninguna calificación de los modelos evaluadores.
Uso: .venv/bin/python -I validacion/agentico/panel.py --muestra validacion/santiago/muestra_300.csv [--n 2] [--particion k/K]"""
import argparse, json, os, subprocess, sys, time, hashlib
from datetime import datetime
from pathlib import Path
import pandas as pd
R = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(R / "scoring"))
import llm_cli
from puntuar import prompt_de, validar, RUBRICA

INSTR = """

## How to work (agentic adjudication)
Before rating, use web search (at most 4 searches) to check the three facts that decide the level:
(a) whether software or AI agents available in October 2026 already perform this task or its main sub-steps (product pages, documentation,
case studies); (b) whether the task requires physical presence or manipulation; (c) whether law, licensing or professional liability
requires a human to perform or sign it in typical jurisdictions. Do not search for this task's rating in any index or paper.
Then return ONLY one JSON object with the eight fields above plus "evidence": a list of at most 3 objects {"fact": "...", "url": "..."}."""

def llamar(prompt, timeout=600):
    cmd = ["claude", "-p", "--output-format", "json", "--model", "opus", "--tools", "WebSearch,WebFetch", "--allowedTools", "WebSearch,WebFetch",
           "--strict-mcp-config", "--no-session-persistence", "--system-prompt", "You are a careful labor-economics researcher. Verify facts on the web before judging."]
    t0 = time.time(); p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, env=llm_cli._env())
    d = json.loads(p.stdout); llm_cli._registrar("panel_agentico", "opus", hashlib.sha256(prompt.encode()).hexdigest()[:16], round(time.time() - t0, 1), not d.get("is_error"), 1, d)
    return d["result"], d.get("total_cost_usd", 0)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--muestra", required=True); ap.add_argument("--n", type=int); ap.add_argument("--particion", default="0/1")
    a = ap.parse_args(); k, K = map(int, a.particion.split("/"))
    t = pd.read_parquet(R / "datos/tareas_unicas.parquet"); m = pd.read_csv(R / a.muestra)
    t = t[t.task_id.isin(m.task_id) & (t.task_id % K == k)]
    out = R / "validacion/agentico/salidas" / (f"panel.p{k}.jsonl" if K > 1 else "panel.jsonl"); out.parent.mkdir(parents=True, exist_ok=True)
    hechos = {json.loads(l)["task_id"] for l in open(out) if "error" not in l} if out.exists() else set()
    t = t[~t.task_id.isin(hechos)]; t = t.head(a.n) if a.n else t
    base = prompt_de(RUBRICA.read_text()); print(f"{len(t)} pendientes → {out.name}")
    with open(out, "a") as f:
        for r in t.itertuples():
            fila = {"task_id": int(r.task_id)}
            for i in range(3):
                try:
                    txt, costo = llamar(base.format(occupation_title=r.titulo, task_text=r.texto) + INSTR)
                    j = json.loads(txt[txt.index("{"): txt.rindex("}") + 1])
                    fila = {"task_id": int(r.task_id), **validar(json.dumps(j)), "evidence": j.get("evidence", [])[:3], "costo_usd": costo}; break
                except Exception as e:
                    fila = {"task_id": int(r.task_id), "error": str(e)[:200]}; time.sleep(10)
            fila.update(modelo="opus+web", ts=datetime.now().isoformat(timespec="seconds")); f.write(json.dumps(fila, ensure_ascii=False) + "\n"); f.flush()
    print("listo", out)

if __name__ == "__main__":
    main()
