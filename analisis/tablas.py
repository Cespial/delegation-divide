"""Paso 22: tablas LaTeX (booktabs) en articulo/tablas/: tab2_cobertura (datos/atlas/paises_meta.csv por grupo de ingreso),
tab3_ocupaciones (10 ISCO 4 díg. más y menos delegables) y tab4_h1 (regresiones H1/H2, salidas/regresiones.json).
La Tabla 1 comparativa vive en articulo/secciones/02_delegacion.tex. Las cifras de las tablas salen de los datos, no de \\cifra."""
import sys, json; sys.path.insert(0, "noche")
from comun import *
import numpy as np, pandas as pd
lg = log("22_tablas"); SAL = RAIZ / "salidas"; TAB = RAIZ / "articulo/tablas"; TAB.mkdir(parents=True, exist_ok=True)
SINT = pd.read_csv(SAL / "adi_isco.csv").sintetico.astype(str).str.lower().eq("true").any()
MARCA = r" \textbf{Synthetic placeholder values, not results.}" if SINT else ""
ING = [("High income", "High"), ("Upper middle income", "Upper-middle"), ("Lower middle income", "Lower-middle"), ("Low income", "Low")]
esc = lambda s: str(s).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")


def escribir(nombre, txt):
    p = TAB / f"{nombre}.tex"; p.write_text(f"% generado por analisis/tablas.py — no editar a mano\n{txt}\n")
    registrar(p, "derivado: tablas.py", nota="SINTÉTICO" if SINT else ""); lg.info(p.name)


def tab2():
    m = pd.read_csv(DATOS / "atlas/paises_meta.csv")
    filas = []
    for ing, et in ING + [(None, "Total")]:
        d = m if ing is None else m[m.ingreso == ing]
        filas.append(f"{et} & {len(d)} & {(d.resolucion == 2).sum()} & {(d.resolucion == 1).sum()} & {int(d.anio.median())} & "
                     f"{d.empleo_total.sum() / 1e6:,.0f} & {d.pib_pc_ppp.notna().sum()} \\\\")
    filas.insert(-1, r"\midrule")
    escribir("tab2_cobertura", r"""\begin{table}[t]
\centering\small
\caption{Coverage of the country atlas: countries with ILOSTAT employment by ISCO-08 occupation for a year from 2019 onward, by World Bank income group (FY2026). Resolution is the finest ISCO-08 level the country reports.""" + MARCA + r"""}
\label{tab:cobertura}
\begin{tabular}{lrrrrrr}
\toprule
Income group & Countries & 2-digit & 1-digit & Median year & Employment (M) & With GDP pc \\
\midrule
""" + "\n".join(filas) + r"""
\bottomrule
\end{tabular}
\end{table}""")


def tab3():
    o = pd.read_csv(SAL / "adi_isco.csv", dtype={"isco08": str}).sort_values(["adi_l2", "adi_share"], ascending=False)
    fila = lambda r: f"{r.isco08} & {esc(r.titulo)} & {100 * r.adi_l2:.1f} & {100 * r.adi_l3:.1f} & {r.adi_share:.1f} & [{r.ic_lo:.1f}, {r.ic_hi:.1f}] & {int(r.n_tareas)} \\\\"
    top = "\n".join(fila(r) for r in o.head(10).itertuples()); bot = "\n".join(fila(r) for r in o.tail(10).itertuples())
    escribir("tab3_ocupaciones", r"""\begin{table}[t]
\centering\footnotesize
\caption{The ten most and ten least delegable ISCO-08 unit groups. ADI: task-weighted share at L2 or L3; ADI3: at L3; ADIs: weighted mean share of task time delegable, with 95\% bootstrap interval (1,000 draws, tasks resampled within occupation).""" + MARCA + r"""}
\label{tab:ocupaciones}
\begin{tabular}{lp{5.6cm}rrrcr}
\toprule
ISCO & Unit group & ADI & ADI3 & ADIs & 95\% CI (ADIs) & Tasks \\
\midrule
\multicolumn{7}{l}{\emph{Most delegable}}\\
""" + top + r"""
\midrule
\multicolumn{7}{l}{\emph{Least delegable}}\\
""" + bot + r"""
\bottomrule
\end{tabular}
\end{table}""")


def tab4():
    r = json.load(open(SAL / "regresiones.json"))
    def celda(m, k, una_cola=True):
        if m not in r or k not in r[m]["coef"]: return "", ""
        b, se = r[m]["coef"][k], r[m]["se"][k]; p = r[m].get("p_una_cola", {}).get(k)
        est = "" if p is None else ("***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "")
        return f"{b:.2f}{est}".replace("-", "$-$"), f"({se:.2f})"
    filas = []
    for k, et in (("lpib", "log GDP per capita (PPP)"), ("upper-middle", "Upper-middle income"), ("lower-middle", "Lower-middle income"), ("low", "Low income"), ("const", "Constant")):
        cs = [celda(m, k) for m in ("h1a", "h1b", "h1a_iguales", "h2")]
        filas.append(f"{et} & " + " & ".join(c[0] for c in cs) + r" \\")
        filas.append(" & " + " & ".join(c[1] for c in cs) + r" \\")
    n = " & ".join(str(r[m]["n"]) if m in r else "" for m in ("h1a", "h1b", "h1a_iguales", "h2"))
    r2 = " & ".join(f"{r[m]['r2']:.2f}" if m in r else "" for m in ("h1a", "h1b", "h1a_iguales", "h2"))
    escribir("tab4_h1", r"""\begin{table}[t]
\centering\small
\caption{Country-level regressions. Columns (1)--(3): $\mathrm{ADI}_c$ in percent (H1); column (3) uses equal weights within reported groups (sensitivity). Column (4): standardized gap $z(\mathrm{ADI}_c)-z(\text{usage}_c)$ with Anthropic Economic Index usage per working-age person (H2). Reference category: high income. Standard errors in parentheses; stars refer to the preregistered one-sided tests (* $p<0.05$, ** $p<0.01$, *** $p<0.001$).""" + MARCA + r"""}
\label{tab:h1}
\begin{tabular}{lcccc}
\toprule
 & (1) H1 & (2) H1 & (3) H1, equal weights & (4) H2 gap \\
\midrule
""" + "\n".join(filas) + r"""
\midrule
Countries & """ + n + r""" \\
$R^2$ & """ + r2 + r""" \\
\bottomrule
\end{tabular}
\end{table}""")


if __name__ == "__main__":
    for f in (tab2, tab3, tab4):
        try: f()
        except Exception as e: lg.error(f"{f.__name__}: {e}")
