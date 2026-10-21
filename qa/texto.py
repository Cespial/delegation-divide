"""QA del artículo (adaptado del paper del sismo): (a) ningún número de resultado a mano fuera de \\cifra (salvo años, semillas,
L0–L3/H1–H4 y parámetros de diseño permitidos); (b) cero ??id de cifras faltantes en el PDF; (c) cero citas o referencias
indefinidas en main.log; (d) toda cita tiene entrada en referencias.bib y toda entrada se cita. Informa también qué archivo
origina cada error (las secciones del agente de redacción se reportan, no se corrigen aquí). Sale con 1 si hay errores."""
import re, pathlib, sys, subprocess
R = pathlib.Path(__file__).resolve().parents[1]; A = R / "articulo"
err = []
tex = {p.name: p.read_text() for p in sorted((A / "secciones").glob("*.tex"))}
m = (A / "main.tex").read_text(); tex["main.tex"] = m[m.index(r"\begin{document}"):]
# (a) números a mano. Permitidos: diseño del preregistro y del artículo (no son resultados)
PERMIT = {"18,796", "433", "436", "1,500", "0.60", "1,000", "300", "20",
          "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "95", "2.5", "97.5", "0.05", "0.40", "0.80", "0.03", "4,800", "60", "30.2"}
# Hechos de las fuentes y de las clasificaciones (no son resultados; los conteos derivados de datos van por \cifra{diseno.*},
# generados por analisis/claims_diseno.py en salidas_diseno/claims_diseno.jsonl):
PERMIT |= {"0110", "0210", "0310",                       # ISCO-08 fuerzas armadas, excluidos (ILO 2012, ISCO-08 vol. 1)
           "2131", "3259", "2519", "2529",               # ISCO-08 de destino de los rescates SOC (IBS soc10_isco08.dta), B_crosswalk
           "3413", "3511", "4213", "7133", "8155", "8159", "9613",  # ISCO-08 imputados (datos/construir_crosswalk.py), B_crosswalk
           "436",                                        # grupos unitarios de ISCO-08 (ILO 2012)
           "1.2", "28",                                  # ESCO versión 1.2, disponible en 28 lenguas (esco.ec.europa.eu)
           "3166", "4.0",                                # norma ISO 3166-1 alfa-3; licencia CC BY 4.0
           "50", "52",                                   # umbral de 50 % de Eloundou et al. (2024); 52 habilidades O*NET de Felten et al. (2021)
           "702", "70",                                  # Frey y Osborne (2017): 702 ocupaciones, 70 etiquetadas a mano
           "888,000",                                    # Lee et al. (2026): archivos de habilidades de agentes en GitHub
           "100",                                        # escala 0–100 de share_delegable (rúbrica), denominador de ADIs
           "5.5",                                        # versión de Claude Sonnet 5.5 y Claude Haiku 5.5 (docs/MODELOS.md)
           "0.80"}                                       # umbral preregistrado de κ para aceptar lotes (docs/MODELOS.md)
for nombre, t in tex.items():
    t2 = re.sub(r"(?m)(?<!\\)%.*$", "", t)
    t2 = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", "", t2, flags=re.S)
    t2 = re.sub(r"\\(cifra|cifraabs|cifraopc|pval)\{[^}]*\}", "", t2)
    t2 = re.sub(r"\\(ref|label|cite[pt]?|citeauthor|citeyear|includegraphics|input|eqref|url|href|texttt|SetWatermark\w*)(\[[^\]]*\])?\{[^}]*\}", "", t2)
    t2 = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", t2); t2 = re.sub(r"\$[^$]*\$", "", t2)
    t2 = re.sub(r"\b\d{2}-\d{4}(\.\d{2})?\b", "", t2)                                            # códigos SOC / O*NET-SOC (15-1299.04)
    t2 = re.sub(r"\b\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December)\b", "", t2)  # fechas «21 October»
    t2 = re.sub(r"\b2026102\d\b", "", t2); t2 = re.sub(r"\b(19|20)\d\d\b", "", t2)
    t2 = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", t2); t2 = re.sub(r"\b[0-9a-f]{16,}\b", "", t2)       # fechas ISO y hashes
    for x in re.finditer(r"(?<![\w.\-/])(\d[\d,]*\.?\d*)(?![\w/])", t2):
        if x.group(1).rstrip(".,") not in PERMIT:
            err.append(f"{nombre}: número a mano «{x.group(1)}» … {t2[max(0, x.start() - 40):x.end() + 20].strip()!r}")
# (b) y (c): log y PDF
log = (A / "main.log").read_text(errors="ignore") if (A / "main.log").exists() else ""
if not log: err.append("main.log no existe: compile antes (latexmk)")
for l in log.splitlines():
    if "Warning" in l and ("undefined" in l or "Citation `" in l or "Reference `" in l): err.append("log: " + l.strip())
pdftxt = ""
if (A / "main.pdf").exists():
    try: pdftxt = subprocess.run(["pdftotext", str(A / "main.pdf"), "-"], capture_output=True, text=True).stdout
    except Exception: pass
else: err.append("main.pdf no existe")
for x in sorted(set(re.findall(r"\?\?[\w.\-]+", pdftxt))): err.append(f"PDF: cifra faltante {x}")
if "??" in pdftxt and not re.search(r"\?\?[\w.\-]+", pdftxt): err.append(f"PDF contiene ?? ({pdftxt.count('??')} veces)")
# (d) citas vs bib
bib = set(re.findall(r"@\w+\{([^,\s]+),", (A / "referencias.bib").read_text()))
citadas = set(k.strip() for t in tex.values() for g in re.findall(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", t) for k in g.split(","))
if r"\nocite{*}" in m: citadas |= bib
for k in sorted(citadas - bib): err.append(f"cita sin entrada en referencias.bib: {k}")
for k in sorted(bib - citadas): err.append(f"entrada de referencias.bib sin citar: {k}")
palabras = len(pdftxt.split())
sint = "SYNTHETIC" in pdftxt or "sinteticotrue" in ((A / "cifras.tex").read_text() if (A / "cifras.tex").exists() else "")
print(f"palabras PDF ≈ {palabras:,} · citas {len(citadas)} · entradas bib {len(bib)} · índice {'SINTÉTICO (marca de agua)' if sint else 'real'}")
por = {}
for e in err: por.setdefault(e.split(":")[0], 0); por[e.split(":")[0]] += 1
for e in err: print("ERROR", e)
print("errores por origen:", ", ".join(f"{k} {v}" for k, v in sorted(por.items())) or "ninguno")
print("QA texto:", "OK" if not err else f"{len(err)} errores"); sys.exit(1 if err else 0)
