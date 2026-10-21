"""Paso 5: Banco Mundial — países, grupo de ingreso, PIB pc PPP, población, empleo."""
import sys, json; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
import pandas as pd
lg = log("05_worldbank"); d = DATOS / "worldbank"; d.mkdir(parents=True, exist_ok=True)

def wb(url, nombre):
    p = d / f"{nombre}.json"
    if descargar(url, p, "Banco Mundial API", lg, minimo=100):
        j = json.loads(p.read_text()); return j[1] if isinstance(j, list) and len(j) > 1 else []
    return []

paises = wb("https://api.worldbank.org/v2/country?format=json&per_page=400", "paises")
pd.DataFrame([{"iso3": c["id"], "iso2": c["iso2Code"], "pais": c["name"], "region": c["region"]["value"],
               "ingreso": c["incomeLevel"]["value"], "ingreso_id": c["incomeLevel"]["id"], "capital": c["capitalCity"]} for c in paises
              if c["region"]["value"] != "Aggregates"]).to_csv(d / "paises_ingreso.csv", index=False)
registrar(d / "paises_ingreso.csv", "derivado: 05_worldbank.py")
for ind, nombre in [("NY.GDP.PCAP.PP.KD", "pib_pc_ppp"), ("SP.POP.TOTL", "poblacion"), ("SL.EMP.TOTL.SP.ZS", "empleo_pob"),
                    ("SL.TLF.TOTL.IN", "fuerza_laboral"), ("IT.NET.USER.ZS", "internet"), ("SL.ISV.IFRM.ZS", "informalidad")]:
    filas = wb(f"https://api.worldbank.org/v2/country/all/indicator/{ind}?format=json&date=2015:2025&per_page=20000", nombre)
    if filas:
        pd.DataFrame([{"iso3": r["countryiso3code"], "anio": int(r["date"]), "valor": r["value"]} for r in filas if r["countryiso3code"]]
                     ).to_csv(d / f"{nombre}.csv", index=False); registrar(d / f"{nombre}.csv", f"WB {ind}")
lg.info("Banco Mundial listo")
