"""Informe de la segunda noche → docs/noche/2026-10-21/INFORME-NOCHE2.md: estado de cada paso (logs), coberturas (países,
empleo, CIUO GEIH, comparadores, AEI), piloto (filas, % JSON válido, duración media, test-retest y acuerdo sonnet–haiku),
QA del PDF y pendientes. Solo lee; no recalcula el índice."""
import sys, json, re, subprocess; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
import numpy as np, pandas as pd
DIA = "2026-10-21"; out = RAIZ / "docs/noche" / DIA; out.mkdir(parents=True, exist_ok=True)
L = [f"# Informe de la segunda noche — {DIA}", "", f"Generado {datetime.now().isoformat(timespec='minutes')} por `noche/informe2.py`.", ""]
cola = lambda p, n=1: [l.rstrip() for l in open(p, errors="ignore").readlines()[-n:]] if p.exists() else []
errores = lambda p: [l.strip() for l in open(p, errors="ignore") if " ERROR " in l or "Traceback" in l] if p.exists() else []

# 1. pasos
L += ["## 1. Pasos", "", "| Paso | Estado | Detalle |", "|---|---|---|"]
pasos = RAIZ / "logs/noche2_pasos.txt"
for l in (open(pasos).read().splitlines() if pasos.exists() else []):
    m = dict(kv.split("=", 1) for kv in l.split()[1:]); L.append(f"| {l.split()[0]} | {'OK' if m.get('rc') == '0' else 'FALLO rc=' + m.get('rc', '?')} | {m.get('segundos', '?')} s, fin {m.get('fin', '')} |")
for nombre in ("01_onet", "02_ilostat", "02b_ilostat_oc2", "03_esco", "04_comparadores", "05_worldbank", "06_microdatos", "13_geih", "esco_isco",
               "comparadores_isco", "14_pnadc", "15_enoe", "20_indice", "21_figuras", "22_tablas"):
    p = LOGS / f"{nombre}.log"
    if not p.exists(): L.append(f"| {nombre} | sin log | |"); continue
    e = errores(p); ult = (cola(p) or [""])[0][:110].replace("|", "/")
    L.append(f"| {nombre} | {'con errores (' + str(len(e)) + ')' if e else 'OK'} | {ult} |")
corr = sorted((RAIZ / "salidas/corridas").glob("*/")) if (RAIZ / "salidas/corridas").exists() else []
rep = LOGS / "reproducir.log"
if rep.exists(): L += ["", "Salida de `articulo/reproducir.sh`:", "", "```"] + cola(rep, 20) + ["```"]

# 2. coberturas
CL = {}
if (RAIZ / "salidas/claims.jsonl").exists():
    for l in open(RAIZ / "salidas/claims.jsonl"):
        if l.strip(): d = json.loads(l); CL[d["id"]] = d
g = lambda i, f="{:,.0f}": (f.format(CL[i]["valor"]) if isinstance(CL[i]["valor"], (int, float)) else str(CL[i]["valor"])) if i in CL else "—"
sint = any(d.get("sintetico") for d in CL.values())
L += ["", "## 2. Coberturas", "", f"- Índice: **{'SINTÉTICO (prueba del pipeline; no son resultados)' if sint else 'REAL'}**",
      f"- Países en el atlas: **{g('cobertura.paises')}** (2 díg. {g('cobertura.paises.2d')}, 1 díg. {g('cobertura.paises.1d')}); empleo cubierto **{g('cobertura.empleo_millones', '{:,.1f}')} M**",
      f"- ISCO-08 4 díg. con tareas: **{g('cobertura.isco')}** de 436 ({g('cobertura.isco.imputados')} imputados); con empleo GEIH (pesos dentro de grupo): **{g('cobertura.geih.isco')}**",
      f"- Tareas puntuadas con consenso: {g('cobertura.tareas.puntuadas')} de {g('cobertura.tareas')}"]
gr = DATOS / "microdatos/geih_ciuo_resumen.csv"
if gr.exists(): r = pd.read_csv(gr); L.append(f"- GEIH: {len(r)} códigos CIUO-08 A.C. con empleo; empleo mensual medio {r.empleo.sum() / 1e6:.1f} M")
for nom, f in (("ENOE (México, ISCO 1 díg. por tabla manual SINCO)", "enoe_isco1_resumen.csv"), ("PNADC (Brasil, COD 4 díg.)", "pnadc_isco_resumen.csv")):
    p = DATOS / "microdatos" / f
    L.append(f"- {nom}: " + (f"{len(pd.read_csv(p))} grupos, empleo {pd.read_csv(p).empleo.sum() / 1e6:.1f} M" if p.exists() else "no disponible"))
for p, pats in ((LOGS / "comparadores_isco.log", ("Eloundou tareas", "task_penetration", "cobertura ISCO", "AEI por país", "AEI: ninguna")), (LOGS / "esco_isco.log", ("ESCO:",))):
    lineas = open(p, errors="ignore").read().splitlines() if p.exists() else []
    for pat in pats:                                                  # el log acumula corridas: solo la última línea de cada tipo
        hits = [l for l in lineas if pat in l]
        if hits: L.append(f"- `{hits[-1][9:].strip()[:400]}`")
L.append(f"- H3 correlaciones (ISCO 4 díg.): Eloundou r={g('h3.r.eloundou', '{:.2f}')}, Felten r={g('h3.r.felten', '{:.2f}')} · H2 países con uso AEI: {g('h2.n')}")

# 3. piloto
P = RAIZ / "scoring/salidas/piloto"
L += ["", "## 3. Piloto", ""]
arch = sorted(P.glob("*.jsonl")) if P.exists() else []
if not arch: L.append("Sin `scoring/salidas/piloto/*.jsonl`.")
else:
    lla = [json.loads(l) for l in open(RAIZ / "scoring/salidas/llm-llamadas.jsonl") if l.strip()] if (RAIZ / "scoring/salidas/llm-llamadas.jsonl").exists() else []
    lla = pd.DataFrame(lla)
    def leer(p):
        d = pd.DataFrame([json.loads(l) for l in open(p) if l.strip()])
        if "error" not in d: d["error"] = np.nan
        return d
    D = {p.stem: leer(p) for p in arch}
    L += ["| Archivo | filas | válidas | llamadas (registro) | % JSON válido | duración media (s) |", "|---|---|---|---|---|---|"]
    for k, d in D.items():
        mod = k.split("_r")[0]; ok = int(d.error.isna().sum())
        ll = lla[(lla.get("etiqueta") == "adi") & (lla.get("modelo") == mod)] if len(lla) else lla
        n_ll = len(ll); dur = ll.duracion_s.mean() if n_ll and "duracion_s" in ll else np.nan
        L.append(f"| {k} | {len(d)} | {ok} | {n_ll} | {100 * ok / n_ll:.1f} % | {dur:.1f} |" if n_ll else f"| {k} | {len(d)} | {ok} | 0 | — | — |")
    L.append("\n% JSON válido = filas válidas / llamadas registradas con etiqueta `adi` para ese modelo (incluye reintentos y pasadas de retest).")
    def par(a, b, nombre):
        x = D[a][D[a].error.isna()].drop_duplicates("task_id", keep="last").set_index("task_id").level
        y = D[b][D[b].error.isna()].drop_duplicates("task_id", keep="last").set_index("task_id").level
        c = x.index.intersection(y.index)
        if not len(c): return f"- {nombre}: sin tareas comunes"
        dx, dy = x[c].astype(int).values, y[c].astype(int).values
        O = np.zeros((4, 4)); np.add.at(O, (dx, dy), 1); W = (np.subtract.outer(np.arange(4), np.arange(4)) ** 2) / 9; E = np.outer(O.sum(1), O.sum(0)) / O.sum()
        k = 1 - (W * O).sum() / (W * E).sum() if (W * E).sum() > 0 else float("nan")
        return f"- {nombre}: {len(c)} tareas comunes · exacto {100 * np.mean(dx == dy):.1f} % · ±1 {100 * np.mean(abs(dx - dy) <= 1):.1f} % · κ cuadrático {k:.2f}"
    L.append("")
    L.append(par("sonnet", "sonnet_r2", "Test-retest sonnet") if {"sonnet", "sonnet_r2"} <= set(D) else "- Test-retest sonnet: falta sonnet.jsonl o sonnet_r2.jsonl")
    L.append(par("sonnet", "haiku", "Acuerdo sonnet–haiku") if {"sonnet", "haiku"} <= set(D) else "- Acuerdo sonnet–haiku: falta haiku.jsonl")
    if "sonnet" in D:
        s = D["sonnet"][D["sonnet"].error.isna()]
        if len(s): L.append(f"- Distribución de niveles (sonnet): " + ", ".join(f"L{k} {v:.0%}" for k, v in s.level.value_counts(normalize=True).sort_index().items()))

# 4. QA del PDF
pdf = RAIZ / "articulo/main.pdf"
L += ["", "## 4. QA del PDF", ""]
if pdf.exists():
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    pags = re.search(r"Pages:\s+(\d+)", info); L.append(f"- `articulo/main.pdf`: {pags.group(1) if pags else '?'} páginas; marca de agua sintética: {'sí' if sint else 'no'}")
    q = subprocess.run([sys.executable, "-I", str(RAIZ / "qa/texto.py")], capture_output=True, text=True, cwd=RAIZ).stdout.splitlines()
    L += [f"- {q[0]}" if q else "- qa/texto.py sin salida"] + [f"- {l}" for l in q if l.startswith(("errores por origen", "QA texto"))]
    L += ["", "<details><summary>Errores de qa/texto.py</summary>", "", "```"] + [l for l in q if l.startswith("ERROR")][:150] + ["```", "</details>"]
else:
    L.append("- No hay `articulo/main.pdf`.")

# 5. pendientes
pend = []
if sint: pend.append("El índice es SINTÉTICO: falta la corrida principal (requiere docs/OSF_DOI.txt) y `MODO=\"--entrada scoring/salidas/main\"` en reproducir.sh.")
if not (DATOS / "microdatos/pnadc_isco_resumen.csv").exists(): pend.append("PNADC: los ZIP siguen incompletos (.parcial); reintentar descarga y correr analisis/microdatos_pnadc.py.")
if not (DATOS / "esco/skills.jsonl").exists(): pend.append("ESCO skills.jsonl no existe aún: esco_isco.py usa los títulos enlazados desde ocupaciones.")
if not (RAIZ / "validacion/respuestas").exists(): pend.append("Validación humana: faltan validacion/respuestas/*.xlsx (α y κ humanos salen como «--»).")
if CL.get("robustez.esco.h1.pendiente", {}).get("valor") == "--": pend.append("Robustez ESCO (robustez.esco.h1.pendiente): requiere puntuar el banco de skills ESCO.")
pend += ["Validar la decisión de pesos 4 díg. GEIH para todos los países (docs/DESVIACIONES.md).",
         "Corregir en articulo/referencias.bib los comentarios % dentro de entradas (BibTeX los reporta como errores) y citar o quitar entradas sin citar.",
         "Revisar los números a mano que qa/texto.py marca en las secciones del agente de redacción."]
L += ["", "## 5. Pendientes", ""] + [f"- [ ] {p}" for p in pend]
(out / "INFORME-NOCHE2.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
