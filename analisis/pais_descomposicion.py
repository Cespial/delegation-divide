"""Paso 21: descomposición por país del ADI publicado, para el sitio (no entra en la API v2026.1 ni en el paper).
Con la misma matriz país × ISCO 4 díg. de indice.py (pesos D1) escribe salidas/pais_grupos.csv:
  por país y gran grupo ISCO (1–9): participación en el empleo, ADI del grupo con la mezcla de ese país y su aporte en puntos
  (Σ aportes = ADI del país), y salidas/pais_barreras.csv: las cuatro barreras ponderadas por el empleo de cada país.
Comprueba que la suma reproduce salidas/indice_pais_detalle.csv: tolerancia 0,01 puntos, porque el ADI por ocupación
se lee del CSV publicado (4 decimales) y no de la matriz en memoria; el sitio muestra un decimal."""
import sys
sys.path.insert(0, "noche"); sys.path.insert(0, "analisis")
from comun import *
import numpy as np, pandas as pd
from indice import cargar_atlas, matriz_paises, pesos_d1, vectores_peso

lg = log("21_pais_descomposicion")
SAL = RAIZ / "salidas"
BARRERAS = ["barrera_fisica", "barrera_responsabilidad", "barrera_confianza", "barrera_acceso"]


def main():
    occ = pd.read_csv(SAL / "indice_isco_detalle.csv", dtype={"isco08": str})
    isco = occ.isco08.values
    paises, meta = cargar_atlas()
    v_geih, v_oes = vectores_peso(isco)
    M, E = matriz_paises(isco, paises, pesos_d1(meta, v_geih, v_oes))
    ciso = sorted(paises.iso3.unique())
    gg = occ.isco08.str[0].values

    filas = []
    for k in sorted(set(gg)):
        u = gg == k
        share = M[:, u].sum(1)
        aporte = M[:, u] @ occ.adi_l2.values[u]
        aporte3 = M[:, u] @ occ.adi_l3.values[u]
        for ci, c in enumerate(ciso):
            filas.append({"iso3": c, "gg": k, "empleo_share": 100 * share[ci],
                          "adi_l2_grupo": 100 * aporte[ci] / share[ci] if share[ci] > 0 else np.nan,
                          "contrib_l2": 100 * aporte[ci], "contrib_l3": 100 * aporte3[ci]})
    G = pd.DataFrame(filas)
    B = pd.DataFrame(100 * (M @ occ[BARRERAS].values), columns=BARRERAS); B.insert(0, "iso3", ciso)

    ref = pd.read_csv(SAL / "indice_pais_detalle.csv").set_index("iso3")
    suma = G.groupby("iso3").contrib_l2.sum()
    dif = (suma - 100 * ref.adi_l2.reindex(suma.index)).abs().max()
    if dif > 0.01: sys.exit(f"la descomposición no reproduce el ADI publicado: diferencia máxima {dif:.2e}")
    if (G.groupby("iso3").empleo_share.sum() - 100).abs().max() > 1e-6: sys.exit("las participaciones no suman 100")
    G.to_csv(SAL / "pais_grupos.csv", index=False, float_format="%.4f")
    B.to_csv(SAL / "pais_barreras.csv", index=False, float_format="%.4f")
    lg.info(f"{len(ciso)} países × {G.gg.nunique()} grandes grupos; diferencia máxima con el ADI publicado {dif:.4f} puntos")


if __name__ == "__main__":
    main()
