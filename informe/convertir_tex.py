"""Conversión ÚNICA de articulo/secciones/*.tex a informe/secciones/*.html (fragmentos), con pandoc 3 + citeproc.
- \\cifra{id} / \\cifraabs / \\cifraopc / \\pval → <span class="cf" data-cifra="id" data-modo="txt|abs|opc|p"></span> (ensamblar.py los llena).
- Referencias cruzadas renumeradas al esquema del informe (capítulos 1–7, anexos A–C, figuras y tablas por capítulo).
- Las figuras y \\input de tablas se quitan: el informe las coloca a mano con su componente.
- Citas: autor-año (Chicago) sin bibliografía por sección; la lista completa sale en secciones/referencias.html.
Después de la primera corrida, secciones/*.html se editan a mano: este script NO sobrescribe salvo con --forzar."""
import re, sys, json, subprocess, pathlib
R = pathlib.Path(__file__).resolve().parents[1]; SEC = R / "articulo/secciones"; OUT = R / "informe/secciones"; OUT.mkdir(exist_ok=True)
FORZAR = "--forzar" in sys.argv
# archivo .tex → (archivo html, número de capítulo o letra de anexo o None)
MAPA = [("01_intro", "00-introduction", None), ("02_delegacion", "01-delegation", "1"), ("03_datos", "02-data", "2"),
        ("04_metodo", "03-method", "3"), ("05_indice", "04-index", "4"), ("06_atlas", "05-atlas", "5"),
        ("07_validacion", "06-validation", "6"), ("08_limites", "07-limitations", "7"), ("09_conclusion", "08-conclusion", None),
        ("A_rubrica", "A-rubric", "A"), ("B_crosswalk", "B-crosswalk", "B"), ("F_citar", "C-cite", "C")]
FIG = {"fig:escalera": "1.1", "fig:flujo": "3.1", "fig:isco": "4.1", "fig:barreras": "4.2", "fig:mapa": "5.1", "fig:ingreso": "5.2"}
TAB = {"tab:comparativa": "1.1", "tab:cobertura": "2.1", "tab:ocupaciones": "4.1", "tab:h1": "5.1"}
EQ = {"eq:adi_o": "(1)", "eq:adi_var": "(2)", "eq:adi_c": "(3)"}

# 1) etiquetas de sección → número del informe (recorre secciones y subsecciones en orden)
SECN = {}
for tex, _, cap in MAPA:
    sub = 0
    for l in (SEC / f"{tex}.tex").read_text().splitlines():
        if re.search(r"\\section\{", l): actual = cap
        elif re.search(r"\\subsection\{", l): sub += 1; actual = f"{cap}.{sub}" if cap else None
        for lab in re.findall(r"\\label\{((?:sec|app):[^}]*)\}", l):
            SECN[lab] = actual
NOMBRE = lambda lab: ("the Introduction" if lab == "sec:intro" else "the Conclusion" if lab == "sec:conclusion" else
                      f"Annex {SECN[lab]}" if lab.startswith("app:") else
                      (f"Chapter {SECN[lab]}" if SECN.get(lab) and "." not in SECN[lab] else f"Section {SECN.get(lab, '??' + lab)}"))


def referencias(s):
    s = re.sub(r"(?:Sections?|Chapters?)~\\ref\{([^}]*)\}(?:\s*and~\\ref\{([^}]*)\})?",
               lambda m: NOMBRE(m[1]) + (f" and {NOMBRE(m[2]).replace('Section ', '').replace('Chapter ', '')}" if m[2] else ""), s)
    s = re.sub(r"Appendix~\\ref\{([^}]*)\}", lambda m: NOMBRE(m[1]), s)
    s = re.sub(r"Figure~\\ref\{([^}]*)\}", lambda m: f"Figure {FIG.get(m[1], '??' + m[1])}", s)
    s = re.sub(r"Table~\\ref\{([^}]*)\}", lambda m: f"Table {TAB.get(m[1], '??' + m[1])}", s)
    s = re.sub(r"Equations?~\\ref\{([^}]*)\}(?:[–-]+|\s*and~)\\ref\{([^}]*)\}", lambda m: f"Equations {EQ[m[1]]}–{EQ[m[2]]}", s)
    s = re.sub(r"\\ref\{([^}]*)\}", lambda m: EQ.get(m[1]) or FIG.get(m[1]) or TAB.get(m[1]) or NOMBRE(m[1]), s)
    return s


def previo(s):
    s = re.sub(r"(?m)^%.*\n", "", s)
    s = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}\s*", "", s, flags=re.S)
    s = re.sub(r"\\input\{tablas/[^}]*\}\s*", "", s)
    for mac, modo in (("cifraabs", "abs"), ("cifraopc", "opc"), ("pval", "p"), ("cifra", "txt")):
        s = re.sub(r"\\" + mac + r"\{([^}]*)\}", lambda m: f"CIFRA{modo}Z{m[1].replace('_', 'UNDERSCORE')}ZFIN", s)
    s = re.sub(r"\\label\{(?:sec|app):[^}]*\}", "", s)
    return referencias(s)


def pandoc(tex):
    r = subprocess.run(["pandoc", "-f", "latex", "-t", "html5", "--mathml", "--citeproc", "--wrap=none",
                        "--bibliography", str(R / "articulo/referencias.bib"), "-M", "suppress-bibliography=true",
                        "-M", "link-citations=false", "--shift-heading-level-by=1"], input=tex, capture_output=True, text=True)
    if r.stderr.strip(): print("  pandoc:", r.stderr.strip()[:400])
    return r.stdout


def posterior(h):
    h = re.sub(r"CIFRA(txt|abs|opc|p)Z(.+?)ZFIN", lambda m: f'<span class="cf" data-cifra="{m[2].replace("UNDERSCORE", "_")}" data-modo="{m[1]}"></span>', h)
    h = re.sub(r'<span class="citation" data-cites="[^"]*">(.*?)</span>', r'<span class="cite">\1</span>', h)
    return h


claves = set()
for tex, html, cap in MAPA:
    dst = OUT / f"{html}.html"
    src = (SEC / f"{tex}.tex").read_text()
    for g in re.findall(r"\\cite[pt]?\*?(?:\[[^]]*\])*\{([^}]*)\}", src): claves |= {k.strip() for k in g.split(",")}
    if dst.exists() and not FORZAR: print(f"  existe {dst.name} (usar --forzar)"); continue
    dst.write_text(f"<!-- convertido de articulo/secciones/{tex}.tex por convertir_tex.py; editar aquí desde ahora -->\n" + posterior(pandoc(previo(src))))
    print(f"  {tex}.tex → {dst.name}")
# bibliografía completa una sola vez
bib = OUT / "referencias.html"
if FORZAR or not bib.exists():
    r = subprocess.run(["pandoc", "-f", "markdown", "-t", "html5", "--citeproc", "--wrap=none", "--bibliography", str(R / "articulo/referencias.bib")],
                       input="---\nnocite: |\n  " + ", ".join(f"@{k}" for k in sorted(claves)) + "\n---\n", capture_output=True, text=True)
    bib.write_text(r.stdout); print(f"  referencias.html ({len(claves)} claves; {r.stdout.count('class=\"csl-entry\"')} entradas)")
print(json.dumps({k: v for k, v in SECN.items()}, ensure_ascii=False))
