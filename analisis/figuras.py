"""Paso 21: figuras del artículo (PDF vectorial en articulo/fig/, estilo sobrio, fuente serif). Si el índice es sintético cada
figura lleva la marca de agua diagonal «SYNTHETIC». Lee salidas/ (indice.py) y datos/atlas/. Uso: analisis/figuras.py [fig1 fig4 …]
Con --estilo informe: SVG con texto vivo (Barlow) en informe/fig/, paleta teal del informe (barreras validadas con el validador de dataviz:
pasa banda de luminosidad, croma, separación CVD y contraste) y tamaños de la retícula del informe (caja de texto de 7,0 in)."""
import sys, zipfile; sys.path.insert(0, "noche")
from comun import *
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INFORME = "--estilo" in sys.argv and sys.argv[sys.argv.index("--estilo") + 1] == "informe"
if "--estilo" in sys.argv: i = sys.argv.index("--estilo"); del sys.argv[i:i + 2]
lg = log("21_figuras"); SAL = RAIZ / "salidas"; FIG = RAIZ / ("informe/fig" if INFORME else "articulo/fig"); FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"], "mathtext.fontset": "stix",
                     "font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                     "ytick.major.width": 0.6, "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.03})
TINTA, GRIS, CLARO = "#1f2a36", "#7d8794", "#d9dde2"
INGRESO_COL = {"high": "#1f4e79", "upper-middle": "#4f86b8", "lower-middle": "#d08c3f", "low": "#a8432f"}
# paleta del paper (por defecto) y del informe: L2+ claro / L3 oscuro, cmap del mapa, tonos de la escalera, relleno de cajas
P = dict(l2="#a9c2da", l3="#1f4e79", cmap="Blues", tonos=["#eef1f4", "#dfe6ee", "#c6d5e4", "#a9c2da"], caja="#f3f5f7", sin_dato="#eceef0")
INGRESO_EN = {"high": "High income", "upper-middle": "Upper-middle income", "lower-middle": "Lower-middle income", "low": "Low income"}
GG = {"1": "Managers", "2": "Professionals", "3": "Technicians and associate prof.", "4": "Clerical support", "5": "Service and sales",
      "6": "Skilled agricultural", "7": "Craft and related trades", "8": "Plant and machine operators", "9": "Elementary occupations"}
BARRERAS = [("barrera_fisica", "Physical", "#5b6b7c"), ("barrera_responsabilidad", "Accountability", "#9c6b3f"),
            ("barrera_confianza", "Trust", "#b9a26b"), ("barrera_acceso", "Access", "#8fa9bf")]
if INFORME:
    from matplotlib import font_manager
    for f in sorted((RAIZ / "informe/fonts").glob("Barlow-*.ttf")): font_manager.fontManager.addfont(str(f))
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Barlow", "Helvetica Neue", "DejaVu Sans"], "mathtext.fontset": "custom", "svg.hashsalt": "adi-informe",
                         "mathtext.rm": "Barlow", "mathtext.it": "Barlow:italic", "font.size": 8.6, "svg.fonttype": "none",
                         "axes.edgecolor": "#6b7280", "axes.labelcolor": "#1a1918", "xtick.color": "#6b7280", "ytick.color": "#1a1918",
                         "xtick.labelcolor": "#4b5058", "ytick.labelcolor": "#1a1918", "axes.spines.left": False, "ytick.major.size": 0})
    TINTA, GRIS, CLARO = "#1a1918", "#6b7280", "#e5e3e0"
    # rampa ordinal validada con validate_palette.js de dataviz (--ordinal, superficie #fff: tono único, L monótona, contraste del extremo claro 2,16:1);
    # cada grupo lleva además su forma, para que el ingreso no dependa solo del color
    INGRESO_COL = {"high": "#0a4540", "upper-middle": "#1d7770", "lower-middle": "#43998f", "low": "#7cbcb5"}
    BARRERAS = [("barrera_fisica", "Physical", "#5b6fae"), ("barrera_responsabilidad", "Accountability", "#c4862f"),
                ("barrera_confianza", "Trust", "#8e4f8f"), ("barrera_acceso", "Access", "#5f8f3a")]
    P = dict(l2="#9ccbc6", l3="#0a5c56", cmap=matplotlib.colors.LinearSegmentedColormap.from_list("adi", ["#e8f3f1", "#9ccbc6", "#2f8f86", "#0a4a45"]),
             tonos=["#eef5f4", "#d9ebe9", "#9ccbc6", "#4fa39c"], caja="#f3f1ee", sin_dato="#ebe9e5")
W = 7.0 if INFORME else 6.5     # ancho de la caja de texto del informe (in)
WW = 7.0 if INFORME else 6.5    # ancho total (in)
SINT = (SAL / "adi_isco.csv").exists() and pd.read_csv(SAL / "adi_isco.csv").sintetico.astype(str).str.lower().eq("true").any()


def guardar(fig, nombre):
    if SINT:
        fig.text(0.5, 0.5, "SYNTHETIC", rotation=30, ha="center", va="center", fontsize=54, color="#b22222", alpha=0.18, weight="bold", zorder=100)
    p = FIG / f"{nombre}.{'svg' if INFORME else 'pdf'}"; fig.savefig(p, transparent=INFORME, **({"metadata": {"Date": None}} if INFORME else {})); plt.close(fig)  # SVG sin fecha: se regenera idéntico
    if not INFORME: registrar(p, "derivado: figuras.py", nota="SINTÉTICO" if SINT else "")  # el informe no ensucia el manifiesto de datos
    lg.info(f"{p.name}")


def caja(ax, x, y, w, h, texto, fc="white", ec=TINTA, fs=8, peso="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012", fc=fc, ec=ec, lw=0.7))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=fs, weight=peso, color=TINTA, wrap=True)


def flecha(ax, a, b):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=8, lw=0.7, color=GRIS))


def fig1_escalera():
    niveles = [("L0", "No meaningful role", "Human does the task;\nagent cannot speed\nup any substantial\npart"),
               ("L1", "Augmentation", "Human performs the\ntask; AI assists\nstep by step\n(drafts, searches)"),
               ("L2", "Partial delegation", "Agent executes\nsub-steps end to end;\nhuman does a key\nstep or reviews"),
               ("L3", "Full delegation", "Agent completes the\ntask from goal and\naccess; human\nassigns and accepts")]
    fig, ax = plt.subplots(figsize=(6.5, 3.0)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    tonos = P["tonos"]
    for k, (cod, nom, defi) in enumerate(niveles):
        x, y, w, h = 0.02 + k * 0.205, 0.08 + k * 0.15, 0.19, 0.42
        ax.add_patch(plt.Rectangle((x, 0.08), w, y - 0.08 + h, fc=tonos[k], ec=TINTA, lw=0.6))
        ax.text(x + w / 2, y + h - 0.05, f"{cod}", ha="center", va="top", fontsize=12, weight="bold", color=TINTA)
        ax.text(x + w / 2, y + h - 0.14, nom, ha="center", va="top", fontsize=8.5, style="italic", color=TINTA)
        ax.text(x + w / 2, y + 0.04, defi, ha="center", va="bottom", fontsize=6.3, color=TINTA, linespacing=1.25)
    ax.annotate("", xy=(0.83, 0.97), xytext=(0.02, 0.62), arrowprops=dict(arrowstyle="-|>", color=GRIS, lw=0.8))
    ax.text(0.33, 0.86, "agent contributes → executes → finishes", rotation=21, fontsize=7.5, color=GRIS, ha="center")
    ax.text(0.865, 0.62, "Barriers that keep\na task below L3", fontsize=8, weight="bold", color=TINTA, va="top")
    for k, (_, nom, col) in enumerate(BARRERAS):
        yy = 0.5 - k * 0.1; ax.add_patch(plt.Rectangle((0.865, yy - 0.025), 0.02, 0.05, fc=col, ec="none"))
        ax.text(0.895, yy, nom, fontsize=7.5, va="center", color=TINTA)
    guardar(fig, "fig1_escalera")


def _claim(i, defecto):
    """Valor de salidas/claims.jsonl (para que las cajas de la figura 2 no lleven cifras escritas a mano)."""
    import json
    f = SAL / "claims.jsonl"
    if f.exists():
        for l in f.read_text().splitlines():
            c = json.loads(l)
            if c.get("id") == i and c.get("valor") not in (None, "--"): return c["valor"]
    return defecto


def fig2_flujo():
    fig, ax = plt.subplots(figsize=(6.5, 2.4)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    nt, nm, ni, npai = (int(_claim(i, d)) for i, d in (("cobertura.tareas", 18796), ("n.modelos", 2), ("cobertura.isco", 433), ("cobertura.paises", 146)))
    pasos = [(f"O*NET 30.2\n{nt:,} task\nstatements", 0.0), ("Crosswalk\nO*NET-SOC 2019\n→ SOC 2010\n→ ISCO-08", 0.205),
             (f"Ratings\n{nm} language models\n+ validation\nsample (1,500 tasks)", 0.41), (f"ISCO-08\n{ni} unit groups\ntask-weighted\nADI, ADI3, ADIs", 0.615),
             (f"Countries\nILOSTAT\nemployment\n{npai} countries\n→ world headline", 0.82)]
    for t, x in pasos: caja(ax, x + 0.005, 0.38, 0.17, 0.5, t, fc=P["caja"], fs=7.2)
    for (_, x1), (_, x2) in zip(pasos, pasos[1:]): flecha(ax, (x1 + 0.178, 0.63), (x2 + 0.003, 0.63))
    notas = ["importance × frequency\nweights", "SOC → k ISCO groups:\nweight 1/k", "modal level; ties →\nlower; median share",
             "bootstrap over tasks\nwithin occupation", "4-digit weights within\nreported groups"]
    for (n, (_, x)) in zip(notas, pasos): ax.text(x + 0.09, 0.27, n, ha="center", va="top", fontsize=6.8, color=GRIS, style="italic")
    guardar(fig, "fig2_flujo")


def fig3_isco():
    g = pd.read_csv(SAL / "indice_gg.csv", dtype={"gg": str}).sort_values("adi_l2")
    fig, ax = plt.subplots(figsize=(W, 2.62) if INFORME else (6.0, 3.2)); y = np.arange(len(g))
    ax.barh(y, 100 * g.adi_l2, color=P["l2"], height=0.62, label="ADI (L2 or L3)")
    ax.barh(y, 100 * g.adi_l3, color=P["l3"], height=0.62, label="ADI3 (L3 only)")
    ax.errorbar(100 * g.adi_l2, y, xerr=[100 * (g.adi_l2 - g.lo), 100 * (g.hi - g.adi_l2)], fmt="none", ecolor=TINTA, elinewidth=0.7, capsize=2)
    ax.set_yticks(y, [f"{k}  {GG.get(k, k)}" for k in g.gg]); ax.set_xlabel("Share of task weight delegable to AI agents (%)")
    ax.set_xlim(0, 100); ax.legend(frameon=False, loc="lower right", fontsize=8); ax.grid(axis="x", color=CLARO, lw=0.5); ax.set_axisbelow(True)
    if INFORME:  # etiqueta de valor al final de cada barra, después del bigote
        for yy, v, h in zip(y, 100 * g.adi_l2, 100 * g.hi): ax.text(h + 1.2, yy, f"{v:.1f}", va="center", fontsize=7.6, color=TINTA, fontweight="semibold")
    guardar(fig, "fig3_isco")


def natural_earth():
    d = DATOS / "geo"; shp = d / "ne_110m_admin_0_countries.shp"
    if not shp.exists():
        z = d / "ne_110m_admin_0_countries.zip"
        if descargar("https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip", z, "Natural Earth 110m", lg, minimo=10000):
            zipfile.ZipFile(z).extractall(d)
    return shp if shp.exists() else None


def fig4_mapa():
    p = pd.read_csv(SAL / "adi_pais.csv")
    try:
        import geopandas as gpd
        shp = natural_earth()
        if shp is None: raise RuntimeError("sin Natural Earth")
        w = gpd.read_file(shp); iso = w["ISO_A3_EH"].where(w["ISO_A3_EH"] != "-99", w["ADM0_A3"]); w["iso3"] = iso
        w = w[w.iso3 != "ATA"].merge(p[["iso3", "adi_l2"]], on="iso3", how="left"); w["v"] = 100 * w.adi_l2
        fig, ax = plt.subplots(figsize=(WW, 2.84) if INFORME else (6.5, 3.4))
        if INFORME: fig.subplots_adjust(left=0, right=1, bottom=0, top=1)  # el mapa ocupa el ancho de la caja: el SVG sale a escala 1:1
        w[w.v.isna()].plot(ax=ax, color=P["sin_dato"], edgecolor="white", linewidth=0.2)
        if INFORME:  # leyenda dentro del mapa, sobre el Pacífico sur: el mapa gana alto sin crecer la página
            cax = ax.inset_axes([0.015, 0.13, 0.25, 0.035])
            w[w.v.notna()].plot(ax=ax, column="v", cmap=P["cmap"], edgecolor="white", linewidth=0.2, legend=True, cax=cax,
                                legend_kwds={"orientation": "horizontal"})
            cax.tick_params(labelsize=7, length=2, width=0.5, pad=1.5); cax.set_title("ADI$_c$, % of task time at L2–L3", fontsize=7, loc="left", pad=3)
            for s_ in cax.spines.values(): s_.set_visible(False)
        else:
            w[w.v.notna()].plot(ax=ax, column="v", cmap=P["cmap"], edgecolor="white", linewidth=0.2, legend=True,
                                legend_kwds={"shrink": 0.55, "label": "ADI$_c$ (% of employment-weighted task time at L2–L3)", "orientation": "horizontal", "pad": 0.02})
        ax.set_axis_off(); ax.set_xlim(-170, 180); ax.set_ylim(-57, 84)
    except Exception as e:
        lg.warning(f"mapa con geopandas falló ({e}); gráfico de puntos por país")
        p = p.sort_values("adi_l2"); fig, ax = plt.subplots(figsize=(6.5, 7.5))
        ax.scatter(100 * p.adi_l2, np.arange(len(p)), s=6, c=p.ingreso.map(INGRESO_COL).fillna(GRIS))
        ax.set_yticks(np.arange(len(p)), p.iso3, fontsize=3.5); ax.set_xlabel("ADI$_c$ (%)")
    guardar(fig, "fig4_mapa")


MARCA = {"high": "D", "upper-middle": "^", "lower-middle": "s", "low": "o"}; MARCA_S = {"high": 24, "upper-middle": 34, "lower-middle": 26, "low": 30}  # áreas parejas a la vista


def fig5_ingreso():
    p = pd.read_csv(SAL / "indice_pais_detalle.csv").dropna(subset=["pib_pc_ppp"])
    x, y = np.log(p.pib_pc_ppp), 100 * p.adi_l2
    fig, ax = plt.subplots(figsize=(WW, 3.1) if INFORME else (5.2, 3.6))
    for ing, col in INGRESO_COL.items():
        d = p[p.ingreso == ing]; ax.scatter(np.log(d.pib_pc_ppp), 100 * d.adi_l2, s=MARCA_S[ing] if INFORME else 14, color=col, alpha=1 if INFORME else 0.85,
                   marker=MARCA[ing] if INFORME else "o", lw=0.7 if INFORME else 0, edgecolors="white" if INFORME else "none", label=INGRESO_EN[ing], zorder=3)
    b, a = np.polyfit(x, y, 1); xx = np.linspace(x.min(), x.max(), 50); ax.plot(xx, a + b * xx, color=TINTA, lw=0.9)
    import matplotlib.patheffects as pe
    desp = {"COL": (-34, -8), "MEX": (10, -10), "BRA": (-30, 10), "USA": (-8, 9), "IND": (5, -8), "DEU": (6, -9), "NGA": (-22, 5)}
    for iso, (dx, dy) in desp.items():
        r = p[p.iso3 == iso]
        if len(r): ax.annotate(iso, (np.log(r.pib_pc_ppp.iat[0]), 100 * r.adi_l2.iat[0]), fontsize=7.5, color=TINTA, xytext=(dx, dy), textcoords="offset points",
                               arrowprops=dict(arrowstyle="-", color=GRIS, lw=0.5, shrinkA=0, shrinkB=2), path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    tk = [1000, 3000, 10000, 30000, 100000]; ax.set_xticks(np.log(tk), [f"{t:,}" for t in tk])
    ax.set_xlabel("GDP per capita, PPP (constant 2021 international \\$, log scale)"); ax.set_ylabel("ADI$_c$ (%)")
    ax.legend(frameon=False, fontsize=8, loc="upper left"); ax.grid(color=CLARO, lw=0.5); ax.set_axisbelow(True)
    guardar(fig, "fig5_ingreso")


def fig6_barreras():
    g = pd.read_csv(SAL / "indice_gg.csv", dtype={"gg": str}).sort_values("gg", ascending=False)
    fig, ax = plt.subplots(figsize=(W if INFORME else 6.0, 3.2)); y = np.arange(len(g)); base = np.zeros(len(g))
    for col, nom, c in BARRERAS:
        v = 100 * g[col].values; ax.barh(y, v, left=base, color=c, height=0.65, label=nom, edgecolor="white", lw=0.3); base += v
    ax.set_yticks(y, [f"{k}  {GG[k]}" for k in g.gg]); ax.set_xlabel("Task weight flagged by each barrier (%; barriers are not exclusive and stack)")
    ax.legend(frameon=False, ncol=4, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    ax.grid(axis="x", color=CLARO, lw=0.5); ax.set_axisbelow(True)
    guardar(fig, "fig6_barreras")


def fig7_h4():
    """H4: probabilidad de delegación total (L3) según la duración humana de la tarea. Curva = logit preregistrado (regresiones.json);
    puntos = proporción observada de tareas en L3 por veintiles de duración (control visual del ajuste)."""
    import json
    k = json.load(open(SAL / "regresiones.json"))["h4"]["coef"]
    t = pd.read_csv(SAL / "adi_tarea.csv"); t = t[(t.n_modelos.fillna(0) > 0) & t.minutos.notna()]
    lm = np.log(np.clip(t.minutos, 1, 4800)); y = (t.nivel == 3).astype(float)
    q = pd.qcut(lm, 20, duplicates="drop"); g = pd.DataFrame({"lm": lm, "y": y}).groupby(q, observed=True).agg(lm=("lm", "median"), y=("y", "mean"))
    xx = np.linspace(0, np.log(4800), 300); pp = 100 / (1 + np.exp(-(k["const"] + k["lmin"] * xx + k["lmin2"] * xx ** 2)))
    pico = -k["lmin"] / (2 * k["lmin2"]); ppico = 100 / (1 + np.exp(-(k["const"] + k["lmin"] * pico + k["lmin2"] * pico ** 2)))
    fig, ax = plt.subplots(figsize=(W, 2.5) if INFORME else (5.2, 3.0))
    ax.scatter(g.lm, 100 * g.y, s=26, color=P["l2"], edgecolors=P["l3"], lw=0.6, zorder=3, label="Observed share at L3 (task-length twentieths)")
    ax.plot(xx, pp, color=P["l3"], lw=1.6, zorder=4, label="Preregistered logit fit (H4)")
    ax.axvline(pico, color=GRIS, lw=0.7, ls=(0, (3, 2)), zorder=2)
    ax.annotate(f"Peak at {np.exp(pico):.1f} minutes: {ppico:.1f}% of tasks fully delegable", (pico, ppico), xytext=(14, 4), textcoords="offset points",
                fontsize=7.8, color=TINTA, fontweight="semibold" if INFORME else "normal")
    tk = [1, 5, 15, 60, 240, 960, 4800]; ax.set_xticks(np.log(tk), ["1 min", "5", "15", "1 h", "4 h", "16 h", "80 h"])
    ax.set_xlim(-0.1, np.log(4800) + 0.1); ax.set_ylim(0, max(100 * g.y.max(), ppico) * 1.3)
    ax.set_xlabel("Minutes a competent person needs for one instance of the task (log scale)"); ax.set_ylabel("Tasks rated L3 (%)")
    ax.legend(frameon=False, fontsize=8, loc="upper right"); ax.grid(color=CLARO, lw=0.5); ax.set_axisbelow(True)
    if INFORME: ax.spines["left"].set_visible(True); ax.spines["left"].set_color("#6b7280"); ax.tick_params(axis="y", length=3)
    guardar(fig, "fig7_h4")


TODAS = {"fig1": fig1_escalera, "fig2": fig2_flujo, "fig3": fig3_isco, "fig4": fig4_mapa, "fig5": fig5_ingreso, "fig6": fig6_barreras, "fig7": fig7_h4}
if __name__ == "__main__":
    pedidas = [a.split("_")[0] for a in sys.argv[1:]] or list(TODAS)
    lg.info(f"figuras {'SINTÉTICAS' if SINT else 'reales'}: {pedidas}")
    for k in pedidas:
        try: TODAS[k]()
        except Exception as e: lg.error(f"{k}: {e}")
