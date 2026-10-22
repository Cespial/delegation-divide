"""Ensambla informe/informe.html: plantilla Jinja + secciones editables + cifras.json + figuras SVG + tablas HTML + componentes.
Cada número del informe sale de cifras.json por id; un id inexistente se imprime en rojo como ??id y hace fallar el paso.
Uso: .venv/bin/python -I informe/ensamblar.py"""
import re, json, sys, pathlib
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup as M
INF = pathlib.Path(__file__).resolve().parent; R = INF.parent; sys.path.insert(0, str(INF))
import minigraficas as mg
D = json.load(open(INF / "cifras.json")); C = D["cifras"]
v = lambda i: C[i]["v"]
env = Environment(loader=FileSystemLoader(str(INF / "plantilla")), autoescape=False)
K = env.get_template("componentes.html").module
leer = lambda p: (INF / p).read_text()
def svg(nombre):
    s = leer(f"fig/{nombre}.svg"); s = s[s.index("<svg"):]
    return M(re.sub(r'<svg([^>]*?) width="[^"]*" height="[^"]*"', r'<svg\1', s, count=1))
def tab(nombre): return M(re.sub(r"<!--.*?-->\n?", "", leer(f"tablas/{nombre}.html")))
def logos():
    out = []
    for f, cls in (("marca/adi-marca.svg", "adi"), ("marca/logos/unal-logo.svg", "unal"), ("marca/logos/eafit-logo.svg", "eafit"),
                   ("marca/logos/inplux-logo-horizontal-mono.svg", "inplux")):
        out.append(f'<img class="{cls}" src="{f}" alt="{cls.upper()}">')
    return M("".join(out))
c = K.c
FUENTE = "Agent Delegability Index v2026.1 (doi:10.5281/zenodo.23552918)"

# ---------- componentes que reemplazan marcadores <!--@x--> ----------
def ladder():
    niveles = [("L0", "No meaningful role", "The agent cannot perform or materially speed up any substantial part of the task.", "Human does the task.", "tareas.nivel0.pct"),
               ("L1", "Augmentation", "A human performs the task; the AI assists step by step with drafts, searches and suggestions.", "Human produces the output.", "tareas.nivel1.pct"),
               ("L2", "Partial delegation", "An agent executes substantial sub-steps end to end from a goal; a human performs an essential step or reviews.", "Human checks and completes.", "tareas.nivel2.pct"),
               ("L3", "Full delegation", "An agent completes the whole task to the quality a competent worker would accept, given only the goal and access.", "Human assigns and accepts.", "tareas.nivel3.pct")]
    h = '<div class="ladder">'
    for k, (cod, nom, d, rol, i) in enumerate(niveles):
        h += f'<div class="n n{k}" style="min-height:{1.55 + 0.32 * k:.2f}in"><div class="c">{cod}</div><div class="nom">{nom}</div><p>{d}</p><div class="rol">{rol}</div><div class="pct">{c(i)}%<small>of task statements</small></div></div>'
    h += '</div><div class="barreras-ley"><b>Barriers recorded for every task:</b><span style="--c:#5b6fae">Physical presence</span><span style="--c:#c4862f">Accountability</span><span style="--c:#8e4f8f">Trust and care</span><span style="--c:#5f8f3a">Access to systems</span></div>'
    return M(h)

def flujo():
    pasos = [("Tasks", "cobertura.tareas", "O*NET 30.2 task statements", "Weighted by importance and frequency."),
             ("Crosswalk", "cobertura.isco", "ISCO-08 unit groups", "O*NET-SOC 2019 to SOC 2010 to ISCO-08; a SOC code split across k groups weighs 1/k."),
             ("Ratings", "n.modelos", "language models rate every task", "Frozen rubric; ties go to the lower level; human and agentic validation."),
             ("Occupations", "cobertura.isco", "occupation scores", "Task-weighted ADI, ADI3 and ADIs with bootstrap intervals."),
             ("Countries", "cobertura.paises", "countries in the atlas", "ILOSTAT employment by occupation, latest year from 2019.")]
    return M('<div class="flujo">' + "".join(f'<div class="paso"><div class="k">{a}</div><div class="c">{c(i)}</div><div class="t">{t}</div><p>{p}</p></div>' for a, i, t, p in pasos) + "</div>")

def tarjetas():
    t = [("agree.kappa.sonnet_haiku", "Model and model", f"Sonnet 5.5 and Haiku 5.5 over {C['cobertura.tareas.puntuadas']['txt']} tasks."),
         ("agree.kappa.humano.modelo", "Human and models", f"Blind rating of {C['n.humano']['txt']} tasks, led by a coauthor with student raters."),
         ("agree.kappa.panel.modelo", "Agentic panel and models", f"Claude Opus 5.5 with web search over {C['n.panel']['txt']} tasks.")]
    return M('<div class="tarjetas">' + "".join(f'<div class="tarjeta"><div class="c">{c(i)}</div><div class="t">{n}</div><p>{p}</p></div>' for i, n, p in t) + "</div>")

COMP = {
 "fig1_1": lambda: K.figura("1.1", "Four levels of delegation, from no role for the agent to full hand-over",
        "ADI rubric levels and the share of the 18,796 O*NET task statements rated at each level (model consensus)", ladder(),
        "Levels describe what is technically feasible with publicly available AI agents as of October 2026, not current adoption.", FUENTE + "; O*NET 30.2.", "ancho"),
 "fig3_1": lambda: K.figura("3.1", "From task statements to a country atlas in five steps", "Pipeline of the index, with the count at each step",
        flujo(), "", FUENTE + ".", "ancho"),
 "fig4_1": lambda: K.figura("4.1", "Managers and clerical workers do the most delegable work; elementary occupations the least",
        "Share of task weight at L2 or L3 (ADI) and at L3 only (ADI3), by ISCO-08 major group, %", svg("fig3_isco"),
        "Whiskers show the 95% bootstrap interval of ADI (1,000 draws, tasks resampled within occupation). Unit groups are averaged with world employment weights.", FUENTE + "; ILOSTAT."),
 "fig4_2": lambda: K.figura("4.2", "The physical barrier dominates manual work; access and trust weigh on office work",
        "Task weight flagged by each barrier, by ISCO-08 major group, %", svg("fig6_barreras"),
        "Barriers are not exclusive: a task can carry several, so bars can exceed 100%.", FUENTE + "."),
 "fig5_1": lambda: K.figura("5.1", "Delegable work concentrates in high-income economies",
        "ADI by country: employment-weighted share of task time at L2 or L3, %", svg("fig4_mapa"),
        "Finest ISCO-08 level each country reports to ILOSTAT, latest year from 2019. Grey: no occupation data. Boundaries: Natural Earth 1:110m.", FUENTE + "; ILOSTAT.", "ancho"),
 "fig5_2": lambda: K.figura("5.2", "Each log point of income adds about seven points of delegable work",
        "ADI against GDP per capita at purchasing power parity (log scale), by World Bank income group, FY2026", svg("fig5_ingreso"),
        M(f"Line: ordinary least squares fit of the preregistered H1 regression, slope {c('h1.pendiente')} (95% CI {c('h1.pendiente.lo')}–{c('h1.pendiente.hi')})."),
        FUENTE + "; World Bank World Development Indicators.", "ancho"),
 "tab2_1": lambda: K.tabla("2.1", "Coverage of the country atlas by income group", tab("tab2_cobertura"),
        "Countries with ILOSTAT employment by ISCO-08 occupation for a year from 2019 onward. Resolution is the finest ISCO-08 level the country reports. Employment in millions. Source: ILOSTAT; World Bank FY2026 income groups."),
 "tab4_1": lambda: K.tabla("4.1", "The ten most and ten least delegable occupations", tab("tab3_ocupaciones"),
        "ISCO-08 unit groups. ADI: task-weighted share at L2 or L3; ADI3: at L3; ADIs: weighted mean share of task time delegable, with 95% bootstrap interval (1,000 draws). Source: " + FUENTE + "."),
 "tab5_1": lambda: K.tabla("5.1", "Delegability rises with income across countries", tab("tab4_h1"),
        "Columns (1)–(3): ADI in percent (H1); column (3) uses equal weights within reported groups. Column (4): standardized gap between ADI and Anthropic Economic Index usage per working-age person (H2). Reference: high income. Standard errors in parentheses; stars refer to the preregistered one-sided tests (* p < 0.05, ** p < 0.01, *** p < 0.001)."),
 "box1": lambda: M('<div class="box" id="box-1"><p class="bn">Box 1</p><h4>What the rubric asks of each task</h4>'
        '<p>The rating model receives one occupation title and one task statement, and a fixed definition of the reference technology: publicly available AI agents as of October 2026, able to use tools, run code, browse the web, operate a computer and handle files, with no physical body.</p>'
        '<p>It returns a level from L0 to L3, the share of the task’s working time an agent could take over, the minutes a competent human needs for one instance, four yes-or-no barriers (physical presence, accountability, trust and care, access to systems) and its confidence. It rates what is technically feasible, not what employers do today or what the law allows.</p>'
        '<p>The rubric was frozen at preregistration; its full text is in Annex A.</p></div>'),
 "tarjetas": tarjetas,
 "lat:isco": lambda: K.lat("ISCO-08", "", "The International Standard Classification of Occupations, maintained by the ILO. Its 436 unit groups are the finest level most countries use to report employment."),
 "lat:onet": lambda: K.lat("O*NET", c("cobertura.tareas"), "task statements in O*NET 30.2, the United States occupational database, the largest public bank of written job tasks."),
 "lat:extremos": lambda: K.lat("Delegable on every task", c("extremo.isco.n.max"), M(f"unit groups reach the maximum, led by {C['extremo.isco.top1.nombre']['txt']}. {C['extremo.isco.n.min']['txt']} reach zero.")),
 "lat:h4": lambda: K.lat("Peak task length", M(f"{c('h4.pico.minutos')} min"), "of human time is where full delegation is most likely."),
 "lat:titular": lambda: K.lat("World headline", M(f"{c('titular.global.l2')}%"), M(f"of task time is at least partly delegable; 95% interval {c('titular.global.l2.lo')}–{c('titular.global.l2.hi')}%.")),
 "lat:h2": lambda: K.lat("Use and delegability", M(f"r = {c('h2.r.adi_uso')}"), M(f"across {c('h2.n')} countries with Anthropic Economic Index data.")),
}
INDICE = [("fig-1-1", "Figure 1.1", "Four levels of delegation"), ("tab-1-1", "Table 1.1", "Measures of AI and work compared"), ("tab-2-1", "Table 2.1", "Coverage of the country atlas"),
          ("fig-3-1", "Figure 3.1", "From task statements to a country atlas"), ("box-1", "Box 1", "What the rubric asks of each task"),
          ("fig-4-1", "Figure 4.1", "ADI by occupational major group"), ("tab-4-1", "Table 4.1", "The most and least delegable occupations"),
          ("fig-4-2", "Figure 4.2", "Barriers by occupational major group"), ("fig-5-1", "Figure 5.1", "ADI by country"),
          ("fig-5-2", "Figure 5.2", "ADI and income"), ("tab-5-1", "Table 5.1", "Country-level regressions")]

CAPS = [("00-introduction", None, "introduccion", "Introduction"), ("01-delegation", "1", "cap1", None), ("02-data", "2", "cap2", None),
        ("03-method", "3", "cap3", None), ("04-index", "4", "cap4", None), ("05-atlas", "5", "cap5", None), ("06-validation", "6", "cap6", None),
        ("07-limitations", "7", "cap7", None), ("08-conclusion", None, "conclusion", None)]
ANEXOS = [("A-rubric", "A", "anexoA"), ("B-crosswalk", "B", "anexoB"), ("C-cite", "C", "anexoC")]


def procesar(nombre, num):
    s = re.sub(r"<!-- convertido.*?-->\n?", "", leer(f"secciones/{nombre}.html"))
    m = re.search(r"<h2[^>]*>(.*?)</h2>", s, re.S); titulo = re.sub("<[^>]+>", "", m[1]).strip(); s = s[:m.start()] + s[m.end():]
    lead = ""
    if num:  # capítulos numerados: el primer párrafo va a la apertura
        p = re.search(r"<p>(.*?)</p>", s, re.S); texto = p[1]
        # la apertura lleva las primeras frases (≤ ~300 caracteres de texto visible); el resto del párrafo sigue en el cuerpo
        cortes = [m.end() for m in re.finditer(r"[.?!](?:</[a-z]+>)?\s+(?=[A-Z<])", texto)]
        vis = lambda t: len(re.sub(r"<[^>]+>", "", t))
        corte = next((k for k in reversed(cortes) if vis(texto[:k]) <= 300), cortes[0] if cortes else len(texto))
        lead, resto = texto[:corte].strip(), texto[corte:].strip()
        s = s[:p.start()] + (f"<p>{resto}</p>" if resto else "") + s[p.end():]
    k = [0]
    def h3(mm):
        k[0] += 1; return f'<h3 id="{nombre[:2]}-{mm[1]}">' + (f'<span class="num">{num}.{k[0]}</span>' if num and num.isdigit() else "") + mm[2] + "</h3>"
    s = re.sub(r'<h3 id="([^"]*)">(.*?)</h3>', h3, s)
    s = re.sub(r"<!--@tab1_1:inicio-->(.*?)<!--@tab1_1:fin-->", lambda mm: str(K.tabla("1.1", "Measures of AI and work compared with ADI", M(mm[1].replace("<table>", '<table class="comparativa">')),
               "? = the source does not state it. Source: authors’ review of the cited sources.")), s, flags=re.S)
    s = re.sub(r"<!--@([a-z0-9_:]+)-->", lambda mm: str(COMP[mm[1]]()), s)
    return titulo, M(lead), M(s)


capitulos = []
for nombre, num, ident, forzado in CAPS:
    t, lead, cuerpo = procesar(nombre, num)
    img = next((f"img/{ident}.{e}" for e in ("webp", "jpg", "png") if (INF / f"img/{ident}.{e}").exists()), None)
    capitulos.append(dict(id=ident, num=num, titulo=forzado or t, lead=lead, cuerpo=cuerpo, apertura=bool(num) or ident == "introduccion", img=img))
anexos = []
for nombre, num, ident in ANEXOS:
    t, _, cuerpo = procesar(nombre, None); anexos.append(dict(id=ident, num=num, titulo=t, cuerpo=cuerpo))

alto = lambda x: 1.0 + 3.6 * (x - 15) / 40
peldanos = [dict(id=f"titular.ingreso.{k}.l2", paises=f"cobertura.ingreso.{q}.paises", nombre=n, alto=round(alto(v(f"titular.ingreso.{k}.l2")), 2))
            for k, q, n in (("bajo", "bajo", "Low income"), ("medio_bajo", "medio_bajo", "Lower-middle income"), ("medio_alto", "medio_alto", "Upper-middle income"), ("alto", "alto", "High income"))]
GG = ["Managers", "Professionals", "Technicians", "Clerical support", "Service and sales", "Skilled agricultural", "Craft and trades", "Machine operators", "Elementary"]
grupos = sorted([(GG[g - 1], v(f"gg.{g}.l2")) for g in range(1, 10)], key=lambda z: -z[1])
fisica = sorted([(GG[g - 1], v(f"gg.{g}.barrera_fisica.pct")) for g in range(1, 10)], key=lambda z: -z[1])
mini = dict(titular=M(mg.titular(v("titular.global.l2"), v("titular.global.l3"))),
            ingreso=M(mg.barras([(n, v(f"titular.ingreso.{k}.l2")) for k, n in (("bajo", "Low"), ("medio_bajo", "Lower-middle"), ("medio_alto", "Upper-middle"), ("alto", "High"))],
                                colores=["#bfe0dc", "#7dbdb5", "#2f8f86", "#0a5c56"], maximo=60, etq_w=70, alto_barra=12)),
            grupos=M(mg.barras(grupos, maximo=100, alto_barra=10, sep=4.2)), fisica=M(mg.barras(fisica, maximo=100, colores=["#5b6fae"] * 9, alto_barra=10, sep=4.2)),
            paises=M(mg.tira_paises([("BDI", "Burundi"), ("IND", "India"), ("COL", "Colombia"), ("USA", "United States"), ("SGP", "Singapore")])),
            kappa=M(mg.barras([("Models", v("agree.kappa.sonnet_haiku")), ("Human", v("agree.kappa.humano.modelo")), ("Agentic panel", v("agree.kappa.panel.modelo"))],
                              maximo=1, etq_w=70, alto_barra=14, sep=6, sufijo="")))

html = env.get_template("informe.html").render(capitulos=capitulos, anexos=anexos, peldanos=peldanos, mini=mini, sintetico=D["sintetico"],
        marca=M(leer("marca/adi-marca.svg")), logos=logos(), referencias=M(leer("secciones/referencias.html")),
        indice_fig=[dict(id=a, n=b, titulo=t) for a, b, t in INDICE])
faltan = []
def llenar(m):
    i, modo = m[1], m[2]
    if i not in C:
        if modo == "opc": return "–"
        faltan.append(i); return f'<span class="cf falta">??{i}</span>'
    e = C[i]; return f'<span class="cf" data-cifra="{i}">{e.get(modo if modo in ("abs", "p") else "txt", e["txt"])}</span>'
html = re.sub(r'<span class="cf" data-cifra="([^"]+)" data-modo="([a-z]+)"></span>', llenar, html)
(INF / "informe.html").write_text(html)
n = len(re.findall(r'class="cf" data-cifra', html))
print(f"informe.html: {n} cifras desde cifras.json; {len(faltan)} ids inexistentes{': ' + ', '.join(sorted(set(faltan))) if faltan else ''}")
sys.exit(1 if faltan else 0)
