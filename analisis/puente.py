"""Puente O*NET-SOC 2019 → SOC 2010 → ISCO-08 4 díg. Copia literal de la lógica de datos/construir_crosswalk.py
(que no se puede importar: corre al cargarse). Si cambia allí, cambiar aquí. Lo usan comparadores_isco.py e indice.py."""
import sys; sys.path.insert(0, "noche")
from comun import DATOS
import pandas as pd

C = DATOS / "crosswalks"
NUEVAS = {"15-1299.04": 151199, "15-1299.05": 151199, "15-1299.06": 151199, "15-1299.07": 151199}


def ibs():
    """SOC 2010 (int) → ISCO-08 (str 4 díg.) con peso 1/k."""
    x = pd.read_stata(C / "ibs/soc10_isco08.dta"); x["soc10"] = x.soc10.astype(int); x["isco08"] = x.isco08.astype(str).str.zfill(4)
    x["peso_map"] = 1 / x.groupby("soc10").isco08.transform("nunique")
    return x[["soc10", "isco08", "peso_map"]]


def rescatador(conocidos):
    """SOC 2010 que el IBS no trae → mismo grupo amplio, «all other» primero (idéntico a construir_crosswalk.py)."""
    def rescatar(c):
        if c in conocidos: return c
        for cand in [c // 10 * 10 + 9] + sorted(k for k in conocidos if k // 10 == c // 10) + sorted(k for k in conocidos if k // 100 == c // 100):
            if cand in conocidos: return cand
        return c
    return rescatar


def puente():
    """onet19 → isco08 con peso_map (suma 1 por onet19)."""
    x = ibs()
    w = pd.read_csv(C / "onet_2010_to_2019.csv").rename(columns={"O*NET-SOC 2010 Code": "onet10", "O*NET-SOC 2019 Code": "onet19"})
    w["soc10"] = w.onet10.str.replace(r"\D", "", regex=True).str[:6].astype(int)
    w["soc10_orig"] = w.soc10; w["soc10"] = w.soc10.map(rescatador(set(x.soc10)))
    w = pd.concat([w, pd.DataFrame([{"onet19": k, "soc10": v} for k, v in NUEVAS.items() if k not in set(w.onet19)])], ignore_index=True)
    w["soc10_orig"] = w.soc10_orig.fillna(w.soc10).astype(int)
    p = w[["onet19", "soc10", "soc10_orig"]].drop_duplicates(["onet19", "soc10"]).merge(x, on="soc10")
    p["peso_map"] /= p.groupby("onet19").soc10.transform("nunique")
    return p


def soc_a_int(s):
    """'11-1011' / '11-1011.00' / 111011 → 111011."""
    return pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True).str[:6], errors="coerce")
