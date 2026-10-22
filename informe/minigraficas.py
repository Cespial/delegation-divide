"""Mini-gráficas SVG para «At a glance» (baldosas). Texto en tinta, color solo en las marcas; valores desde cifras.json y salidas/."""
import pandas as pd, pathlib
R = pathlib.Path(__file__).resolve().parents[1]
TINTA, GRIS, FIL = "#1a1918", "#6b7280", "#e5e3e0"
T = lambda x, y, s, anc="start", tam=7, peso=400, col=TINTA: f'<text x="{x:.1f}" y="{y:.1f}" font-family="Barlow" font-size="{tam}" font-weight="{peso}" fill="{col}" text-anchor="{anc}">{s}</text>'


def titular(l2, l3):
    w = 300; s = f'<svg viewBox="0 0 {w} 46" xmlns="http://www.w3.org/2000/svg">'
    a, b = w * l3 / 100, w * (l2 - l3) / 100
    s += f'<rect x="0" y="12" width="{w}" height="14" fill="#eef5f4"/><rect x="0" y="12" width="{a + b:.1f}" height="14" fill="#9ccbc6"/><rect x="0" y="12" width="{a:.1f}" height="14" fill="#0a4a45"/>'
    # L3 es una franja de pocos puntos: su rótulo va arriba, el de L2 abajo, para que no se monten
    s += T(0, 8, f"L3 full: {l3:.1f}%", tam=7.2, peso=600) + T(a + b / 2, 39, f"L2 partial: {l2 - l3:.1f}%", "middle", 7.2) + T(w, 39, f"L0–L1: {100 - l2:.1f}%", "end", 7.2, col=GRIS)
    return s + "</svg>"


def barras(pares, maximo=100, colores=None, w=300, alto_barra=11, sep=4, etq_w=96, sufijo="%"):
    h = len(pares) * (alto_barra + sep); s = f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
    for k, (et, v) in enumerate(pares):
        y = k * (alto_barra + sep); L = (w - etq_w - 34) * v / maximo; c = colores[k] if colores else "#2f8f86"
        s += T(etq_w - 6, y + alto_barra - 2.5, et, "end", 7) + f'<rect x="{etq_w}" y="{y}" width="{max(L, 1):.1f}" height="{alto_barra}" fill="{c}"/>'
        s += T(etq_w + L + 4, y + alto_barra - 2.5, f"{v:.1f}{sufijo}" if sufijo else f"{v:.2f}", tam=7, peso=600)
    return s + "</svg>"


def tira_paises(marcas):
    p = pd.read_csv(R / "salidas/adi_pais.csv"); v = 100 * p.adi_l2; w, x0, x1 = 300, 10, 290
    lo, hi = 10, 70; X = lambda z: x0 + (x1 - x0) * (z - lo) / (hi - lo)
    s = f'<svg viewBox="0 0 {w} 62" xmlns="http://www.w3.org/2000/svg"><line x1="{x0}" x2="{x1}" y1="30" y2="30" stroke="{FIL}"/>'
    for z in v: s += f'<circle cx="{X(z):.1f}" cy="30" r="3.1" fill="#2f8f86" fill-opacity="0.35"/>'
    for k, (iso, nom) in enumerate(marcas):
        z = 100 * p.loc[p.iso3 == iso, "adi_l2"].iat[0]; arriba = k % 2 == 0; y = 14 if arriba else 50
        s += f'<circle cx="{X(z):.1f}" cy="30" r="3.6" fill="#0a4a45"/><line x1="{X(z):.1f}" x2="{X(z):.1f}" y1="{19 if arriba else 34}" y2="{26 if arriba else 41}" stroke="{TINTA}" stroke-width="0.6"/>'
        s += T(X(z), y, f"{nom} {z:.1f}", "middle", 6.8, 600 if iso in ("COL",) else 400)
    for t in (20, 40, 60): s += T(X(t), 61, f"{t}%", "middle", 6, col=GRIS)
    return s + "</svg>"
