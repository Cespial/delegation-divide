"""Offline tests for adi-mcp: tools registered, every response carries citation (+warning if synthetic)."""
import asyncio
import json

import adi
from adi_mcp import server


def _run(coro):
    return asyncio.run(coro)


def _payload(result):
    sc = getattr(result, "structuredContent", None)
    if sc:
        return sc.get("result", sc) if isinstance(sc, dict) and "result" in sc and len(sc) == 1 else sc
    return json.loads(result.content[0].text)


def test_tools_registered():
    names = {t.name for t in _run(server.mcp.list_tools())}
    assert names == {"lookup_occupation", "country_profile", "top_occupations", "cite"}


def test_lookup_by_code_has_citation_and_warning():
    p = _payload(_run(server.mcp.call_tool("lookup_occupation", {"isco_or_title": "2631"})))
    assert p["match"]["isco08"] == "2631"
    assert "espinal2026delegation" in p["citation"]
    if adi.is_synthetic():
        assert "SYNTHETIC/PLACEHOLDER" in p["warning"]


def test_lookup_by_title():
    p = _payload(_run(server.mcp.call_tool("lookup_occupation", {"isco_or_title": "software"})))
    assert p["match"]["isco08"] == "2512"
    assert p["n_candidates"] >= 1


def test_lookup_error_still_cites():
    p = _payload(_run(server.mcp.call_tool("lookup_occupation", {"isco_or_title": "9999"})))
    assert "error" in p and "citation" in p


def test_country_and_top_and_cite():
    c = _payload(_run(server.mcp.call_tool("country_profile", {"iso3": "col"})))
    assert c["profile"]["iso3"] == "COL" and "citation" in c
    t = _payload(_run(server.mcp.call_tool("top_occupations", {"n": 2, "level": "l3"})))
    assert t["n"] == 2 and t["occupations"][0]["adi_l3"] >= t["occupations"][1]["adi_l3"]
    z = _payload(_run(server.mcp.call_tool("cite", {"format": "apa"})))
    assert z["citation_text"].startswith("Espinal Maya, C.")
    assert z["bibtex_key"] == "espinal2026delegation"
