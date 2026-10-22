"""Perfil de Colombia en el atlas (página al estilo «Perfil de Colombia» del Informe Nacional de Competitividad).
Lee la tabla publicada salidas/indice_pais_detalle.csv (la misma que alimenta los claims del atlas) y escribe:
- informe/perfil.json: filas de la tabla Colombia / puesto en América Latina y el Caribe / mejor de la región / región / ingreso alto / mundo,
  y la frase-hallazgo; todo calculado aquí, nada tecleado.
- informe/fig/perfil_alc.svg: barras del ADI de los países de la región con Colombia resaltada.
verificar.py vuelve a llamar a calcular() y compara con el HTML. Uso: .venv/bin/python -I informe/perfil.py"""
import json, pathlib
import pandas as pd
INF = pathlib.Path(__file__).resolve().parent; R = INF.parent
PAIS, REGION = "COL", "Latin America & Caribbean"
NOMBRE = {"Puerto Rico (US)": "Puerto Rico", "Bahamas, The": "Bahamas", "St. Lucia": "Saint Lucia", "Curacao": "Curaçao"}
TINTA, GRIS, FIL = "#1a1918", "#5d636b", "#dcdad6"


def calcular():
    d = pd.read_csv(R / "salidas/indice_pais_detalle.csv"); d["nombre"] = d.pais.map(lambda x: NOMBRE.get(x, x))
    for c in ("adi_l2", "adi_l3"): d[c] = 100 * d[c]
    reg = d[d.region.str.strip() == REGION]; col = d[d.iso3 == PAIS].iloc[0]
    pond = lambda x, c: (x[c] * x.empleo_total).sum() / x.empleo_total.sum()
    def fila(c, nombre, unidad, fmt, mayor_mejor=True, ponderar=True, fuente=""):
        x = reg.dropna(subset=[c]); orden = x.sort_values(c, ascending=not mayor_mejor).reset_index(drop=True)
        puesto = int(orden.index[orden.iso3 == PAIS][0]) + 1; mejor = orden.iloc[0]
        agr = (lambda z: pond(z.dropna(subset=[c]), c)) if ponderar else (lambda z: z[c].mean())
        return dict(nombre=nombre, unidad=unidad, col=fmt(col[c]), puesto=f"{puesto} of {len(x)}", mejor=f"{mejor.nombre} ({fmt(mejor[c])})",
                    region=fmt(agr(reg)), alto=fmt(agr(d[d.ingreso == "high"])), mundo=fmt(agr(d)), fuente=fuente, v=float(col[c]))
    f1, f2 = (lambda v: f"{v:.1f}"), (lambda v: f"{v:.2f}")
    grupos = [
        ("Delegability", [fila("adi_l2", "ADI: task time at least partly delegable (L2–L3)", "%", f1, fuente="ADI v2026.1"),
                          fila("adi_l3", "ADI3: task time fully delegable (L3)", "%", f1, fuente="ADI v2026.1"),
                          fila("adi_share", "ADIs: expected share of working time delegable", "%", f1, fuente="ADI v2026.1")]),
        ("Adoption", [fila("usage_per_capita_index", "AI use per working-age adult (index)ᵃ", "index", f2, ponderar=False, fuente="Anthropic Economic Index"),
                      ]),
        ("Context", [fila("pib_pc_ppp", "GDP per capita, PPP (constant 2021 international $)ᵃ", "$", lambda v: f"{v:,.0f}", ponderar=False, fuente="World Bank WDI"),
                     fila("informalidad_pct", "Informal employment, % of total employmentᵃ ᵇ", "%", f1, mayor_mejor=False, ponderar=False, fuente="ILOSTAT")]),
    ]
    a = grupos[0][1][0]; n_reg = len(reg); lo, hi = f1(100 * col.l2_lo), f1(100 * col.l2_hi)
    mundo, alto = float(a["mundo"]), float(a["alto"])
    hallazgo = (f"Colombia ranks {a['puesto'].split()[0]} of {n_reg} countries in Latin America and the Caribbean: {a['col']}% of its task time is at least "
                f"partly delegable, {'above' if a['v'] > mundo else 'below'} the world figure of {a['mundo']}% and {alto - a['v']:.1f} points below high-income countries.")
    barras = reg.sort_values("adi_l2", ascending=False)[["iso3", "nombre", "adi_l2"]].values.tolist()
    k = [b[0] for b in barras].index(PAIS); ant, sig = barras[k - 1], barras[k + 1]
    hallazgo_fig = (f"Colombia sits between {ant[1]} ({ant[2]:.1f}%) and {sig[1]} ({sig[2]:.1f}%); {barras[0][1]} leads the region at {barras[0][2]:.1f}% "
                    f"and {barras[-1][1]} closes it at {barras[-1][2]:.1f}%.")
    return dict(grupos=grupos, hallazgo=hallazgo, hallazgo_fig=hallazgo_fig, n_region=n_reg, intervalo=f"{lo}–{hi}", anio=int(col.anio), resolucion=int(col.resolucion),
                region_l2=a["region"], mundo_l2=a["mundo"], barras=barras)


def svg(p):
    # viewBox en puntos tipográficos al ancho de la caja (7 in = 504 pt): font-size 7 se imprime a 7 pt
    W, H, x0, x1, y0, y1 = 504, 164, 24, 446, 12, 104; top = 60; vals = [b[2] for b in p["barras"]]
    Y = lambda v: y1 - (y1 - y0) * v / top; n = len(vals); paso = (x1 - x0) / n; ancho = paso * 0.66
    T = lambda x, y, s, anc="start", tam=7, peso=400, col=TINTA, rot=None, halo=False: (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Barlow" font-size="{tam}" '
         f'font-weight="{peso}" fill="{col}" text-anchor="{anc}"' + (f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else "")
         + (' stroke="#fff" stroke-width="2.2" paint-order="stroke"' if halo else "") + f">{s}</text>")
    s = f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
    for v in range(0, top + 1, 10):
        s += f'<line x1="{x0}" x2="{x1}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{FIL}" stroke-width="{0.8 if v == 0 else 0.4}"/>' + T(x0 - 5, Y(v) + 2.4, f"{v}", "end", 6.6, col=GRIS)
    s += T(x0 - 18, y0 - 6, "% of task time at L2–L3", tam=6.6, col=GRIS)
    for val, dash in ((float(p["region_l2"]), "4 2.4"), (float(p["mundo_l2"]), "1.2 2")):
        s += f'<line x1="{x0}" x2="{x1 + 4}" y1="{Y(val):.1f}" y2="{Y(val):.1f}" stroke="{TINTA}" stroke-width="0.7" stroke-dasharray="{dash}"/>'
    for k, (iso, nom, v) in enumerate(p["barras"]):
        cx = x0 + paso * (k + 0.5); c = "#0a4a45" if iso == PAIS else "#9ccbc6"; yo = iso == PAIS
        s += f'<path d="M{cx - ancho / 2:.1f},{y1} V{Y(v) + 1.6:.1f} q0,-1.6 1.6,-1.6 h{ancho - 3.2:.1f} q1.6,0 1.6,1.6 V{y1} Z" fill="{c}"/>'
        s += T(cx, Y(v) - 2.6, f"{v:.1f}", "middle", 6.3, 700 if yo else 500, halo=True)
        s += T(cx + 2.4, y1 + 7.5, nom, "end", 6.8, 700 if yo else 400, rot=-55)
    # rótulos de las líneas de referencia en el canal derecho, fuera de las barras
    s += T(x1 + 8, Y(float(p["region_l2"])) - 1.2, f"Region {p['region_l2']}", tam=6.8, peso=600)
    s += T(x1 + 8, Y(float(p["mundo_l2"])) + 6.8, f"World {p['mundo_l2']}", tam=6.8, peso=600)
    return s + "</svg>"


if __name__ == "__main__":
    p = calcular(); (INF / "fig/perfil_alc.svg").write_text(svg(p))
    (INF / "perfil.json").write_text(json.dumps({k: v for k, v in p.items() if k != "barras"}, ensure_ascii=False, indent=1))
    print("perfil:", p["hallazgo"])
