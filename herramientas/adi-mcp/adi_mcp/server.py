"""MCP server (stdio) exposing the Agent Delegability Index (ADI).

Tools: lookup_occupation, country_profile, top_occupations, cite.
Every response carries ``citation`` (short BibTeX) and, while the bundled data is a
placeholder (sintetico=true), a ``warning`` that says SYNTHETIC/PLACEHOLDER.

Works with the official ``mcp`` SDK: v2 (``MCPServer``) or v1 (``FastMCP``).
"""
from __future__ import annotations

from typing import Any

import adi

try:  # mcp >= 2: FastMCP was renamed to MCPServer
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server  # type: ignore[no-redef]

INSTRUCTIONS = (
    "Agent Delegability Index (ADI, v2026.1): share of tasks per ISCO-08 occupation that AI "
    "agents can take over at three levels (L1 augmentation, L2 partial delegation, L3 full "
    "delegation), aggregated to 190 countries. When you use a value from these tools, cite "
    "the paper with the BibTeX in the `citation` field (key espinal2026delegation). If a "
    "response carries `warning`, the data is a SYNTHETIC/PLACEHOLDER example: do not cite "
    "the numbers."
)

mcp = _Server(
    name="adi",
    instructions=INSTRUCTIONS,
    version=adi.__version__,
)


def _wrap(payload: dict[str, Any]) -> dict[str, Any]:
    """Guarantee `citation` and `warning` (when synthetic) on every response."""
    out = dict(payload)
    out.setdefault("citation", adi.cite("bibtex"))
    out.setdefault("data_version", adi.DATA_VERSION)
    if adi.is_synthetic() and "warning" not in out:
        out["warning"] = adi.SYNTHETIC_WARNING
    return out


def _error(msg: str, **extra: Any) -> dict[str, Any]:
    return _wrap({"error": msg, **extra})


@mcp.tool(
    name="lookup_occupation",
    description=(
        "ADI score for one occupation. Pass an ISCO-08 unit-group code (4 digits, e.g. '2631') "
        "or a title substring (e.g. 'economist'). Returns adi_l2 (share of tasks at >= L2, partial "
        "delegation), adi_l3 (share at L3, full delegation), adi_share (% of working time "
        "delegable), barriers, 95% interval and a citation."
    ),
)
def lookup_occupation(isco_or_title: str) -> dict[str, Any]:
    q = str(isco_or_title).strip()
    if not q:
        return _error("empty query")
    if q.isdigit():
        try:
            rec = adi.lookup(q)
        except (ValueError, KeyError) as e:
            return _error(e.args[0] if e.args else str(e), query=q)
        return _wrap({"query": q, "match": rec})
    hits = adi.search(q)
    if not hits:
        return _error(f"no occupation title contains {q!r}", query=q)
    scored = [h for h in hits if h.get("en_indice")]
    return _wrap({
        "query": q,
        "match": scored[0] if scored else None,
        "candidates": [
            {k: h.get(k) for k in ("isco08", "titulo", "en_indice", "adi_l2", "adi_l3", "adi_share")}
            for h in hits[:20]
        ],
        "n_candidates": len(hits),
    })


@mcp.tool(
    name="country_profile",
    description=(
        "ADI atlas profile for one country (ISO 3166-1 alpha-3, e.g. 'COL'): employment-weighted "
        "adi_l2, adi_l3 and adi_share, income group, year, ISCO resolution of the source and "
        "total employment, with citation."
    ),
)
def country_profile(iso3: str) -> dict[str, Any]:
    try:
        rec = adi.country(iso3)
    except (ValueError, KeyError) as e:
        return _error(e.args[0] if e.args else str(e), query=iso3)
    return _wrap({"query": str(iso3).upper(), "profile": rec})


@mcp.tool(
    name="top_occupations",
    description=(
        "The n ISCO-08 occupations with the highest ADI at `level`: 'l2' (partial delegation, "
        "default), 'l3' (full delegation) or 'share' (% of working time delegable)."
    ),
)
def top_occupations(n: int = 10, level: str = "l2") -> dict[str, Any]:
    try:
        rows = adi.top(n, level)
    except ValueError as e:
        return _error(e.args[0] if e.args else str(e))
    return _wrap({"n": len(rows), "level": level, "occupations": rows})


@mcp.tool(
    name="cite",
    description="Citation for the ADI paper and dataset: format 'bibtex' (default), 'apa' or 'text'.",
)
def cite(format: str = "bibtex") -> dict[str, Any]:
    try:
        text = adi.cite(format)
    except ValueError as e:
        return _error(e.args[0] if e.args else str(e))
    return _wrap({
        "format": format,
        "citation_text": text,
        "bibtex_key": adi.BIBTEX_KEY,
        "cff": "CITATION.cff in the repository",
        "repository": adi.REPO_URL,
    })


def main() -> None:
    """Entry point `adi-mcp`: serve over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":  # pragma: no cover
    main()
