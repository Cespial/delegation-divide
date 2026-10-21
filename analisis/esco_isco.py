"""ESCO v1 → ISCO-08 4 díg. Lee datos/esco/ocupaciones.jsonl (EN y ES, con skills esenciales/opcionales enlazados) y, si
existe, datos/esco/skills.jsonl (títulos y tipo). Salida: datos/esco_skills_isco.parquet (isco08, ocupacion_uri, skill_uri,
skill_en, skill_es, tipo, relacion) y datos/esco_ocupaciones_isco.parquet (ocupaciones ESCO por ISCO). Tolera skills ausentes."""
import sys, json; sys.path.insert(0, "noche")
from comun import *
import pandas as pd
lg = log("esco_isco"); E = DATOS / "esco"

def leer(p):
    if not p.exists(): return []
    out = []
    for l in open(p):
        try: out.append(json.loads(l))
        except json.JSONDecodeError: pass   # la captura puede estar escribiendo la última línea
    return out

occ = leer(E / "ocupaciones.jsonl")
if not occ: lg.error("no hay datos/esco/ocupaciones.jsonl"); sys.exit(0)
o = pd.DataFrame(occ)
o["isco08"] = o.codigo_isco.astype(str).str.extract(r"^(\d{4})")[0]
o = o.dropna(subset=["isco08"]).drop_duplicates(["uri", "lang"], keep="last")
en, es = o[o.lang == "en"], o[o.lang == "es"]
ocu = en[["uri", "isco08", "codigo_isco", "titulo", "descripcion"]].rename(columns={"uri": "ocupacion_uri", "titulo": "titulo_en"})
ocu = ocu.merge(es[["uri", "titulo"]].rename(columns={"uri": "ocupacion_uri", "titulo": "titulo_es"}), on="ocupacion_uri", how="left")
ocu.to_parquet(DATOS / "esco_ocupaciones_isco.parquet", index=False)
registrar(DATOS / "esco_ocupaciones_isco.parquet", "derivado: esco_isco.py", nota=f"{len(ocu)} ocupaciones ESCO, {ocu.isco08.nunique()} ISCO")

filas = []
for lang, d in (("en", en), ("es", es)):
    for r in d.itertuples():
        for rel in ("esenciales", "opcionales"):
            for s in (getattr(r, rel) or []):
                filas.append({"ocupacion_uri": r.uri, "isco08": r.isco08, "skill_uri": s["uri"], "lang": lang, "titulo": s.get("titulo"),
                              "tipo": s.get("tipo"), "relacion": "esencial" if rel == "esenciales" else "opcional"})
s = pd.DataFrame(filas)
if s.empty:
    lg.warning("ocupaciones sin skills enlazados: solo se escribe esco_ocupaciones_isco.parquet"); sys.exit(0)
base = s[s.lang == "en"].drop(columns="lang").rename(columns={"titulo": "skill_en"})
tes = s[s.lang == "es"][["skill_uri", "titulo"]].drop_duplicates("skill_uri").rename(columns={"titulo": "skill_es"})
base = base.merge(tes, on="skill_uri", how="left")
sk = leer(E / "skills.jsonl")   # títulos canónicos si la captura de skills ya terminó
if sk:
    k = pd.DataFrame(sk).drop_duplicates(["uri", "lang"], keep="last")
    for lang, col in (("en", "skill_en"), ("es", "skill_es")):
        m = k[k.lang == lang].set_index("uri").titulo
        base[col] = base.skill_uri.map(m).fillna(base[col])
    lg.info(f"skills.jsonl: {k.uri.nunique()} skills con título")
else:
    lg.warning("datos/esco/skills.jsonl aún no existe: títulos tomados de los enlaces de cada ocupación")
base = base.drop_duplicates(["isco08", "ocupacion_uri", "skill_uri"])
base.to_parquet(DATOS / "esco_skills_isco.parquet", index=False)
registrar(DATOS / "esco_skills_isco.parquet", "derivado: esco_isco.py", nota=f"{len(base)} pares ocupación-skill")
lg.info(f"ESCO: {len(ocu)} ocupaciones → {ocu.isco08.nunique()} ISCO-08; pares ocupación-skill {len(base):,}; skills únicos "
        f"{base.skill_uri.nunique():,}; esenciales {(base.relacion == 'esencial').mean():.0%}; con título ES {base.skill_es.notna().mean():.0%}")
