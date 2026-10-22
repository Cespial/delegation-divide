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
NOMBRE = {"Puerto Rico (US)": "Puerto Rico", "Bahamas, The": "Bahamas", "St. Lucia": "Saint Lucia", "Curacao": "Curaçao",
          # nombres de uso común para el sitio (fuera de América Latina no salen en el informe)
          "Naoero": "Nauru", "Turkiye": "Türkiye", "Cote d'Ivoire": "Côte d’Ivoire", "Gambia, The": "The Gambia", "Egypt, Arab Rep.": "Egypt",
          "Iran, Islamic Rep.": "Iran", "Congo, Dem. Rep.": "DR Congo", "Lao PDR": "Laos", "Kyrgyz Republic": "Kyrgyzstan", "Slovak Republic": "Slovakia",
          "Somalia, Fed. Rep.": "Somalia", "Korea, Rep.": "South Korea", "Brunei Darussalam": "Brunei", "Russian Federation": "Russia"}
TINTA, GRIS, FIL = "#1a1918", "#5d636b", "#dcdad6"


# nombres de región para el texto (las de la tabla son las del Banco Mundial, con «&» y espacios sobrantes)
REGIONES = {"Latin America & Caribbean": "Latin America and the Caribbean", "Europe & Central Asia": "Europe and Central Asia",
            "East Asia & Pacific": "East Asia and Pacific", "Sub-Saharan Africa": "Sub-Saharan Africa", "South Asia": "South Asia",
            "North America": "North America", "Middle East, North Africa, Afghanistan & Pakistan": "the Middle East, North Africa, Afghanistan and Pakistan"}


def calcular(pais=PAIS):
    """Perfil de un país frente a su región (Banco Mundial), los países de ingreso alto y el mundo. El informe lo pide para Colombia;
    el sitio web (sitio/datos/exportar.py) para los 146 países, con la misma función."""
    d = pd.read_csv(R / "salidas/indice_pais_detalle.csv"); d["nombre"] = d.pais.map(lambda x: NOMBRE.get(x, x)); d["region"] = d.region.str.strip()
    for c in ("adi_l2", "adi_l3"): d[c] = 100 * d[c]
    col = d[d.iso3 == pais].iloc[0]; reg = d[d.region == col.region]; nom_reg = REGIONES.get(col.region, col.region)
    pond = lambda x, c: (x[c] * x.empleo_total).sum() / x.empleo_total.sum()
    def fila(c, nombre, unidad, fmt, mayor_mejor=True, ponderar=True, fuente=""):
        x = reg.dropna(subset=[c]); orden = x.sort_values(c, ascending=not mayor_mejor).reset_index(drop=True)
        hay = pd.notna(col[c]); puesto = int(orden.index[orden.iso3 == pais][0]) + 1 if hay else None; mejor = orden.iloc[0] if len(orden) else None
        agr = (lambda z: pond(z.dropna(subset=[c]), c)) if ponderar else (lambda z: z[c].mean())
        return dict(nombre=nombre, unidad=unidad, col=fmt(col[c]) if hay else "–", puesto=f"{puesto} of {len(x)}" if hay else "–",
                    mejor=f"{mejor.nombre} ({fmt(mejor[c])})" if mejor is not None else "–", region=fmt(agr(reg)) if len(x) else "–",
                    alto=fmt(agr(d[d.ingreso == "high"])), mundo=fmt(agr(d)), fuente=fuente, v=float(col[c]) if hay else None)
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
    mundo, alto = float(a["mundo"]), float(a["alto"]); dif = alto - a["v"]
    sujeto = f"{col.nombre} ranks {a['puesto'].split()[0]} of {n_reg} countries in {nom_reg}" if n_reg > 1 else f"{col.nombre} is the only country of {nom_reg} in the atlas"
    hallazgo = (f"{sujeto}: {a['col']}% of its task time is at least "
                f"partly delegable, {'above' if a['v'] > mundo else 'below'} the world figure of {a['mundo']}% and {abs(dif):.1f} points "
                f"{'below' if dif > 0 else 'above'} high-income countries.")
    barras = reg.sort_values("adi_l2", ascending=False)[["iso3", "nombre", "adi_l2"]].values.tolist()
    k = [b[0] for b in barras].index(pais)
    if n_reg == 1: hallazgo_fig = f"{col.nombre} is the only country of {nom_reg} in the atlas."
    elif k == 0: hallazgo_fig = f"{col.nombre} leads {nom_reg} at {barras[0][2]:.1f}%, ahead of {barras[1][1]} ({barras[1][2]:.1f}%); {barras[-1][1]} closes the region at {barras[-1][2]:.1f}%."
    elif k == n_reg - 1: hallazgo_fig = f"{col.nombre} closes {nom_reg} at {barras[k][2]:.1f}%, behind {barras[k - 1][1]} ({barras[k - 1][2]:.1f}%); {barras[0][1]} leads the region at {barras[0][2]:.1f}%."
    else:
        ant, sig = barras[k - 1], barras[k + 1]
        hallazgo_fig = (f"{col.nombre} sits between {ant[1]} ({ant[2]:.1f}%) and {sig[1]} ({sig[2]:.1f}%); {barras[0][1]} leads the region at {barras[0][2]:.1f}% "
                        f"and {barras[-1][1]} closes it at {barras[-1][2]:.1f}%.")
    return dict(grupos=grupos, hallazgo=hallazgo, hallazgo_fig=hallazgo_fig, n_region=n_reg, intervalo=f"{lo}–{hi}", anio=int(col.anio), resolucion=int(col.resolucion),
                region_l2=a["region"], mundo_l2=a["mundo"], barras=barras, iso3=pais, nombre=col.nombre, region=col.region, region_nombre=nom_reg)


def svg(p):
    # barras horizontales, una fila por país (los nombres se leen sin girar); viewBox en puntos al ancho de la caja (7 in = 504 pt)
    W, x0, x1, top, paso, alto, y0 = 504, 118, 470, 60, 9.6, 6.4, 22
    filas = p["barras"]; n = len(filas); H = y0 + paso * n + 16
    X = lambda v: x0 + (x1 - x0) * v / top
    T = lambda x, y, s, anc="start", tam=7, peso=400, col=TINTA, halo=False: (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Barlow" font-size="{tam}" '
         f'font-weight="{peso}" fill="{col}" text-anchor="{anc}"' + (' stroke="#fff" stroke-width="2.2" paint-order="stroke"' if halo else "") + f">{s}</text>")
    s = f'<svg viewBox="0 0 {W} {H:.0f}" xmlns="http://www.w3.org/2000/svg">'
    for v in range(0, top + 1, 10):
        s += f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{y0 - 3}" y2="{H - 13:.1f}" stroke="{FIL}" stroke-width="{0.8 if v == 0 else 0.4}"/>' + T(X(v), H - 4, f"{v}", "middle", 6.6, col=GRIS)
    s += T(x1 + 6, H - 4, "%", tam=6.6, col=GRIS)
    et = ""
    for k, (iso, nom, v) in enumerate(filas):
        y = y0 + paso * k; c = "#0a4a45" if iso == PAIS else "#9ccbc6"; yo = iso == PAIS
        s += f'<path d="M{x0},{y:.1f} H{X(v) - 1.6:.1f} q1.6,0 1.6,1.6 V{y + alto - 1.6:.1f} q0,1.6 -1.6,1.6 H{x0} Z" fill="{c}"/>'
        s += T(x0 - 6, y + 5.4, nom, "end", 7, 700 if yo else 400)
        et += T(X(v) + 3, y + 5.4, f"{v:.1f}", tam=6.6, peso=700 if yo else 500, halo=True)
    # líneas de referencia sobre las barras y bajo las cifras (el halo blanco de la cifra corta la línea); rótulos arriba
    ref = sorted(((float(p["region_l2"]), "4 2.4", f"Region {p['region_l2']}"), (float(p["mundo_l2"]), "1.2 2", f"World {p['mundo_l2']}")))
    for (val, dash, rot), anc in zip(ref, ("end", "start")):  # la línea de la izquierda rotula hacia la izquierda y la otra hacia la derecha
        s += f'<line x1="{X(val):.1f}" x2="{X(val):.1f}" y1="{y0 - 9}" y2="{H - 13:.1f}" stroke="{TINTA}" stroke-width="0.7" stroke-dasharray="{dash}"/>'
        s += T(X(val) + (-3 if anc == "end" else 3), y0 - 11, rot, anc, 6.8, 600)
    return s + et + "</svg>"


if __name__ == "__main__":
    p = calcular(); (INF / "fig/perfil_alc.svg").write_text(svg(p))
    (INF / "perfil.json").write_text(json.dumps({k: v for k, v in p.items() if k != "barras"}, ensure_ascii=False, indent=1))
    print("perfil:", p["hallazgo"])
