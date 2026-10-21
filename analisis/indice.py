"""Paso 20: índice ADI tarea → ocupación ISCO-08 4 díg. → país → mundo, con las pruebas H1–H4 del preregistro
(docs/OSF_PREREGISTRO_EN.md, secciones Indices y Statistical models). Escribe salidas/adi_{isco,pais,tarea}.csv, detalles y
salidas/claims.jsonl (cada cifra del paper).

  --sintetico       genera scoring/salidas/sintetico/{sonnet,haiku,deepseek-v4-pro,kimi-k2.6}.jsonl (semilla 20261020) y los usa;
                    sirve solo para probar el pipeline: todo sale con sintetico=true y las figuras con marca de agua.
  --entrada DIR     JSONL reales de scoring/puntuar.py (uno por modelo; *_rN.jsonl son pasadas de test-retest).

Reglas del preregistro (no cambiar sin registrar desviación):
  consenso = nivel modal entre modelos, empate → nivel menor; share = mediana; ADI_o = Σ w·1[nivel ≥ 2]; ADI3 = Σ w·1[nivel = 3];
  ADIs = Σ w·share/100; país a la resolución que reporta (2 díg., si no 1 díg.); titular = media ponderada por empleo.
Decisión sin dato (registrada en docs/DESVIACIONES.md): ningún país reporta empleo ISCO a 4 díg. en ILOSTAT, así que los 4 díg.
dentro de cada grupo reportado se ponderan con el empleo de la GEIH (Colombia, CIUO-08 A.C.) para todos los países; pesos iguales
como sensibilidad (preregistrada).
"""
import argparse, json, re, subprocess, sys, time
from datetime import datetime
sys.path.insert(0, "noche")
from comun import *
import numpy as np, pandas as pd

lg = log("20_indice")
SAL = RAIZ / "salidas"; SAL.mkdir(exist_ok=True)
MODELOS = ["sonnet", "haiku", "deepseek-v4-pro", "kimi-k2.6"]
SEMILLA, B = 20261020, 1000
INGRESO = {"High income": "high", "Upper middle income": "upper-middle", "Lower middle income": "lower-middle", "Low income": "low"}
CORTO = {"high": "alto", "upper-middle": "medio_alto", "lower-middle": "medio_bajo", "low": "bajo"}
CLAIMS = []


def claim(i, v, nota=""):
    if isinstance(v, (np.floating, np.integer)): v = v.item()
    if isinstance(v, float) and not np.isfinite(v): v = "--"
    CLAIMS.append({"id": i, "valor": v, "t": datetime.now().isoformat(timespec="seconds"), "sintetico": SINT, **({"nota": nota} if nota else {})})


# ---------------------------------------------------------------- datos sintéticos
MAS = r"\b(?:analy[sz]e|prepare|record|compile|review|write|calculate|document|schedule|research|report|draft|plan|monitor|evaluate|maintain records|process)\w*"
MENOS = r"\b(?:operate|repair|lift|install|drive|clean|load|assemble|weld|cut|climb|lay|move|carry|examine patients|treat|feed|harvest|paint|dig)\w*"
FISICO = r"\b(?:operate|repair|lift|install|drive|clean|load|assemble|weld|cut|climb|lay|move|carry|treat|feed|harvest|paint|dig|inspect|tend)\w*"


def sintetico(tareas, destino):
    """Niveles plausibles, NO resultados: latente por palabras clave + ruido común + ruido por modelo; U invertida en log minutos."""
    rng = np.random.default_rng(SEMILLA); destino.mkdir(parents=True, exist_ok=True)
    t = tareas.texto.str.lower()
    n = len(t); mas = t.str.count(MAS).values; menos = t.str.count(MENOS).values; fis = t.str.contains(FISICO).values
    lmin = rng.normal(3.6, 1.1, n)                                   # log minutos «verdaderos»
    z = 0.9 * mas - 1.1 * menos - 0.8 * fis + 0.45 - 0.18 * (lmin - 3.6) ** 2 + rng.normal(0, 0.8, n)
    sesgo = {"sonnet": 0.0, "haiku": 0.12, "deepseek-v4-pro": -0.08, "kimi-k2.6": 0.05}
    def una(m, ruido, filas_idx):
        zz = z[filas_idx] + sesgo[m] + rng.normal(0, ruido, len(filas_idx))
        lvl = np.digitize(zz, [-1.3, -0.1, 1.1])
        share = np.clip(np.round(lvl * 27 + rng.normal(6, 9, len(zz))), 0, 100).astype(int)
        mins = np.clip(np.round(np.exp(lmin[filas_idx] + rng.normal(0, 0.35, len(zz)))), 1, 9000).astype(int)
        out = []
        for k, i in enumerate(filas_idx):
            if rng.random() < 0.003:
                out.append({"task_id": int(tareas.task_id.iat[i]), "error": "sintetico: JSON inválido"}); continue
            out.append({"task_id": int(tareas.task_id.iat[i]), "level": int(lvl[k]), "share_delegable": int(share[k]), "minutes_human": int(mins[k]),
                        "barrier_physical": bool(fis[i] or (lvl[k] <= 1 and rng.random() < 0.3)), "barrier_accountability": bool(rng.random() < 0.10 + 0.08 * (lvl[k] == 2)),
                        "barrier_trust": bool(rng.random() < 0.15 + 0.05 * (lvl[k] >= 2)), "barrier_access": bool(rng.random() < 0.20),
                        "confidence": ["LOW", "MEDIUM", "HIGH"][int(rng.integers(0, 3))]})
        for f in out: f.update(modelo=m, rubrica_sha="sintetico", ts=datetime.now().isoformat(timespec="seconds"))
        return out
    todos = np.arange(n); rr = rng.choice(n, 300, replace=False)
    for m in MODELOS:
        with open(destino / f"{m}.jsonl", "w") as f:
            for fila in una(m, 0.5, todos): f.write(json.dumps(fila) + "\n")
    for m in ("sonnet", "haiku"):                                    # test-retest en 300 tareas
        with open(destino / f"{m}_r2.jsonl", "w") as f:
            for fila in una(m, 0.5, rr): f.write(json.dumps(fila) + "\n")
    lg.info(f"sintético: {len(MODELOS)} modelos × {n:,} tareas + retest 300 en {destino}")


# ---------------------------------------------------------------- lectura
CAMPOS = ["level", "share_delegable", "minutes_human", "barrier_physical", "barrier_accountability", "barrier_trust", "barrier_access"]


def leer_modelo(p):
    filas = [json.loads(l) for l in open(p) if l.strip()]
    d = pd.DataFrame(filas)
    if "error" not in d: d["error"] = np.nan
    ok = d[d.error.isna() & d.get("level", pd.Series(dtype=float)).notna()].drop_duplicates("task_id", keep="last")
    fallos = set(d.loc[d.error.notna(), "task_id"]) - set(ok.task_id)
    return ok[["task_id"] + CAMPOS].set_index("task_id"), len(fallos)


def leer_union(rutas):
    """Une varios JSONL (particiones de un mismo pase): descarta errores y líneas truncadas, deja la última fila válida por task_id (por ts)."""
    filas = []
    for p in rutas:
        for l in open(p):
            if not l.strip(): continue
            try: filas.append(json.loads(l))
            except json.JSONDecodeError: pass                      # línea a medio escribir por un proceso en curso
    d = pd.DataFrame(filas)
    if d.empty or "level" not in d: return pd.DataFrame(columns=CAMPOS).rename_axis("task_id")
    if "error" not in d: d["error"] = np.nan
    d = d[d.error.isna() & d.level.isin([0, 1, 2, 3])]
    if "ts" in d: d = d.sort_values("ts", kind="stable")
    return d.drop_duplicates("task_id", keep="last").set_index("task_id")[CAMPOS]


def leer_hoja(f):
    """Hoja de un evaluador humano (formato validacion/santiago/hoja_Santiago.xlsx): serie task_id → nivel 0..3 (solo filas llenas)."""
    try: x = pd.read_excel(f, sheet_name="2_tareas_300")
    except ValueError: x = pd.read_excel(f)
    col = next((c for c in x.columns if str(c).lower().startswith(("level", "nivel"))), None)
    if col is None or "task_id" not in x: return pd.Series(dtype=float)
    s = pd.Series(pd.to_numeric(x[col], errors="coerce").values, index=pd.to_numeric(x.task_id, errors="coerce").values).dropna()
    s = s[s.index.notna() & s.isin([0, 1, 2, 3])]; s = s[~s.index.duplicated(keep="last")]; s.index = s.index.astype(int)
    return s


def esc_tex(t): return re.sub(r"([&%#_$])", r"\\\1", str(t))


ARTICULO = re.compile(r"^(United |Netherlands|Philippines|Gambia|Bahamas|Czech Republic|Dominican Republic|Central African|Maldives|Solomon|Marshall|"
                      r"Comoros|Seychelles|Russian Federation|Slovak Republic|Kyrgyz Republic|Lao PDR|Syrian|Democratic|Republic|West Bank|Turks|Cayman|Virgin|Faroe)")


def con_articulo(pais):
    """Nombre de país para usar a mitad de frase en inglés («the United Kingdom»)."""
    return ("the " + pais) if ARTICULO.match(str(pais)) else str(pais)


def alpha_ordinal(M):
    """Krippendorff α ordinal; M = unidades × evaluadores con valores 0..3 o NaN."""
    M = np.asarray(M, float); cnt = np.stack([(M == c).sum(1) for c in range(4)], 1).astype(float)
    m = cnt.sum(1); cnt = cnt[m >= 2]; m = m[m >= 2]
    if len(m) == 0: return np.nan
    o = np.einsum("uc,uk->ck", cnt / (m - 1)[:, None], cnt) - np.diag((cnt / (m - 1)[:, None]).sum(0))
    nc = o.sum(1); n = nc.sum(); cs = np.cumsum(nc)
    d2 = np.array([[(cs[max(c, k)] - (cs[min(c, k) - 1] if min(c, k) > 0 else 0) - (nc[c] + nc[k]) / 2) ** 2 for k in range(4)] for c in range(4)])
    De = (np.outer(nc, nc) * d2).sum() / (n - 1)
    return 1 - (o * d2).sum() / De if De > 0 else np.nan


def kappa_cuadratica(a, b):
    a, b = np.asarray(a), np.asarray(b); ok = ~(np.isnan(a) | np.isnan(b)); a, b = a[ok].astype(int), b[ok].astype(int)
    if len(a) < 2: return np.nan
    O = np.zeros((4, 4)); np.add.at(O, (a, b), 1); W = (np.subtract.outer(np.arange(4), np.arange(4)) ** 2) / 9
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    return 1 - (W * O).sum() / (W * E).sum() if (W * E).sum() > 0 else np.nan


# ---------------------------------------------------------------- agregación ISCO 4 díg. → país (también la usa analisis/robustez_esco.py)
def cargar_atlas(sin_d3=False):
    """Atlas largo (empleo > 0) y metadatos de país. sin_d3=True: países originales, antes de la exclusión D3."""
    suf = "_sin_d3" if sin_d3 else ""
    P = pd.read_parquet(DATOS / f"atlas/paises{suf}.parquet"); meta = pd.read_csv(DATOS / f"atlas/paises_meta{suf}.csv")
    return P[P.empleo > 0], meta


def vectores_peso(isco):
    """Empleo por ISCO 4 díg. en el orden de `isco`: (GEIH Colombia, BLS OES 2024 por el mismo puente)."""
    geih = pd.read_csv(DATOS / "microdatos/geih_ciuo_resumen.csv", dtype={"ciuo4": str})
    geih["isco08"] = geih.ciuo4.str.zfill(4); v_geih = geih.groupby("isco08").empleo.sum().reindex(isco).fillna(0).values
    oes = pd.read_csv(DATOS / "oes/oes_isco.csv", dtype={"isco08": str})
    v_oes = oes.set_index(oes.isco08.str.zfill(4)).empleo.reindex(isco).fillna(0).values
    return v_geih, v_oes


def pesos_d1(meta, v_geih, v_oes):
    """D1 (docs/DESVIACIONES.md): pesos 4 díg. por grupo de ingreso — alto (HIC): OES; resto: GEIH. Devuelve país → vector."""
    ingreso_de = meta.set_index("iso3").ingreso_id.to_dict()
    return lambda c: v_oes if ingreso_de.get(c) == "HIC" else v_geih


def matriz_paises(isco, P, v):
    """M[c,u] = (e_cg / E_c) · v_u / V_g ; v es un vector o una función país → vector; V_g = 0 → pesos iguales en el grupo.
    P: atlas largo; filas de M en orden alfabético de iso3."""
    nc = P.iso3.nunique(); isco_s = np.asarray(isco).astype(str)
    M = np.zeros((nc, len(isco))); E = np.zeros(nc)
    for ci, (c, d) in enumerate(P.groupby("iso3")):
        vc = v(c) if callable(v) else v
        for g, e in zip(d.grupo, d.empleo):
            u = np.flatnonzero(np.char.startswith(isco_s, g))
            if not len(u): continue
            vu = vc[u] if vc[u].sum() > 0 else np.ones(len(u))
            M[ci, u] += e * vu / vu.sum(); E[ci] += e
    return M / E[:, None], E


# ---------------------------------------------------------------- main
def main():
    global SINT
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group()
    g.add_argument("--sintetico", action="store_true"); g.add_argument("--entrada")
    ap.add_argument("--reps", type=int, default=B)
    a = ap.parse_args(); SINT = a.sintetico or not a.entrada; t0 = time.time()
    tareas = pd.read_parquet(DATOS / "tareas_unicas.parquet").reset_index(drop=True)
    if SINT:
        ent = RAIZ / "scoring/salidas/sintetico"; sintetico(tareas, ent)
    else:
        ent = (RAIZ / a.entrada) if not a.entrada.startswith("/") else Path(a.entrada)
    arch = sorted(p for p in ent.glob("*.jsonl") if not re.search(r"_r\d+$", p.stem))
    if not arch: sys.exit(f"sin JSONL de modelos en {ent}")
    lg.info(f"modo {'SINTÉTICO' if SINT else 'REAL'} · entrada {ent} · modelos {[p.stem for p in arch]}")
    claim("diseno.semilla", SEMILLA); claim("diseno.reps", a.reps); claim("n.modelos", len(arch))

    # --- tarea × modelo
    tid = tareas.task_id.values; pos = pd.Series(np.arange(len(tid)), index=tid)
    nm = len(arch); L = np.full((len(tid), nm), np.nan); S = L.copy(); MIN = L.copy(); BAR = np.full((len(tid), nm, 4), np.nan)
    nombres = []
    for j, p in enumerate(arch):
        d, nf = leer_modelo(p); d = d[d.index.isin(pos.index)]; ix = pos[d.index].values; nombres.append(p.stem)
        L[ix, j] = d.level; S[ix, j] = d.share_delegable; MIN[ix, j] = d.minutes_human
        for k, c in enumerate(CAMPOS[3:]): BAR[ix, j, k] = d[c].astype(float)
        mk = p.stem.replace(".", "_"); claim(f"n.fallos.{mk}", nf); claim(f"n.tareas.{mk}", len(d))
        lg.info(f"{p.stem}: {len(d):,} tareas válidas, {nf} fallidas tras reintentos")
    cnt = np.stack([(L == c).sum(1) for c in range(4)], 1); nval = (~np.isnan(L)).sum(1)
    nivel = np.where(nval > 0, cnt.argmax(1), -1)                  # argmax devuelve el primer máximo = nivel menor en empates
    with np.errstate(all="ignore"):
        share = np.nanmedian(S, 1); minutos = np.nanmedian(MIN, 1); barrera = np.nanmean(BAR, 1)   # barrera: fracción de modelos que la marcan
    rated = nval > 0
    claim("cobertura.tareas", len(tid)); claim("cobertura.tareas.puntuadas", int(rated.sum()))
    for c in range(4): claim(f"tareas.nivel{c}.pct", 100 * np.mean(nivel[rated] == c))
    claim("tareas.l2.pct", 100 * np.mean(nivel[rated] >= 2)); claim("tareas.empates.pct", 100 * np.mean((cnt.max(1)[:, None] == cnt).sum(1)[rated] > 1))

    # --- ocupación ISCO 4 díg.
    pares = pd.read_parquet(DATOS / "pares_isco_tarea.parquet").rename(columns={"Task ID": "task_id"})
    pares = pares[pares.task_id.isin(pos.index)]; pares["i"] = pos[pares.task_id].values
    pares = pares[rated[pares.i.values]].sort_values(["isco08", "i"]).reset_index(drop=True)
    isco = np.array(sorted(pares.isco08.unique())); gi = pd.Series(np.arange(len(isco)), index=isco)[pares.isco08].values
    w = pares.peso.values; ti = pares.i.values
    X = np.stack([(nivel[ti] >= 2), (nivel[ti] == 3), share[ti] / 100, *barrera[ti].T], 1).astype(float)   # 3 índices + 4 barreras
    X = np.nan_to_num(X)
    def ocup(wv, Xv, g=gi, n=len(isco)):
        den = np.bincount(g, wv, n); return np.stack([np.bincount(g, wv * Xv[:, k], n) for k in range(Xv.shape[1])], 1) / den[:, None]
    O = ocup(w, X)                                                 # (433, 7)
    starts = np.r_[0, np.flatnonzero(np.diff(gi)) + 1]; sizes = np.diff(np.r_[starts, len(gi)])
    # bootstrap: tareas remuestreadas dentro de ocupación (vectorizado por bloques)
    rng = np.random.default_rng(SEMILLA); OB = np.empty((a.reps, len(isco), 3)); pasos = 50
    for b0 in range(0, a.reps, pasos):
        nb = min(pasos, a.reps - b0)
        dr = starts[gi][None, :] + np.floor(rng.random((nb, len(gi))) * sizes[gi][None, :]).astype(np.int64)
        Wd = w[dr]; den = np.add.reduceat(Wd, starts, axis=1)
        for k in range(3): OB[b0:b0 + nb, :, k] = np.add.reduceat(Wd * X[dr, k], starts, axis=1) / den
    lg.info(f"bootstrap ocupaciones {a.reps} réplicas en {time.time() - t0:.0f} s")

    tit = pd.read_csv(DATOS / "esco/isco08_grupos_unitarios.csv", dtype=str).set_index("isco08").titulo
    ntar = np.bincount(gi, minlength=len(isco))
    occ = pd.DataFrame({"isco08": isco, "titulo": tit.reindex(isco).values, "adi_l2": O[:, 0], "adi_l3": O[:, 1], "adi_share": 100 * O[:, 2],
                        "n_tareas": ntar, "barrera_fisica": O[:, 3], "barrera_responsabilidad": O[:, 4], "barrera_confianza": O[:, 5],
                        "barrera_acceso": O[:, 6], "ic_lo": 100 * np.percentile(OB[:, :, 2], 2.5, 0), "ic_hi": 100 * np.percentile(OB[:, :, 2], 97.5, 0)})
    occ["imputado"] = occ.isco08.map(pares.groupby("isco08").imputado.first())
    for k, c in enumerate(["l2", "l3"]):
        occ[f"{c}_lo"] = np.percentile(OB[:, :, k], 2.5, 0); occ[f"{c}_hi"] = np.percentile(OB[:, :, k], 97.5, 0)
    claim("cobertura.isco", len(isco)); claim("cobertura.isco.imputados", int(occ.imputado.sum()))

    # --- pesos 4 díg. dentro de grupo: GEIH (primario) e iguales (sensibilidad)
    v_geih, v_oes = vectores_peso(isco)
    claim("cobertura.geih.isco", int((v_geih > 0).sum())); lg.info(f"GEIH: {int((v_geih > 0).sum())} de {len(isco)} ISCO con empleo")

    paises, meta = cargar_atlas()
    ciso = sorted(paises.iso3.unique())
    # D1 (docs/DESVIACIONES.md): pesos 4 díg. por grupo de ingreso — alto: BLS OES 2024 (EE. UU.) por el mismo puente;
    # medio-alto, medio-bajo y bajo: GEIH Colombia. Sensibilidades: GEIH para todos y pesos iguales.
    claim("cobertura.oes.isco", int((v_oes > 0).sum()))
    v_ingreso = pesos_d1(meta, v_geih, v_oes)
    def matriz(v, P=None): return matriz_paises(isco, paises if P is None else P, v)   # filas en orden alfabético de iso3
    M, E = matriz(v_ingreso); Mi, _ = matriz(np.ones(len(isco))); Mg, _ = matriz(v_geih)
    C = M @ O[:, :3]; Ci = Mi @ O[:, :3]; Cg = Mg @ O[:, :3]; CB = np.einsum("cu,buk->bck", M, OB)       # (B, países, 3)
    pa = pd.DataFrame({"iso3": ciso, "adi_l2": C[:, 0], "adi_l3": C[:, 1], "adi_share": 100 * C[:, 2], "empleo_total": E,
                       "adi_l2_iguales": Ci[:, 0], "adi_l3_iguales": Ci[:, 1], "adi_share_iguales": 100 * Ci[:, 2],
                       "adi_l2_geih": Cg[:, 0], "adi_l3_geih": Cg[:, 1],
                       "l2_lo": np.percentile(CB[:, :, 0], 2.5, 0), "l2_hi": np.percentile(CB[:, :, 0], 97.5, 0)})
    pa = pa.merge(meta[["iso3", "pais", "ingreso", "anio", "resolucion", "pib_pc_ppp", "region", "informalidad_pct"]], on="iso3", how="left")
    pa["ingreso"] = pa.ingreso.map(INGRESO)
    occ["empleo_mundial"] = E @ M                                  # empleo implícito por 4 díg. (para figuras por gran grupo)

    # --- titulares
    def media(df, col, peso="empleo_total"): return float(np.average(df[col], weights=df[peso]))
    claim("cobertura.paises", len(pa)); claim("cobertura.paises.2d", int((pa.resolucion == 2).sum())); claim("cobertura.paises.1d", int((pa.resolucion == 1).sum()))
    claim("cobertura.empleo_millones", E.sum() / 1e6); claim("cobertura.paises.sin_pib", int(pa.pib_pc_ppp.isna().sum()))
    wE = E / E.sum(); glob_b = CB.transpose(0, 2, 1) @ wE              # (B, 3)
    for k, c in enumerate(["l2", "l3", "share"]):
        claim(f"titular.global.{c}", 100 * float(wE @ C[:, k]))
        claim(f"titular.global.{c}.lo", 100 * np.percentile(glob_b[:, k], 2.5)); claim(f"titular.global.{c}.hi", 100 * np.percentile(glob_b[:, k], 97.5))
    claim("titular.global.l2.iguales", 100 * float(wE @ Ci[:, 0])); claim("titular.global.l3.iguales", 100 * float(wE @ Ci[:, 1]))
    claim("titular.global.l2.geih", 100 * float(wE @ Cg[:, 0])); claim("titular.global.l3.geih", 100 * float(wE @ Cg[:, 1]))
    claim("titular.global.l2.sin_ponderar", 100 * pa.adi_l2.mean())
    Ou = ocup(np.ones_like(w), X[:, :1]); claim("titular.global.l2.pesos_uniformes", 100 * float(wE @ (M @ Ou[:, 0])))   # tareas con igual peso
    Mx, Ex = matriz(v_geih * ~occ.imputado.values.astype(bool)); claim("titular.global.l2.sin_imputados", 100 * float((Ex / Ex.sum()) @ (Mx @ O[:, 0])))
    for ing, corto in CORTO.items():
        d = pa[pa.ingreso == ing]
        if len(d): claim(f"titular.ingreso.{corto}.l2", 100 * media(d, "adi_l2")); claim(f"titular.ingreso.{corto}.l3", 100 * media(d, "adi_l3")); claim(f"cobertura.ingreso.{corto}.paises", len(d))
    d = pa[pa.ingreso.isin(["upper-middle", "lower-middle"])]
    claim("titular.ingreso.medio.l2", 100 * media(d, "adi_l2")); claim("titular.ingreso.medio.l3", 100 * media(d, "adi_l3"))
    for iso in ("COL", "MEX", "BRA", "USA", "IND", "CHN"):
        r = pa[pa.iso3 == iso]
        if len(r): claim(f"pais.{iso}.l2", 100 * r.adi_l2.iat[0])

    # --- extremos (3 ISCO y 3 países con mayor y menor ADI L2; empates en L2 se ordenan por ADIs)
    for nom, df, idc, nomc in (("isco", occ, "isco08", "titulo"), ("pais", pa, "iso3", "pais")):
        s = df.sort_values(["adi_l2", "adi_share"], ascending=False, kind="stable").reset_index(drop=True)
        claim(f"extremo.{nom}.n.max", int((df.adi_l2 >= df.adi_l2.max() - 1e-9).sum())); claim(f"extremo.{nom}.n.min", int((df.adi_l2 <= df.adi_l2.min() + 1e-9).sum()))
        for k in range(3):
            for pre, r in (("top", s.iloc[k]), ("bot", s.iloc[len(s) - 1 - k])):
                claim(f"extremo.{nom}.{pre}{k + 1}.l2", 100 * r.adi_l2); claim(f"extremo.{nom}.{pre}{k + 1}.id", str(r[idc]))
                claim(f"extremo.{nom}.{pre}{k + 1}.nombre", esc_tex(con_articulo(r[nomc]) if nom == "pais" else r[nomc][:1].lower() + r[nomc][1:]))

    # --- por modelo (exploratorio)
    for j, m in enumerate(nombres):
        okm = ~np.isnan(L[ti, j]); Xm = np.stack([(L[ti, j] >= 2), (L[ti, j] == 3)], 1).astype(float)
        with np.errstate(all="ignore"): Om = ocup(w * okm, Xm)
        Om = np.where(np.isnan(Om), np.nanmean(Om, 0), Om)
        claim(f"titular.modelo.{m.replace('.', '_')}.l2", 100 * float(wE @ (M @ Om[:, 0])))

    # --- H1
    import statsmodels.api as sm
    from scipy import stats
    h = pa.dropna(subset=["pib_pc_ppp"]).copy(); h["y"] = 100 * h.adi_l2; h["lpib"] = np.log(h.pib_pc_ppp)
    r1 = sm.OLS(h.y, sm.add_constant(h.lpib)).fit()
    b, se = r1.params.lpib, r1.bse.lpib; p1 = stats.t.sf(b / se, r1.df_resid)
    hb = h.index.values                                            # pa tiene índice posicional (= filas de M y CB)
    Xc = h.lpib.values - h.lpib.mean(); slopes = (100 * CB[:, hb, 0] @ Xc) / (Xc @ Xc)
    claim("h1.pendiente", b); claim("h1.se", se); claim("h1.p", p1); claim("h1.r2", r1.rsquared); claim("h1.n", int(r1.nobs))
    lo, hi = np.percentile(slopes, [2.5, 97.5]); claim("h1.pendiente.lo", lo); claim("h1.pendiente.hi", hi)
    claim("h1.pendiente.ic", f"{lo:.2f} to {hi:.2f}".replace("-", "$-$"))
    hd = h.dropna(subset=["ingreso"]); D = pd.get_dummies(hd.ingreso).reindex(columns=["low", "lower-middle", "upper-middle"], fill_value=0).astype(float)
    r2 = sm.OLS(hd.y, sm.add_constant(D)).fit()
    for k in D.columns:
        claim(f"h1.dif.{CORTO[k]}_alto", r2.params[k]); claim(f"h1.dif.{CORTO[k]}_alto.p", stats.t.cdf(r2.params[k] / r2.bse[k], r2.df_resid))
    claim("h1.dif.bajo_alto", r2.params["low"]); claim("h1.dummies.r2", r2.rsquared)
    r1i = sm.OLS(100 * h.adi_l2_iguales, sm.add_constant(h.lpib)).fit(); claim("h1.pendiente.iguales", r1i.params.lpib)
    r1g = sm.OLS(100 * h.adi_l2_geih, sm.add_constant(h.lpib)).fit(); claim("h1.pendiente.geih", r1g.params.lpib)
    r1s = sm.OLS(h.adi_share, sm.add_constant(h.lpib)).fit(); claim("h1.pendiente.share", r1s.params.lpib)
    r1r = sm.OLS(h.y, sm.add_constant(h.lpib)).fit(cov_type="HC1"); claim("h1.se.hc1", r1r.bse.lpib)
    # D3 (docs/DESVIACIONES.md): titular y pendiente H1 con los países originales, antes de la exclusión por calidad del dato
    p0, m0 = DATOS / "atlas/paises_sin_d3.parquet", DATOS / "atlas/paises_meta_sin_d3.csv"
    if p0.exists() and m0.exists():
        P0, meta0 = cargar_atlas(sin_d3=True)
        M0, E0 = matriz(pesos_d1(meta0, v_geih, v_oes), P0)
        d0 = pd.DataFrame({"iso3": sorted(P0.iso3.unique()), "y": 100 * (M0 @ O[:, 0]), "e": E0})
        claim("d3.titular.l2.150", float(np.average(d0.y, weights=d0.e))); claim("d3.n.paises", len(d0))
        claim("d3.titular.l2.con_regla", 100 * float(wE @ C[:, 0]), nota="= titular.global.l2, con 2 decimales para compararlo con d3.titular.l2.150")
        d0 = d0.merge(meta0[["iso3", "pib_pc_ppp"]], on="iso3").dropna()
        r0 = sm.OLS(d0.y, sm.add_constant(np.log(d0.pib_pc_ppp))).fit(); claim("d3.h1.pendiente.150", r0.params.iloc[1]); claim("d3.h1.n", int(r0.nobs))
        lg.info(f"D3 sensibilidad: {P0.iso3.nunique()} países, titular {np.average(100 * (M0 @ O[:, 0]), weights=E0):.3f}, pendiente {r0.params.iloc[1]:.3f}")
    else:
        for i in ("d3.titular.l2.150", "d3.h1.pendiente.150", "d3.n.paises"): claim(i, "--", nota="falta datos/atlas/paises_sin_d3.parquet (correr analisis/atlas_insumos.py)")
    reg = {"h1a": {"coef": r1.params.to_dict(), "se": r1.bse.to_dict(), "p_una_cola": {"lpib": p1}, "n": int(r1.nobs), "r2": r1.rsquared},
           "h1b": {"coef": r2.params.to_dict(), "se": r2.bse.to_dict(), "p_una_cola": {k: stats.t.cdf(r2.params[k] / r2.bse[k], r2.df_resid) for k in D.columns}, "n": int(r2.nobs), "r2": r2.rsquared},
           "h1a_iguales": {"coef": r1i.params.to_dict(), "se": r1i.bse.to_dict(), "n": int(r1i.nobs), "r2": r1i.rsquared}}

    # --- H2 (uso AEI por país)
    au = DATOS / "aei_pais.csv"
    if au.exists():
        u = pd.read_csv(au)[["iso3", "usage_per_capita_index"]].dropna()
        h2 = pa.merge(u, on="iso3").dropna(subset=["ingreso"]); z = lambda s: (s - s.mean()) / s.std()
        h2["brecha"] = z(h2.adi_l2) - z(h2.usage_per_capita_index)
        D2 = pd.get_dummies(h2.ingreso).reindex(columns=["low", "lower-middle", "upper-middle"], fill_value=0).astype(float)
        r3 = sm.OLS(h2.brecha, sm.add_constant(D2)).fit()
        for k in ("lower-middle", "upper-middle"):
            claim(f"h2.b.{CORTO[k]}", r3.params[k]); claim(f"h2.b.{CORTO[k]}.p", stats.t.sf(r3.params[k] / r3.bse[k], r3.df_resid))
        if D2["low"].sum() > 0:
            claim("h2.b.bajo", r3.params["low"]); claim("h2.b.bajo.p", r3.pvalues["low"], nota="bilateral: H2 no predice signo para ingreso bajo")
        else:
            claim("h2.b.bajo", "--"); claim("h2.b.bajo.p", "--")
        D3 = pd.DataFrame({"low": D2["low"], "medio": D2["lower-middle"] + D2["upper-middle"]})
        r4 = sm.OLS(h2.brecha, sm.add_constant(D3)).fit()
        claim("h2.brecha.medio", r4.params.medio); claim("h2.brecha.medio.p", stats.t.sf(r4.params.medio / r4.bse.medio, r4.df_resid)); claim("h2.n", len(h2))
        claim("h2.r.adi_uso", h2.adi_l2.corr(h2.usage_per_capita_index))
        pa = pa.merge(u, on="iso3", how="left"); pa.loc[pa.iso3.isin(h2.iso3), "brecha_h2"] = h2.set_index("iso3").brecha.reindex(pa.iso3[pa.iso3.isin(h2.iso3)]).values
        reg["h2"] = {"coef": r3.params.to_dict(), "se": r3.bse.to_dict(), "p_una_cola": {k: stats.t.sf(r3.params[k] / r3.bse[k], r3.df_resid) for k in ("lower-middle", "upper-middle")}, "n": int(r3.nobs), "r2": r3.rsquared}
    else:
        for i in ("h2.brecha.medio", "h2.n", "h2.b.bajo", "h2.b.bajo.p"): claim(i, "--")

    # --- H3
    cp = DATOS / "comparadores_isco.parquet"
    if cp.exists():
        k = occ.merge(pd.read_parquet(cp), on="isco08", how="left")
        for col, nom in (("eloundou_beta", "eloundou"), ("felten_aioe", "felten"), ("eloundou_gpt4_beta", "eloundou_gpt4"), ("webb_pct_ai", "webb_ai"),
                         ("webb_pct_software", "webb_software"), ("webb_pct_robot", "webb_robot"), ("eisfeldt_genaiexp", "eisfeldt"), ("aei_exposicion_obs", "aei"), ("aei_penetracion", "aei_tareas")):
            if col not in k: continue
            d = k[["adi_l2", col]].dropna()
            claim(f"h3.r.{nom}", stats.pearsonr(d.adi_l2, d[col])[0]); claim(f"h3.rho.{nom}", stats.spearmanr(d.adi_l2, d[col])[0]); claim(f"h3.n.{nom}", len(d))
        occ = k

    # --- H4: logit 1[nivel = 3] ~ log min + log min², errores agrupados por ocupación O*NET
    ok = rated & ~np.isnan(minutos)
    lm = np.log(np.clip(minutos[ok], 1, 4800)); y = (nivel[ok] == 3).astype(float)
    grupos = pd.factorize(tareas.onet19.values[ok])[0]
    r5 = sm.Logit(y, sm.add_constant(np.column_stack([lm, lm ** 2]))).fit(disp=0, cov_type="cluster", cov_kwds={"groups": grupos})
    b1, b2 = r5.params[1], r5.params[2]
    claim("h4.b1", b1); claim("h4.b2", b2); claim("h4.p1", stats.norm.sf(r5.tvalues[1])); claim("h4.p2", stats.norm.cdf(r5.tvalues[2]))
    claim("h4.n", int(ok.sum())); claim("h4.n.clusters", int(grupos.max() + 1))
    claim("h4.pico.minutos", float(np.exp(-b1 / (2 * b2))) if b2 < 0 else "--")
    reg["h4"] = {"coef": dict(zip(["const", "lmin", "lmin2"], r5.params)), "se": dict(zip(["const", "lmin", "lmin2"], r5.bse)), "n": int(ok.sum())}

    # --- acuerdo
    claim("agree.alpha.modelos", alpha_ordinal(L))
    if "sonnet" in nombres and "haiku" in nombres:
        claim("agree.kappa.sonnet_haiku", kappa_cuadratica(L[:, nombres.index("sonnet")], L[:, nombres.index("haiku")]))
    nret = 0
    for m in ("sonnet", "haiku"):
        p2 = ent / f"{m}_r2.jsonl"
        if p2.exists() and m in nombres:
            d2, _ = leer_modelo(p2); d2 = d2[d2.index.isin(pos.index)]; a1 = L[pos[d2.index].values, nombres.index(m)]
            claim(f"agree.testretest.{m}.kappa", kappa_cuadratica(a1, d2.level.values)); claim(f"agree.testretest.{m}.exacto.pct", 100 * np.nanmean(a1 == d2.level.values))
            nret = max(nret, len(d2))
        else:
            claim(f"agree.testretest.{m}.kappa", "--")
    claim("n.testretest", nret if nret else "--")
    cons = pd.Series(np.where(rated, nivel, np.nan), index=tid)    # consenso de modelos por task_id
    col_m = {m: pd.Series(L[:, nombres.index(m)], index=tid) for m in ("sonnet", "haiku") if m in nombres}
    MIN_H, MIN_P = 20, 50                                           # mínimo de tareas en común para reportar acuerdo humano / panel / envoltorio

    # D2 (docs/DESVIACIONES.md): un evaluador humano ciego (Santiago, 300 tareas); α humano–humano solo con ≥ 2 hojas
    rh = RAIZ / "validacion/respuestas"
    hojas = {f.stem: leer_hoja(f) for f in sorted(rh.glob("*.xlsx")) if not f.name.startswith("~$")} if rh.exists() else {}
    hojas = {k: v for k, v in hojas.items() if len(v)}
    hv = None
    if hojas:
        Hm = pd.DataFrame(hojas); hv = Hm.median(1).round() if Hm.shape[1] > 1 else Hm.iloc[:, 0]
        if Hm.shape[1] >= 2:
            ks = [kappa_cuadratica(Hm.iloc[:, i], Hm.iloc[:, j]) for i in range(Hm.shape[1]) for j in range(i + 1, Hm.shape[1])]
            claim("agree.alpha.humano", alpha_ordinal(Hm.values)); claim("agree.kappa.humano.min", min(ks)); claim("agree.kappa.humano.max", max(ks))
        c_h = cons.reindex(hv.index); n_h = int((hv.notna() & c_h.notna()).sum())
        claim("n.humano", n_h); claim("n.humano.hojas", Hm.shape[1]); claim("n.validacion", n_h)
        if n_h >= MIN_H:
            claim("agree.alpha.humano.modelo", alpha_ordinal(np.column_stack([hv.values, c_h.values]))); claim("agree.kappa.humano.modelo", kappa_cuadratica(hv.values, c_h.values))
            claim("agree.exacto.humano.modelo.pct", 100 * float((hv == c_h)[c_h.notna()].mean()))
            for m, sm_ in col_m.items(): claim(f"agree.kappa.humano.{m}", kappa_cuadratica(hv.values, sm_.reindex(hv.index).values))
            claim("humano.nivel.media", float(hv[c_h.notna()].mean())); claim("modelo.nivel.media.humano", float(c_h.dropna().mean()))
        lg.info(f"validación humana: {Hm.shape[1]} hoja(s), {n_h} tareas calificadas con consenso")
    if hv is None or int(cons.reindex(hv.index).notna().sum()) < MIN_H:
        for i in ("agree.alpha.humano.modelo", "agree.kappa.humano.modelo", "agree.kappa.humano.sonnet", "agree.kappa.humano.haiku", "agree.exacto.humano.modelo.pct"): claim(i, "--")
        if hv is None: claim("n.humano", "--")

    # D2: panel agéntico (Opus 5.5 + web), validación NO humana; particiones panel.p?.jsonl + panel.jsonl
    rp = RAIZ / "validacion/agentico/salidas"
    pan = leer_union(sorted(rp.glob("panel.p*.jsonl")) + ([rp / "panel.jsonl"] if (rp / "panel.jsonl").exists() else [])) if rp.exists() else pd.DataFrame(columns=CAMPOS)
    pv = pan.level.astype(float); pv = pv[pv.index.isin(pos.index)]; c_p = cons.reindex(pv.index); ok_p = c_p.notna(); pv, c_p = pv[ok_p], c_p[ok_p]
    IDS_P = ["n.panel", "agree.kappa.panel.modelo", "agree.alpha.panel.modelo", "agree.kappa.panel.sonnet", "agree.kappa.panel.haiku", "panel.nivel.media",
             "modelo.nivel.media.muestra", "panel.l2.pct", "modelo.l2.pct.muestra", "agree.exacto.panel.modelo.pct"]
    if len(pv) >= MIN_P:
        claim("n.panel", len(pv)); claim("agree.kappa.panel.modelo", kappa_cuadratica(pv.values, c_p.values)); claim("agree.alpha.panel.modelo", alpha_ordinal(np.column_stack([pv.values, c_p.values])))
        for m in ("sonnet", "haiku"): claim(f"agree.kappa.panel.{m}", kappa_cuadratica(pv.values, col_m[m].reindex(pv.index).values) if m in col_m else np.nan)
        claim("panel.nivel.media", float(pv.mean())); claim("modelo.nivel.media.muestra", float(c_p.mean()))
        claim("panel.l2.pct", 100 * float((pv >= 2).mean())); claim("modelo.l2.pct.muestra", 100 * float((c_p >= 2).mean()))
        claim("agree.exacto.panel.modelo.pct", 100 * float((pv == c_p).mean()))
        if hv is not None:
            hh = hv.reindex(pv.index).dropna(); claim("n.panel.humano", len(hh))
            claim("agree.kappa.panel.humano", kappa_cuadratica(pv.reindex(hh.index).values, hh.values) if len(hh) >= MIN_H else np.nan)
        else: claim("agree.kappa.panel.humano", "--")
    else:
        for i in IDS_P + ["agree.kappa.panel.humano"]: claim(i, "--", nota=f"panel con {len(pv)} tareas (< {MIN_P})")
    lg.info(f"panel agéntico: {len(pv)} tareas válidas con consenso")

    # sensibilidad al envoltorio por defecto de Claude Code (preregistrada): scoring/salidas/envoltorio_cc/{modelo}.p?.jsonl
    re_ = RAIZ / "scoring/salidas/envoltorio_cc"
    for m in ("sonnet", "haiku"):
        ev = leer_union(sorted(re_.glob(f"{m}.p*.jsonl")) + ([re_ / f"{m}.jsonl"] if (re_ / f"{m}.jsonl").exists() else [])) if re_.exists() else pd.DataFrame(columns=CAMPOS)
        ids = [f"envoltorio.{m}.{x}" for x in ("n", "kappa", "nivel.neutro", "nivel.cc", "l2.neutro.pct", "l2.cc.pct", "kappa.humano.neutro", "kappa.humano.cc")]
        if m not in col_m or ev.empty:
            for i in ids: claim(i, "--")
            continue
        cc = ev.level.astype(float); cc = cc[cc.index.isin(pos.index)]; ne = col_m[m].reindex(cc.index); ok_e = ne.notna(); cc, ne = cc[ok_e], ne[ok_e]
        lg.info(f"envoltorio {m}: {len(cc)} tareas con calificación principal")
        if len(cc) < MIN_P:
            for i in ids: claim(i, "--", nota=f"{len(cc)} tareas (< {MIN_P})")
            continue
        claim(f"envoltorio.{m}.n", len(cc)); claim(f"envoltorio.{m}.kappa", kappa_cuadratica(ne.values, cc.values))
        claim(f"envoltorio.{m}.nivel.neutro", float(ne.mean())); claim(f"envoltorio.{m}.nivel.cc", float(cc.mean()))
        claim(f"envoltorio.{m}.l2.neutro.pct", 100 * float((ne >= 2).mean())); claim(f"envoltorio.{m}.l2.cc.pct", 100 * float((cc >= 2).mean()))
        hh = hv.reindex(cc.index).dropna() if hv is not None else pd.Series(dtype=float)
        claim(f"envoltorio.{m}.n.humano", len(hh) if hv is not None else "--")
        for tag, ser in (("neutro", ne), ("cc", cc)):
            claim(f"envoltorio.{m}.kappa.humano.{tag}", kappa_cuadratica(hh.values, ser.reindex(hh.index).values) if len(hh) >= MIN_H else np.nan)

    # --- placebo: tareas permutadas entre ocupaciones (pesos y número de tareas fijos), 1.000 veces
    rng = np.random.default_rng(SEMILLA + 1); sd_obs = O[:, 0].std(); x2 = X[:, 0]
    hb_l = h.lpib.values; Xc = hb_l - hb_l.mean(); Mh = M[hb]
    sd_p = np.empty(a.reps); sl_p = np.empty(a.reps); den = np.bincount(gi, w, len(isco))
    for r in range(a.reps):
        o = np.bincount(gi, w * x2[rng.permutation(len(x2))], len(isco)) / den
        sd_p[r] = o.std(); sl_p[r] = (100 * (Mh @ o)) @ Xc / (Xc @ Xc)
    claim("placebo.p", float(np.mean(sd_p >= sd_obs))); claim("placebo.h1.p", float(np.mean(sl_p >= b)))
    claim("placebo.sd.obs", sd_obs); claim("placebo.sd.media", sd_p.mean())
    if not (RAIZ / "salidas_robustez/claims_esco.jsonl").exists():   # los valores reales los emite analisis/robustez_esco.py
        claim("robustez.esco.h1.pendiente", "--", nota="falta salidas_robustez/claims_esco.jsonl (analisis/robustez_esco.py)")

    # --- gran grupo ISCO (figuras 3 y 6)
    gg = occ.isco08.str[0].values; wm = occ.empleo_mundial.values; fil = []
    for g in sorted(set(gg)):
        s = gg == g; ww = wm[s] / wm[s].sum() if wm[s].sum() > 0 else np.ones(s.sum()) / s.sum()
        bb = OB[:, s, 0] @ ww
        fil.append({"gg": g, "adi_l2": occ.adi_l2.values[s] @ ww, "lo": np.percentile(bb, 2.5), "hi": np.percentile(bb, 97.5), "adi_l3": occ.adi_l3.values[s] @ ww,
                    "adi_share": occ.adi_share.values[s] @ ww, **{c: occ[c].values[s] @ ww for c in ("barrera_fisica", "barrera_responsabilidad", "barrera_confianza", "barrera_acceso")},
                    "empleo_mundial": wm[s].sum(), "n_isco": int(s.sum())})
        claim(f"gg.{g}.l2", 100 * fil[-1]["adi_l2"])
        for c in ("barrera_fisica", "barrera_responsabilidad", "barrera_confianza", "barrera_acceso"): claim(f"gg.{g}.{c}.pct", 100 * fil[-1][c])
    pd.DataFrame(fil).to_csv(SAL / "indice_gg.csv", index=False)

    # --- salidas
    occ["sintetico"] = SINT; pa["sintetico"] = SINT
    cols_i = ["isco08", "titulo", "adi_l2", "adi_l3", "adi_share", "n_tareas", "barrera_fisica", "barrera_responsabilidad", "barrera_confianza", "barrera_acceso", "ic_lo", "ic_hi", "sintetico"]
    r4d = lambda df: df.round({c: 4 for c in df.columns if c.startswith(("adi_l", "barrera", "l2_", "l3_"))} | {c: 2 for c in ("adi_share", "ic_lo", "ic_hi", "adi_share_iguales")})
    out = r4d(occ[cols_i].copy()); out["sintetico"] = out.sintetico.map({True: "true", False: "false"}); out.to_csv(SAL / "adi_isco.csv", index=False)
    r4d(occ).to_csv(SAL / "indice_isco_detalle.csv", index=False)
    pp = pa.copy(); pp["resolucion"] = "isco08_" + pp.resolucion.astype(int).astype(str) + "d"; pp["empleo_total"] = pp.empleo_total.round().astype(int)
    cols_p = ["iso3", "pais", "ingreso", "anio", "resolucion", "adi_l2", "adi_l3", "adi_share", "empleo_total", "sintetico"]
    o2 = r4d(pp[cols_p].copy()); o2["sintetico"] = o2.sintetico.map({True: "true", False: "false"}); o2.to_csv(SAL / "adi_pais.csv", index=False)
    r4d(pa).to_csv(SAL / "indice_pais_detalle.csv", index=False)
    tt = pd.DataFrame({"task_id": tid, "titulo": tareas.titulo, "texto": tareas.texto, "nivel": np.where(rated, nivel, np.nan), "share": share, "minutos": minutos,
                       "n_modelos": nval, **{f"barrera_{c}": barrera[:, k] for k, c in enumerate(["fisica", "responsabilidad", "confianza", "acceso"])},
                       **{f"nivel_{m}": L[:, j] for j, m in enumerate(nombres)}, "sintetico": "true" if SINT else "false"})
    tt.round(3).to_csv(SAL / "adi_tarea.csv", index=False)
    json.dump({"sintetico": SINT, **reg}, open(SAL / "regresiones.json", "w"), indent=1, default=float)
    with open(SAL / "claims.jsonl", "w") as f:
        for c in CLAIMS: f.write(json.dumps(c, ensure_ascii=False, default=float) + "\n")
    for p in ("adi_isco.csv", "adi_pais.csv", "adi_tarea.csv", "indice_isco_detalle.csv", "indice_pais_detalle.csv", "indice_gg.csv", "regresiones.json", "claims.jsonl"):
        registrar(SAL / p, "derivado: indice.py", nota="SINTÉTICO" if SINT else "real")
    lg.info(f"titular L2 {[c['valor'] for c in CLAIMS if c['id'] == 'titular.global.l2'][0]:.1f} % · H1 pendiente {b:.2f} (p={p1:.3f}) · "
            f"{len(CLAIMS)} claims · {time.time() - t0:.0f} s")
    if SINT:
        r = subprocess.run(["sh", str(RAIZ / "herramientas/adi-index/sincronizar.sh")], capture_output=True, text=True)
        lg.info("sincronizar.sh: " + (r.stdout + r.stderr).strip().replace("\n", " | "))


if __name__ == "__main__":
    main()
