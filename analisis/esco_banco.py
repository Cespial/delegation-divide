"""Banco secundario ESCO para la robustez preregistrada (OSF 344-83: «robustness with ESCO essential skills instead of O*NET
tasks», exploratorio). Lee datos/esco_skills_isco.parquet (analisis/esco_isco.py) y datos/esco/skills.jsonl (descripciones).

Salidas:
  datos/esco_banco.parquet       una fila por skill ESENCIAL única (esencial para ≥ 1 ocupación ESCO):
                                 task_id (índice en orden de skill_uri + 10_000_000, no choca con O*NET), skill_uri, texto
                                 (etiqueta EN + «: » + descripción EN, máx. 300 caracteres), titulo (ocupación ESCO de referencia),
                                 n_ocupaciones, n_isco.
  datos/esco_pares_isco.parquet  puente isco08 × task_id, pesos iguales dentro de cada ISCO (Σ peso = 1 por ISCO).

Decisiones (documentadas aquí y en el paper):
  * Solo skillType «skill» (= ESCO «skill/competence»); se excluye «knowledge», porque la rúbrica califica actividades que se
    pueden delegar y un saber («quality standards») no es una actividad. La tipología viene de los enlaces hasEssentialSkill de
    cada ocupación (skills.jsonl trae el tipo vacío).
  * titulo: el grupo ISCO en el que la skill es esencial para más ocupaciones ESCO (empate → código menor); dentro de él, la
    ocupación ESCO de título EN alfabéticamente primero. Es el contexto ocupacional que recibe la rúbrica.
  * Congelado: si ya existen puntuaciones en scoring/salidas/esco/ no se reescribe (los task_id y textos deben coincidir con lo
    puntuado) salvo con --forzar.
"""
import sys, json, argparse; sys.path.insert(0, "noche")
from comun import *
import pandas as pd

lg = log("esco_banco")
BASE = 10_000_000; MAXC = 300
ap = argparse.ArgumentParser(); ap.add_argument("--forzar", action="store_true"); a = ap.parse_args()
dest, puente = DATOS / "esco_banco.parquet", DATOS / "esco_pares_isco.parquet"
sal = RAIZ / "scoring/salidas/esco"
if dest.exists() and not a.forzar and sal.exists() and any(sal.glob("*.jsonl")):
    lg.info(f"banco congelado: ya hay puntuaciones en {sal}; no se reescribe (use --forzar)"); sys.exit(0)

s = pd.read_parquet(DATOS / "esco_skills_isco.parquet")
ocu = pd.read_parquet(DATOS / "esco_ocupaciones_isco.parquet")
e = s[(s.relacion == "esencial")]
n_know = e[e.tipo == "knowledge"].skill_uri.nunique()
e = e[e.tipo == "skill"].drop_duplicates(["ocupacion_uri", "skill_uri"])
e = e.merge(ocu[["ocupacion_uri", "titulo_en"]], on="ocupacion_uri", how="left")

desc = {}
p = DATOS / "esco/skills.jsonl"
if p.exists():
    for l in open(p):
        try: o = json.loads(l)
        except json.JSONDecodeError: continue
        if o.get("lang") == "en" and o.get("descripcion"): desc[o["uri"]] = " ".join(o["descripcion"].split())

def texto(lab, uri):
    lab = " ".join(str(lab).split()); t = lab[:1].upper() + lab[1:]
    d = desc.get(uri)
    if d: t = f"{t}: {d}"
    if len(t) > MAXC: t = t[:MAXC - 3].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return t

# ocupación de referencia
c = e.groupby(["skill_uri", "isco08"]).size().rename("n").reset_index().sort_values(["skill_uri", "n", "isco08"], ascending=[True, False, True])
top = c.drop_duplicates("skill_uri").set_index("skill_uri").isco08
ref = e[e.isco08.values == top.reindex(e.skill_uri).values].sort_values(["skill_uri", "titulo_en"]).drop_duplicates("skill_uri").set_index("skill_uri").titulo_en

uris = sorted(e.skill_uri.unique())
lab = e.drop_duplicates("skill_uri").set_index("skill_uri").skill_en
b = pd.DataFrame({"task_id": BASE + pd.RangeIndex(len(uris)), "skill_uri": uris})
b["texto"] = [texto(lab[u], u) for u in uris]
b["titulo"] = ref.reindex(uris).values
b["con_descripcion"] = b.skill_uri.isin(desc.keys())
b["n_ocupaciones"] = e.groupby("skill_uri").ocupacion_uri.nunique().reindex(uris).values
b["n_isco"] = e.groupby("skill_uri").isco08.nunique().reindex(uris).values
b.to_parquet(dest, index=False)

pr = e.drop_duplicates(["isco08", "skill_uri"]).merge(b[["skill_uri", "task_id"]], on="skill_uri")[["isco08", "task_id"]]
pr["peso"] = 1 / pr.groupby("isco08").task_id.transform("size")
pr = pr.sort_values(["isco08", "task_id"]).reset_index(drop=True); pr.to_parquet(puente, index=False)

nota = (f"{len(b)} skills/competencias esenciales (excluidas {n_know} knowledge), {pr.isco08.nunique()} ISCO-08; "
        f"descripción EN {b.con_descripcion.mean():.1%} (skills.jsonl {len(desc)} skills)")
registrar(dest, "derivado: esco_banco.py", nota=nota); registrar(puente, "derivado: esco_banco.py", nota=f"{len(pr)} pares isco08 × skill")
lg.info(nota + f"; pares {len(pr):,}; skills por ISCO mediana {pr.groupby('isco08').size().median():.0f}")
