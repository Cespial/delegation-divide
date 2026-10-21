"""Offline tests for adi-index (no network, bundled data only)."""
import json
import os
import subprocess
import sys

import pytest

import adi
from adi.cli import main


def test_version_fields():
    v = adi.version()
    assert v["package"] == "adi-index"
    assert v["package_version"] == adi.__version__
    assert v["data_version"] == "v2026.1"
    assert isinstance(v["synthetic"], bool)


def test_lookup_2631():
    r = adi.lookup("2631")
    assert r["isco08"] == "2631"
    assert "Economist" in r["titulo"]
    for k in ("adi_l2", "adi_l3", "adi_share", "n_tareas", "ic_lo", "ic_hi"):
        assert isinstance(r[k], (int, float))
    assert r["ic_lo"] <= r["adi_share"] <= r["ic_hi"]
    assert "@article{espinal2026delegation" in r["citation"]


def test_lookup_accepts_int():
    assert adi.lookup(2512)["isco08"] == "2512"


def test_synthetic_warning_present_when_flagged():
    r = adi.lookup("2631")
    if r["sintetico"]:
        assert "SYNTHETIC/PLACEHOLDER" in r["warning"]
        assert adi.version()["synthetic"] is True
    else:
        assert "warning" not in r


def test_lookup_rejects_bad_code():
    with pytest.raises(ValueError):
        adi.lookup("26")
    with pytest.raises(ValueError):
        adi.lookup("abcd")


def test_lookup_invalid_or_unscored_raises_keyerror():
    # 9999 is not an ISCO-08 unit group; 0110 is canonical but not in the placeholder.
    with pytest.raises(KeyError):
        adi.lookup("9999")
    if adi._isco_ref():
        with pytest.raises(KeyError):
            adi.lookup("0110")


def test_search_finds_scored_and_reference():
    hits = adi.search("econom")
    assert hits and hits[0]["isco08"] == "2631" and hits[0]["en_indice"] is True
    assert adi.search("") == []
    if adi._isco_ref():  # los grupos de referencia sin puntuar (p. ej. militares) se devuelven marcados
        assert all("en_indice" in h for h in adi.search("armed forces"))


def test_country():
    c = adi.country("col")
    assert c["iso3"] == "COL" and c["pais"] == "Colombia"
    assert isinstance(c["empleo_total"], int)
    with pytest.raises(KeyError):
        adi.country("ZZZ")
    with pytest.raises(ValueError):
        adi.country("colombia")


def test_top_sorted():
    rows = adi.top(3, "l2")
    assert len(rows) == 3
    assert rows[0]["adi_l2"] >= rows[1]["adi_l2"] >= rows[2]["adi_l2"]
    assert adi.top(2, "share")[0]["adi_share"] >= adi.top(2, "share")[1]["adi_share"]
    with pytest.raises(ValueError):
        adi.top(3, "l9")


def test_cite_formats():
    b = adi.cite("bibtex")
    assert b.startswith("@article{espinal2026delegation") and b.rstrip().endswith("}")
    assert "Jiménez Londoño" in adi.cite("apa")
    assert "v2026.1" in adi.cite("text")
    with pytest.raises(ValueError):
        adi.cite("ris")


def test_cli_lookup_json(capsys):
    assert main(["lookup", "2631"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["isco08"] == "2631" and "citation" in out


def test_cli_cite(capsys):
    assert main(["cite"]) == 0
    assert "@article{espinal2026delegation" in capsys.readouterr().out


def test_cli_error_code(capsys):
    assert main(["lookup", "12"]) == 1
    assert "error:" in capsys.readouterr().err


def test_cli_entry_point_subprocess():
    r = subprocess.run([sys.executable, "-m", "adi.cli", "version"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert r.returncode == 0 and '"data_version": "v2026.1"' in r.stdout
