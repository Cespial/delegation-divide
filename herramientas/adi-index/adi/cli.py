"""Command-line interface: ``adi lookup 2631``, ``adi country COL``, ``adi top``, ``adi cite``."""
from __future__ import annotations

import argparse
import json
import sys

import adi


def _emit(obj, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return
    # plain text
    records = obj if isinstance(obj, list) else [obj]
    for rec in records:
        for k, v in rec.items():
            if k in {"citation", "warning"}:
                continue
            print(f"{k}: {v}")
        print()
    warn = next((r.get("warning") for r in records if isinstance(r, dict) and r.get("warning")), None)
    if warn:
        print(f"WARNING: {warn}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="adi",
        description="Agent Delegability Index (ADI) — query and cite the index.",
    )
    p.add_argument("--format", "-f", choices=["json", "text"], default="json",
                   help="output format for data commands (default json)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("lookup", help="one ISCO-08 unit group (4 digits)")
    s.add_argument("isco")
    s = sub.add_parser("search", help="occupations whose title contains TEXT")
    s.add_argument("text")
    s = sub.add_parser("country", help="country profile (ISO3)")
    s.add_argument("iso3")
    s = sub.add_parser("top", help="highest-scoring occupations")
    s.add_argument("-n", type=int, default=10)
    s.add_argument("--level", choices=["l2", "l3", "share"], default="l2")
    s = sub.add_parser("cite", help="citation for the paper/dataset")
    s.add_argument("style", nargs="?", choices=["bibtex", "apa", "text"], default="bibtex")
    sub.add_parser("version", help="package and data version")

    a = p.parse_args(argv)
    try:
        if a.cmd == "lookup":
            _emit(adi.lookup(a.isco), a.format)
        elif a.cmd == "search":
            _emit(adi.search(a.text), a.format)
        elif a.cmd == "country":
            _emit(adi.country(a.iso3), a.format)
        elif a.cmd == "top":
            _emit(adi.top(a.n, a.level), a.format)
        elif a.cmd == "cite":
            print(adi.cite(a.style))
            if adi.is_synthetic():
                print(f"WARNING: {adi.SYNTHETIC_WARNING}", file=sys.stderr)
        elif a.cmd == "version":
            _emit(adi.version(), a.format)
    except (KeyError, ValueError, FileNotFoundError) as e:
        msg = e.args[0] if e.args else str(e)
        print(f"error: {msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
