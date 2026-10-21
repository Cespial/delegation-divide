"""Arma el paquete de datos abiertos release/v2026.1/ desde salidas/ y scoring/salidas/main/ (todo local, sin red).

Uso (desde la raíz del repo):  .venv/bin/python -I release/construir_release.py

Escribe:
  release/v2026.1/adi_{isco,pais,tarea}.{csv,parquet}
  release/v2026.1/claims.jsonl            (público: sin cifras pendientes «--», sin ids duplicados)
  release/v2026.1/ratings_{sonnet,haiku}.jsonl.gz   (gzip determinista, mtime=0)
  release/v2026.1/api/{index.json, isco/<4 díg.>.json, country/<ISO3>.json}
  release/v2026.1/SHA256SUMS              (todo lo anterior + DATA_DICTIONARY.md + api/README.md)
Se niega a seguir si alguna fila trae sintetico=true.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
VERSION = "v2026.1"
DEST = RAIZ / "release" / VERSION
API = DEST / "api"
SAL = RAIZ / "salidas"
RATINGS = RAIZ / "scoring" / "salidas" / "main"

TITLE = "The Delegation Divide: An Open Index of AI-Agent Delegability across Occupations and Countries"
REPO = "https://github.com/Cespial/delegation-divide"
PREREG_DOI = "10.17605/OSF.IO/9ZNTF"
LICENSE = "CC-BY-4.0"
BIBTEX = (
    "@article{espinal2026delegation,\n"
    f"  title   = {{{TITLE}}},\n"
    "  author  = {Espinal Maya, Cristian and Jim{\\'e}nez Londo{\\~n}o, Santiago},\n"
    "  journal = {arXiv preprint},\n"
    "  year    = {2026},\n"
    f"  url     = {{{REPO}}},\n"
    f"  note    = {{Agent Delegability Index (ADI) {VERSION}. Preregistration: doi:{PREREG_DOI}}}\n"
    "}"
)
CITE = {
    "bibtex": BIBTEX,
    "bibtex_key": "espinal2026delegation",
    "text": f"Espinal Maya, C., & Jiménez Londoño, S. (2026). {TITLE}. arXiv preprint. {REPO}",
    "preregistration_doi": PREREG_DOI,
    "preregistration_url": f"https://doi.org/{PREREG_DOI}",
}


def limpio(v):
    """NaN → None; numpy → python; para JSON."""
    if v is None:
        return None
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, str):
        return v.strip()
    return v


def registro(fila: pd.Series, cols: list[str]) -> dict:
    return {c: limpio(fila[c]) for c in cols if c in fila.index}


def escribir_json(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def gzip_determinista(src: Path, dst: Path) -> None:
    with src.open("rb") as fi, dst.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as fo:
            shutil.copyfileobj(fi, fo)


def claims_publicos() -> tuple[list[dict], int, int]:
    """Copia de salidas/claims.jsonl sin valores pendientes «--» y con un registro por id (el último)."""
    filas = [json.loads(l) for l in (SAL / "claims.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    pend = sum(1 for c in filas if c.get("valor") == "--")
    vistos: dict[str, dict] = {}
    for c in filas:
        if c.get("valor") == "--":
            continue
        vistos[c["id"]] = c
    return list(vistos.values()), pend, len(filas) - pend - len(vistos)


def main() -> int:
    isco = pd.read_csv(SAL / "adi_isco.csv", dtype={"isco08": str})
    pais = pd.read_csv(SAL / "adi_pais.csv")
    tarea = pd.read_csv(SAL / "adi_tarea.csv")
    for nom, df in (("adi_isco", isco), ("adi_pais", pais), ("adi_tarea", tarea)):
        if df.sintetico.astype(str).str.lower().eq("true").any():
            print(f"ERROR: {nom}.csv trae filas sintetico=true; no se arma un release con datos de ejemplo", file=sys.stderr)
            return 1
    for df in (isco, pais, tarea):
        df["sintetico"] = df.sintetico.astype(str).str.lower().eq("true")
    isco["isco08"] = isco.isco08.str.zfill(4)

    if DEST.exists():
        for p in DEST.iterdir():
            if p.name in {"DATA_DICTIONARY.md"}:
                continue
            if p.is_dir() and p.name == "api":
                for q in p.iterdir():
                    if q.name != "README.md":
                        shutil.rmtree(q) if q.is_dir() else q.unlink()
                continue
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    DEST.mkdir(parents=True, exist_ok=True)

    # 1. tablas: CSV idénticos a salidas/ + Parquet tipado
    for nom, df in (("adi_isco", isco), ("adi_pais", pais), ("adi_tarea", tarea)):
        shutil.copyfile(SAL / f"{nom}.csv", DEST / f"{nom}.csv")
        df.to_parquet(DEST / f"{nom}.parquet", index=False, engine="pyarrow", compression="zstd")

    # 2. claims públicos
    cl, pend, dup = claims_publicos()
    with (DEST / "claims.jsonl").open("w", encoding="utf-8") as f:
        for c in cl:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    C = {c["id"]: c["valor"] for c in cl}

    # 3. calificaciones crudas por modelo
    for m in ("sonnet", "haiku"):
        gzip_determinista(RATINGS / f"{m}.jsonl", DEST / f"ratings_{m}.jsonl.gz")

    # 4. API estática
    det_i = pd.read_csv(SAL / "indice_isco_detalle.csv", dtype={"isco08": str})
    det_i["isco08"] = det_i.isco08.str.zfill(4)
    det_i = det_i.set_index("isco08")
    det_p = pd.read_csv(SAL / "indice_pais_detalle.csv").set_index("iso3")
    isco["rank_l2"] = isco.adi_l2.rank(ascending=False, method="min").astype(int)
    pais["rank_l2"] = pais.adi_l2.rank(ascending=False, method="min").astype(int)
    comun = {"version": VERSION, "license": LICENSE, "cite": CITE}
    cols_i = ["isco08", "titulo", "adi_l2", "adi_l3", "adi_share", "n_tareas", "barrera_fisica", "barrera_responsabilidad",
              "barrera_confianza", "barrera_acceso", "ic_lo", "ic_hi"]
    extra_i = ["imputado", "l2_lo", "l2_hi", "l3_lo", "l3_hi"]
    for _, r in isco.iterrows():
        rec = registro(r, cols_i)
        if r.isco08 in det_i.index:
            d = det_i.loc[r.isco08]
            for c in extra_i:
                v = limpio(d[c])
                rec[c] = (str(v).lower() == "true") if c == "imputado" else (round(v, 4) if isinstance(v, float) else v)
        rec["rank_l2"] = int(r.rank_l2)
        rec["n_occupations"] = len(isco)
        escribir_json(API / "isco" / f"{r.isco08}.json", {"type": "isco08_unit_group", "id": r.isco08, **rec, **comun})
    cols_p = ["iso3", "pais", "ingreso", "anio", "resolucion", "adi_l2", "adi_l3", "adi_share", "empleo_total"]
    extra_p = ["l2_lo", "l2_hi", "adi_l2_iguales", "adi_l3_iguales", "adi_share_iguales", "region", "pib_pc_ppp"]
    for _, r in pais.iterrows():
        rec = registro(r, cols_p)
        if r.iso3 in det_p.index:
            d = det_p.loc[r.iso3]
            for c in extra_p:
                v = limpio(d[c])
                rec[c] = round(v, 4) if isinstance(v, float) else v
        rec["rank_l2"] = int(r.rank_l2)
        rec["n_countries"] = len(pais)
        escribir_json(API / "country" / f"{r.iso3}.json", {"type": "country", "id": r.iso3, **rec, **comun})

    def num(i, nd=1):
        v = C.get(i)
        return round(float(v), nd) if isinstance(v, (int, float)) else None

    headline = {
        "statement": (f"{num('titular.global.l2')}% of task time in world employment is at least partly delegable to AI agents "
                      f"(L2 or L3) in 2026; {num('titular.global.l3')}% can be handed over in full (L3)."),
        "world_l2_pct": num("titular.global.l2", 2),
        "world_l2_ci95_pct": [num("titular.global.l2.lo", 2), num("titular.global.l2.hi", 2)],
        "world_l3_pct": num("titular.global.l3", 2),
        "world_l3_ci95_pct": [num("titular.global.l3.lo", 2), num("titular.global.l3.hi", 2)],
        "world_share_pct": num("titular.global.share", 2),
        "by_income_l2_pct": {k: num(f"titular.ingreso.{c}.l2", 2) for k, c in
                             (("high", "alto"), ("upper-middle", "medio_alto"), ("lower-middle", "medio_bajo"), ("low", "bajo"))},
        "by_income_l3_pct": {k: num(f"titular.ingreso.{c}.l3", 2) for k, c in
                             (("high", "alto"), ("upper-middle", "medio_alto"), ("lower-middle", "medio_bajo"), ("low", "bajo"))},
        "h1_slope_pp_per_log_gdp": num("h1.pendiente", 2),
        "h1_slope_ci95": [num("h1.pendiente.lo", 2), num("h1.pendiente.hi", 2)],
        "l3_peak_minutes": num("h4.pico.minutos", 1),
        "claims_ids": ["titular.global.l2", "titular.global.l3", "titular.ingreso.*", "h1.pendiente", "h4.pico.minutos"],
    }
    index = {
        "name": "Agent Delegability Index (ADI)",
        "title": TITLE,
        "headline": headline,
        "coverage": {"tasks": C.get("cobertura.tareas"), "isco08_unit_groups": len(isco), "countries": len(pais),
                     "employment_millions": num("cobertura.empleo_millones", 1), "models": ["claude-sonnet-5-5", "claude-haiku-5-5"]},
        "endpoints": {"occupation": "isco/{isco08}.json", "country": "country/{iso3}.json",
                      "schema": "README.md", "data_dictionary": "../DATA_DICTIONARY.md"},
        "occupations": [{"isco08": r.isco08, "titulo": r.titulo, "adi_l2": limpio(r.adi_l2), "adi_l3": limpio(r.adi_l3),
                         "adi_share": limpio(r.adi_share)} for _, r in isco.sort_values("isco08").iterrows()],
        "countries": [{"iso3": r.iso3, "pais": r.pais, "ingreso": r.ingreso, "adi_l2": limpio(r.adi_l2), "adi_l3": limpio(r.adi_l3),
                       "adi_share": limpio(r.adi_share)} for _, r in pais.sort_values("iso3").iterrows()],
        **comun,
    }
    escribir_json(API / "index.json", index)

    # 5. checksums (rutas relativas a release/v2026.1, orden estable)
    archivos = sorted(p for p in DEST.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    lineas = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(DEST).as_posix()}" for p in archivos]
    (DEST / "SHA256SUMS").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    faltan = [n for n in ("DATA_DICTIONARY.md", "api/README.md") if not (DEST / n).exists()]
    print(f"release {VERSION}: {len(isco)} ocupaciones, {len(pais)} países, {len(tarea)} tareas; "
          f"claims {len(cl)} públicos ({pend} pendientes «--» y {dup} ids repetidos fuera); {len(archivos)} archivos en SHA256SUMS")
    if faltan:
        print(f"AVISO: faltan {faltan}; vuelve a correr cuando existan para que entren en SHA256SUMS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
