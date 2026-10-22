"""Escribe release/arxiv/METADATOS.md (título, autores, abstract en texto plano, categorías, comentarios, licencia)
con las cifras leídas de salidas/claims.jsonl. Falla si el abstract supera 1.920 caracteres o si una cifra falta.

Uso (desde la raíz del repo):  .venv/bin/python -I release/arxiv/metadatos.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
C = {}
for l in (RAIZ / "salidas/claims.jsonl").read_text(encoding="utf-8").splitlines():
    if l.strip():
        c = json.loads(l)
        C[c["id"]] = c


def v(i: str) -> float:
    c = C[i]
    if c.get("sintetico") or not isinstance(c["valor"], (int, float)):
        raise ValueError(f"{i}: cifra no publicable ({c['valor']!r})")
    return float(c["valor"])


f1 = lambda i: f"{v(i):.1f}"
f2 = lambda i: f"{v(i):.2f}"
p_h2 = v("h2.brecha.medio.p")

TITULO = "The Delegation Divide: An Open Index of AI-Agent Delegability across Occupations and Countries"
ABSTRACT = (
    f"{f1('titular.global.l2')}% of task time in world employment is at least partly delegable to AI agents in 2026, "
    f"and only {f1('titular.global.l3')}% can be handed over in full. "
    "Existing measures score exposure to generative AI, mostly for the United States. "
    f"We build the Agent Delegability Index (ADI): two language models rate all {int(v('cobertura.tareas')):,} O*NET 30.2 "
    "task statements on a frozen, preregistered rubric of delegation levels and barriers; tasks are mapped to "
    f"{int(v('cobertura.isco'))} ISCO-08 unit groups and weighted by ILOSTAT employment in {int(v('cobertura.paises'))} countries. "
    "Four findings. "
    f"First, delegable employment rises with income, from {f1('titular.ingreso.bajo.l2')}% in low-income to "
    f"{f1('titular.ingreso.alto.l2')}% in high-income countries, a slope of {f2('h1.pendiente')} percentage points per "
    "log point of GDP per capita. This delegation divide is compositional: the physical barrier dominates the jobs "
    "poorer countries employ most. "
    f"Second, at the occupation level ADI tracks exposure closely (r = {f2('h3.r.eloundou')} with Eloundou et al. and "
    f"{f2('h3.r.felten')} with Felten et al.), above the preregistered bound of 0.80; ADI adds delegation levels and "
    "barriers on top of exposure, for the world, not a new ranking of occupations. "
    f"Third, full delegation is rare and peaks for tasks that take a human about twelve minutes "
    f"({f1('h4.pico.minutos')} minutes). "
    f"Fourth, the preregistered adoption gap is not supported: across {int(v('h2.n'))} countries, delegability and "
    f"observed AI usage correlate at r = {f2('h2.r.adi_uso')}, and the gap between them is not wider in middle-income "
    f"countries (p = {p_h2:.2f}). "
    f"Model agreement is kappa = {f2('agree.kappa.sonnet_haiku')}; human validation is in progress. "
    "We release the index, the atlas, the prompts and an MCP server at https://github.com/Cespial/delegation-divide."
)
COMENTARIOS = ("31 pages, 6 figures, 4 tables. Preregistered at OSF: 10.17605/OSF.IO/9ZNTF. "
               "Data and code: doi:10.5281/zenodo.23552918; repository and MCP server: https://github.com/Cespial/delegation-divide")


def main() -> int:
    n = len(ABSTRACT)
    if n > 1920:
        print(f"ERROR: abstract de {n} caracteres (> 1.920)", file=sys.stderr)
        return 1
    if any(ch in ABSTRACT for ch in "\\{}$"):
        print("ERROR: el abstract trae LaTeX", file=sys.stderr)
        return 1
    md = f"""# arXiv — metadatos de envío (borrador para aprobación de Cristian)

Generado por `release/arxiv/metadatos.py` desde `salidas/claims.jsonl`. No editar a mano: regenerar.

## Título

{TITULO}

## Autores (campo «Authors» de arXiv)

Cristian Espinal Maya (Universidad Nacional de Colombia), Santiago Jiménez Londoño (Universidad EAFIT)

- Cristian Espinal Maya — Universidad Nacional de Colombia, Facultad de Minas — ORCID 0009-0000-1009-8388 — autor de contacto (envía)
- Santiago Jiménez Londoño — Universidad EAFIT — ORCID 0009-0007-9862-7133

## Abstract (texto plano, {n} caracteres de 1.920 permitidos)

```
{ABSTRACT}
```

## Categorías

- Primaria: **econ.GN** (General Economics)
- Cruzadas: **cs.CY** (Computers and Society), **cs.AI** (Artificial Intelligence)

## Comentarios (campo «Comments»)

```
{COMENTARIOS}
```

## Licencia

CC BY 4.0 (Creative Commons Attribution 4.0 International).

## Otros campos

- MSC/ACM: vacío. JEL (en el texto si se quiere): J24, O33, J21.
- Report number / Journal-ref / DOI: vacío (preprint).
- Archivo a subir: `release/arxiv/delegation-divide-arxiv.tar.gz` (generado por `release/arxiv/empaquetar.sh`,
  compila con pdflatex ×2 sin BibTeX porque trae `main.bbl`).
- Recordatorio del plan: enviar un lunes antes de las 14:00 ET.
"""
    (RAIZ / "release/arxiv/METADATOS.md").write_text(md, encoding="utf-8")
    print(f"METADATOS.md escrito; abstract {n} caracteres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
