"""Paso 3: ESCO por API — jerarquía ISCO-08 completa (grupos 1–4 díg.), ocupaciones ESCO con código ISCO,
skills esenciales/opcionales por ocupación, y descripciones de ocupaciones y skills en EN y ES. Checkpoint por URI."""
import sys, json, time; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
import requests
lg = log("03_esco"); d = DATOS / "esco"; d.mkdir(parents=True, exist_ok=True)
API = "https://ec.europa.eu/esco/api/resource/"; IDIOMAS = ["en", "es"]; PAUSA = 0.25

def get(tipo, uri, lang, reint=4):
    for i in range(reint):
        try:
            r = requests.get(API + tipo, params={"uri": uri, "language": lang}, headers=UA, timeout=60)
            if r.status_code == 200: time.sleep(PAUSA); return r.json()
            if r.status_code in (404, 400): return None
            raise IOError(f"HTTP {r.status_code}")
        except Exception as e:
            lg.warning(f"{uri} {lang} intento {i+1}: {e}"); time.sleep(5 * 2 ** i)
    return None

def jsonl(p):  # lee un jsonl a dict por uri
    out = {}
    if p.exists():
        for l in open(p):
            if l.strip(): o = json.loads(l); out[o["uri"] + "|" + o.get("lang", "")] = o
    return out

# 1. Jerarquía ISCO desde la raíz: recorre narrowerConcept hasta los grupos de 4 dígitos
jer_p = d / "isco_jerarquia.jsonl"; jer = jsonl(jer_p)
cola = ["http://data.europa.eu/esco/isco/C" + str(i) for i in range(10)]
ocupaciones_uri = set()
with open(jer_p, "a") as f:
    while cola:
        uri = cola.pop(0)
        if uri + "|en" in jer:
            o = jer[uri + "|en"]
        else:
            j = get("concept", uri, "en")
            if not j: continue
            l = j.get("_links", {})
            o = {"uri": uri, "lang": "en", "codigo": j.get("code"), "titulo": j.get("title"),
                 "descripcion": (j.get("description", {}).get("en", {}) or {}).get("literal", ""),
                 "hijos": [h["uri"] for h in l.get("narrowerConcept", [])], "ocupaciones": [h["uri"] for h in l.get("narrowerOccupation", [])]}
            f.write(json.dumps(o, ensure_ascii=False) + "\n"); jer[uri + "|en"] = o
        cola.extend(o["hijos"]); ocupaciones_uri.update(o["ocupaciones"])
lg.info(f"jerarquía ISCO: {len(jer)} conceptos; {len(ocupaciones_uri)} ocupaciones de primer nivel")

# 2. Ocupaciones (y sus narrowerOccupation) en EN y ES, con skills enlazados
occ_p = d / "ocupaciones.jsonl"; occ = jsonl(occ_p); skills_uri = set(); cola = list(ocupaciones_uri); vistos = set()
with open(occ_p, "a") as f:
    while cola:
        uri = cola.pop(0)
        if uri in vistos: continue
        vistos.add(uri)
        for lang in IDIOMAS:
            if uri + "|" + lang in occ:
                o = occ[uri + "|" + lang]
            else:
                j = get("occupation", uri, lang)
                if not j: continue
                l = j.get("_links", {})
                o = {"uri": uri, "lang": lang, "codigo_isco": j.get("code"), "titulo": j.get("title"),
                     "alternativos": j.get("alternativeLabel", {}).get(lang, []) if isinstance(j.get("alternativeLabel"), dict) else [],
                     "descripcion": (j.get("description", {}).get(lang, {}) or {}).get("literal", ""),
                     "esenciales": [{"uri": s["uri"], "titulo": s["title"], "tipo": s.get("skillType", "").split("/")[-1]} for s in l.get("hasEssentialSkill", [])],
                     "opcionales": [{"uri": s["uri"], "titulo": s["title"], "tipo": s.get("skillType", "").split("/")[-1]} for s in l.get("hasOptionalSkill", [])],
                     "hijos": [h["uri"] for h in l.get("narrowerOccupation", [])]}
                f.write(json.dumps(o, ensure_ascii=False) + "\n"); occ[uri + "|" + lang] = o
            if lang == "en":
                cola.extend(o["hijos"]); skills_uri.update(s["uri"] for s in o["esenciales"] + o["opcionales"])
        if len(vistos) % 200 == 0: lg.info(f"ocupaciones {len(vistos)}, skills por bajar {len(skills_uri)}")
lg.info(f"ocupaciones: {len(vistos)}; skills únicos: {len(skills_uri)}")

# 3. Descripción de cada skill (EN y ES): son el «banco secundario» de enunciados
sk_p = d / "skills.jsonl"; sk = jsonl(sk_p)
with open(sk_p, "a") as f:
    for n, uri in enumerate(sorted(skills_uri)):
        for lang in IDIOMAS:
            if uri + "|" + lang in sk: continue
            j = get("skill", uri, lang)
            if not j: continue
            o = {"uri": uri, "lang": lang, "titulo": j.get("title"), "tipo": (j.get("skillType") or "").split("/")[-1],
                 "reusabilidad": (j.get("reuseLevel") or "").split("/")[-1],
                 "descripcion": (j.get("description", {}).get(lang, {}) or {}).get("literal", "")}
            f.write(json.dumps(o, ensure_ascii=False) + "\n"); sk[uri + "|" + lang] = o
        if n % 500 == 0: lg.info(f"skills {n}/{len(skills_uri)}")
for p in (jer_p, occ_p, sk_p): registrar(p, "ESCO API v1", "https://ec.europa.eu/esco/api/", nota="EN+ES")
# Tabla plana ISCO-08 4 díg. (los 436 grupos unitarios canónicos)
import pandas as pd
g = [o for o in jer.values() if o.get("codigo") and len(str(o["codigo"])) == 4]
pd.DataFrame([{"isco08": o["codigo"], "titulo": o["titulo"], "descripcion": o["descripcion"]} for o in g]).sort_values("isco08").to_csv(d / "isco08_grupos_unitarios.csv", index=False)
registrar(d / "isco08_grupos_unitarios.csv", "derivado: 03_esco.py", nota=f"{len(g)} grupos unitarios")
lg.info(f"ISCO-08 grupos unitarios: {len(g)} (esperados 436)")
