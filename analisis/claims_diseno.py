"""Claims de DISEÑO (no resultados): conteos que el texto cita y que se derivan de los insumos, no de las puntuaciones.
Salida: salidas_diseno/claims_diseno.jsonl (un claim por línea, mismo formato que salidas/claims.jsonl, ids con prefijo diseno.).
articulo/generar_cifras.py lee este archivo además de salidas/claims.jsonl. No lee nada de scoring/ ni de salidas/.
Fuentes: datos/tareas_unicas.parquet, datos/pares_isco_tarea.parquet, datos/crosswalks/ (O*NET 2010→2019, IBS SOC10→ISCO08,
matriz previa), datos/ilostat/emp*_isco_todos.csv, datos/atlas/paises_meta.csv, validacion/muestra_1500.csv. Los valores del
piloto (descartado) se copian de docs/MODELOS.md, donde quedaron fijados antes del registro."""
import json, pathlib
import pandas as pd
R = pathlib.Path(__file__).resolve().parents[1]; D = R / "datos"; OUT = R / "salidas_diseno"; OUT.mkdir(exist_ok=True)
C = []
def claim(i, v, fuente): C.append({"id": "diseno." + i, "valor": v if isinstance(v, (str, float)) else int(v), "fuente": fuente, "sintetico": False})

# O*NET 30.2
t = pd.read_parquet(D / "tareas_unicas.parquet")
claim("onet.tareas", len(t), "datos/tareas_unicas.parquet")
claim("onet.ocupaciones", t.onet19.nunique(), "datos/tareas_unicas.parquet: O*NET-SOC 2019 distintos")

# Pares (grupo ISCO, tarea) del puente
p = pd.read_parquet(D / "pares_isco_tarea.parquet"); f = "datos/pares_isco_tarea.parquet"
claim("puente.pares", len(p), f); claim("puente.tareas", p["Task ID"].nunique(), f); claim("puente.isco", p.isco08.nunique(), f)
claim("puente.imputados", p[p.imputado].isco08.nunique(), f)
claim("puente.conjuntos", p.groupby("isco08")["Task ID"].apply(frozenset).nunique(), f + ": conjuntos de tareas distintos")
n = p.groupby("isco08")["Task ID"].nunique()
claim("puente.tareas_grupo.mediana", int(n.median()), f); claim("puente.tareas_grupo.min", n.min(), f); claim("puente.tareas_grupo.max", n.max(), f)
# Agricultura: tareas cuyo grupo de mayor peso está en el gran grupo 6 (misma regla que validacion/muestra.py)
q = p[~p.imputado].sort_values("peso", ascending=False).drop_duplicates("Task ID")
agro = set(q.loc[q.isco08.str[0] == "6", "Task ID"])
claim("agro.tareas", len(agro), f + ": gran grupo de mayor peso = 6")
m = pd.read_csv(R / "validacion/muestra_1500.csv")
claim("agro.en_muestra", len(agro & set(m.task_id)), "validacion/muestra_1500.csv")

# O*NET-SOC 2010 → 2019
c = pd.read_csv(D / "crosswalks/onet_2010_to_2019.csv"); f = "datos/crosswalks/onet_2010_to_2019.csv"
claim("onet10_19.codigos2010", c["O*NET-SOC 2010 Code"].nunique(), f); claim("onet10_19.codigos2019", c["O*NET-SOC 2019 Code"].nunique(), f)
claim("onet10_19.multiples", (c.groupby("O*NET-SOC 2019 Code")["O*NET-SOC 2010 Code"].nunique() > 1).sum(), f + ": códigos 2019 con varios ancestros 2010")

# IBS SOC 2010 → ISCO-08
s = pd.read_stata(D / "crosswalks/ibs/soc10_isco08.dta"); f = "datos/crosswalks/ibs/soc10_isco08.dta"; k = s.groupby("soc10").isco08.nunique()
claim("ibs.filas", len(s), f); claim("ibs.soc", s.soc10.nunique(), f); claim("ibs.isco", s.isco08.nunique(), f)
claim("ibs.k1", (k == 1).sum(), f); claim("ibs.k2", (k == 2).sum(), f); claim("ibs.k3", (k == 3).sum(), f)
claim("ibs.k4mas", (k >= 4).sum(), f); claim("ibs.kmax", k.max(), f)

# Matriz previa (trabajo anterior de los autores)
mt = pd.read_parquet(D / "crosswalks/occupation_task_matrix.parquet", columns=["CIUO_code", "Task ID"]); f = "datos/crosswalks/occupation_task_matrix.parquet"
claim("previo.ocupaciones", mt.CIUO_code.nunique(), f)
claim("previo.conjuntos", mt.groupby("CIUO_code")["Task ID"].apply(frozenset).nunique(), f)
claim("previo.ocupaciones_por_tarea.mediana", int(mt.groupby("Task ID").CIUO_code.nunique().median()), f)

# ILOSTAT: países con empleo por ISCO-08 (total por sexo, grupos con código de ocupación, sin «X»)
for res, arch, col, pat in ((1, "emp_isco_todos.csv", "OCU", r"OCU_ISCO08_[0-9]$"), (2, "emp2_isco_todos.csv", "OC2", r"OC2_ISCO08_[0-9]{2}$")):
    e = pd.read_csv(D / "ilostat" / arch, usecols=["REF_AREA", "SEX", col, "TIME_PERIOD"], low_memory=False)
    e = e[(e.SEX == "SEX_T") & e[col].astype(str).str.match(pat)]
    a = e.groupby("REF_AREA").TIME_PERIOD.max()
    claim(f"ilostat.paises.{res}d", len(a), f"datos/ilostat/{arch}")
    claim(f"ilostat.paises.{res}d.desde2019", (a >= 2019).sum(), f"datos/ilostat/{arch}: último año ≥ 2019")
meta = pd.read_csv(D / "atlas/paises_meta.csv"); f = "datos/atlas/paises_meta.csv"
claim("atlas.paises", len(meta), f); claim("atlas.paises.2d", (meta.resolucion == 2).sum(), f); claim("atlas.paises.1d", (meta.resolucion == 1).sum(), f)

# Piloto descartado (docs/MODELOS.md, fijado antes del registro osf.io/9zntf)
f = "docs/MODELOS.md (piloto descartado)"
claim("piloto.lote.tareas", 25, f)
claim("piloto.lote.sonnet.kappa", 0.60, f); claim("piloto.lote.haiku.kappa", 0.56, f)
claim("piloto.envoltorio.nivel", 1.64, f); claim("piloto.neutro.nivel", 1.33, f); claim("piloto.envoltorio.kappa", 0.70, f)

(OUT / "claims_diseno.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in C))
print(f"{len(C)} claims de diseño → salidas_diseno/claims_diseno.jsonl")
for x in C: print(f"  {x['id']:<45} {x['valor']}")
