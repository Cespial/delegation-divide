"""adi — Agent Delegability Index (ADI) lookup, search and citation.

Public API:
    lookup(isco)            -> dict   one ISCO-08 unit group (4 digits)
    search(title_substring) -> list   occupations whose title contains the text
    country(iso3)           -> dict   country profile from the atlas
    top(n, level='l2')      -> list   n highest-scoring occupations
    cite(format='bibtex')   -> str    'bibtex' | 'apa' | 'text'
    version()               -> dict   package, data version, synthetic flag

Every record carries ``citation`` (short BibTeX) and, while the bundled data is a
placeholder (column ``sintetico`` == true), a ``warning`` field that says so.
"""
from __future__ import annotations

import csv
import os
from functools import lru_cache
from pathlib import Path

__version__ = "2026.1"
DATA_VERSION = "v2026.1"
REPO_URL = "https://github.com/Cespial/delegation-divide"
BIBTEX_KEY = "espinal2026delegation"
PREREG_DOI = "10.17605/OSF.IO/9ZNTF"
DATA_DOI = "10.5281/zenodo.23552918"

SYNTHETIC_WARNING = (
    "SYNTHETIC/PLACEHOLDER data: these values come from example rows marked "
    "sintetico=true, not from the real ADI v2026.1 index. Do not cite them as "
    f"results. Real data will ship with the paper; see {REPO_URL}."
)

_LEVELS = {"l2": "adi_l2", "l3": "adi_l3", "share": "adi_share"}

__all__ = [
    "lookup", "search", "country", "top", "cite", "version", "PREREG_DOI", "DATA_DOI",
    "SYNTHETIC_WARNING", "DATA_VERSION", "__version__", "data_dir", "is_synthetic",
]


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
def data_dir() -> Path:
    """Directory with adi_isco.csv / adi_pais.csv. Override with $ADI_DATA_DIR."""
    override = os.environ.get("ADI_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).parent / "data"


def _to_bool(v: str) -> bool:
    return str(v).strip().lower() in {"true", "1", "yes", "si", "sí", "t"}


def _to_num(v: str):
    s = str(v).strip()
    if s == "" or s.lower() in {"na", "nan", "none", "null"}:
        return None
    try:
        return int(s) if s.lstrip("-").isdigit() else float(s)
    except ValueError:
        return s


_TEXT_COLS = {"isco08", "titulo", "iso3", "pais", "ingreso", "resolucion", "descripcion"}
_BOOL_COLS = {"sintetico"}


def _typed(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        if k in _BOOL_COLS:
            out[k] = _to_bool(v)
        elif k in _TEXT_COLS:
            out[k] = str(v).strip()
        else:
            out[k] = _to_num(v)
    return out


def _read_csv(name: str) -> list[dict]:
    path = data_dir() / name
    if not path.exists():
        raise FileNotFoundError(
            f"{name} not found in {data_dir()}. Run herramientas/adi-index/sincronizar.sh "
            "or set ADI_DATA_DIR."
        )
    with path.open(newline="", encoding="utf-8") as f:
        return [_typed(r) for r in csv.DictReader(f)]


@lru_cache(maxsize=1)
def _isco_rows() -> list[dict]:
    return _read_csv("adi_isco.csv")


@lru_cache(maxsize=1)
def _pais_rows() -> list[dict]:
    return _read_csv("adi_pais.csv")


@lru_cache(maxsize=1)
def _isco_ref() -> dict[str, dict]:
    """Canonical ISCO-08 unit groups (436) if the reference CSV is bundled; else {}."""
    path = data_dir() / "isco08_grupos_unitarios.csv"
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        return {r["isco08"].strip().zfill(4): r for r in csv.DictReader(f)}


def _reload() -> None:
    """Clear caches (used by tests after changing ADI_DATA_DIR)."""
    _isco_rows.cache_clear()
    _pais_rows.cache_clear()
    _isco_ref.cache_clear()


def is_synthetic() -> bool:
    """True if any bundled row is marked sintetico=true."""
    try:
        return any(r.get("sintetico") for r in _isco_rows()) or any(
            r.get("sintetico") for r in _pais_rows()
        )
    except FileNotFoundError:
        return False


def _decorate(rec: dict) -> dict:
    """Attach citation and synthetic warning to a record."""
    rec = dict(rec)
    rec["version"] = DATA_VERSION
    rec["citation"] = cite("bibtex")
    if rec.get("sintetico"):
        rec["warning"] = SYNTHETIC_WARNING
    return rec


# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------
def _norm_isco(isco: str | int) -> str:
    code = str(isco).strip()
    if not (code.isdigit() and len(code) == 4):
        raise ValueError(f"ISCO-08 unit group must be 4 digits, got {isco!r}")
    ref = _isco_ref()
    if ref and code not in ref:
        raise KeyError(f"{code} is not an ISCO-08 unit group (436 canonical codes)")
    return code


def lookup(isco: str | int) -> dict:
    """Return the ADI record for one ISCO-08 unit group (4-digit code)."""
    code = _norm_isco(isco)
    for r in _isco_rows():
        if r["isco08"].zfill(4) == code:
            return _decorate(r)
    ref = _isco_ref().get(code)
    title = f" ({ref['titulo']})" if ref else ""
    raise KeyError(f"ISCO-08 {code}{title} is valid but has no ADI score in {DATA_VERSION}")


def search(title_substring: str) -> list[dict]:
    """Occupations whose title contains the text (case-insensitive).

    Scored occupations come first with full ADI fields; canonical ISCO-08 groups
    without a score (from the reference list) follow with ``en_indice=False``.
    """
    q = str(title_substring).strip().lower()
    if not q:
        return []
    hits: list[dict] = []
    seen: set[str] = set()
    for r in _isco_rows():
        if q in r["titulo"].lower():
            rec = _decorate(r)
            rec["en_indice"] = True
            hits.append(rec)
            seen.add(r["isco08"].zfill(4))
    for code, ref in _isco_ref().items():
        if code in seen:
            continue
        if q in ref["titulo"].lower():
            hits.append({
                "isco08": code, "titulo": ref["titulo"], "en_indice": False,
                "version": DATA_VERSION, "citation": cite("bibtex"),
            })
    return hits


def country(iso3: str) -> dict:
    """Country profile from the ADI atlas (ISO 3166-1 alpha-3)."""
    code = str(iso3).strip().upper()
    if len(code) != 3 or not code.isalpha():
        raise ValueError(f"iso3 must be a 3-letter ISO 3166-1 code, got {iso3!r}")
    for r in _pais_rows():
        if r["iso3"].upper() == code:
            return _decorate(r)
    raise KeyError(f"{code} not in the ADI atlas {DATA_VERSION}")


def top(n: int = 10, level: str = "l2") -> list[dict]:
    """The n occupations with the highest ADI at ``level`` ('l2', 'l3' or 'share')."""
    col = _LEVELS.get(str(level).lower())
    if col is None:
        raise ValueError(f"level must be one of {sorted(_LEVELS)}, got {level!r}")
    rows = [r for r in _isco_rows() if r.get(col) is not None]
    rows.sort(key=lambda r: r[col], reverse=True)
    return [_decorate(r) for r in rows[: max(int(n), 0)]]


_TITLE = ("The Delegation Divide: An Open Index of AI-Agent Delegability "
          "across Occupations and Countries")


def cite(format: str = "bibtex") -> str:
    """Citation for the ADI paper and dataset ('bibtex', 'apa' or 'text')."""
    fmt = str(format).lower()
    if fmt == "bibtex":
        return (
            f"@article{{{BIBTEX_KEY},\n"
            f"  title   = {{{_TITLE}}},\n"
            "  author  = {Espinal Maya, Cristian and Jim{\\'e}nez Londo{\\~n}o, Santiago},\n"
            "  journal = {arXiv preprint},\n"
            "  year    = {2026},\n"
            f"  url     = {{{REPO_URL}}},\n"
            f"  note    = {{Data: doi:{DATA_DOI}. Preregistration: doi:{PREREG_DOI}}}\n"
            "}"
        )
    if fmt == "apa":
        return (
            f"Espinal Maya, C., & Jiménez Londoño, S. (2026). {_TITLE}. "
            f"arXiv preprint. Data: https://doi.org/{DATA_DOI}. Preregistration: https://doi.org/{PREREG_DOI}"
        )
    if fmt == "text":
        return (
            f"Espinal Maya & Jiménez Londoño (2026), \"{_TITLE}\", arXiv preprint, "
            f"Agent Delegability Index {DATA_VERSION}, {REPO_URL}"
        )
    raise ValueError("format must be 'bibtex', 'apa' or 'text'")


def version() -> dict:
    """Package version, data version and whether the data is a placeholder."""
    info = {
        "package": "adi-index",
        "package_version": __version__,
        "data_version": DATA_VERSION,
        "data_dir": str(data_dir()),
        "synthetic": is_synthetic(),
        "repository": REPO_URL,
    }
    if info["synthetic"]:
        info["warning"] = SYNTHETIC_WARNING
    return info
