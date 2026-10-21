# The Delegation Divide — Agent Delegability Index (ADI)

**An open index of AI-agent delegability for 436 ISCO-08 occupations and 190 countries.**

> Headline: *[NUMBER] % of tasks in world employment are delegable to AI agents in 2026;
> [Y] % in middle-income countries versus [Z] % in high-income countries.* (to be filled by `claims.jsonl`)

ADI scores every ESCO task on three layers — **augmentation**, **partial delegation**, **full delegation** —
with four frontier models, validated against 1,500 human-rated tasks, and aggregates to ISCO-08 and to
countries via ILOSTAT. Cross-listed econ.GN · cs.CY · cs.AI.

- Paper: arXiv:XXXX.XXXXX (pending)
- Dataset: Zenodo DOI (pending) · Hugging Face `cespial/adi` (pending)
- Tool for agents: `pip install adi-index` · MCP server `adi-mcp` (`lookup_occupation`, `country_profile`, `cite`)
- Version: `v2026.1`

## Cite

```bibtex
@article{espinal2026delegation,
  title   = {The Delegation Divide: An Open Index of AI-Agent Delegability for 436 Occupations and 190 Countries},
  author  = {Espinal Maya, Cristian and Jim{\'e}nez Londo{\~n}o, Santiago},
  journal = {arXiv preprint},
  year    = {2026},
  url     = {https://github.com/Cespial/delegation-divide}
}
```

## Layout

| Dir | Content |
|---|---|
| `datos/` | ESCO, ILOSTAT, crosswalks, microdata (CO/MX/BR/PE) |
| `scoring/` | Rubric, prompts, model outputs |
| `analisis/` | Aggregation, index, atlas, validation |
| `validacion/` | Human rating protocol and sheets |
| `articulo/` | LaTeX, `claims.jsonl`, `reproducir.sh` |
| `herramientas/` | `adi-index` (PyPI) and `adi-mcp` (MCP server) |
| `docs/` | Plan, preregistration, decisions |

Licence: code MIT · data and figures CC-BY 4.0.
