# arXiv — metadatos de envío (borrador para aprobación de Cristian)

Generado por `release/arxiv/metadatos.py` desde `salidas/claims.jsonl`. No editar a mano: regenerar.

## Título

The Delegation Divide: An Open Index of AI-Agent Delegability across Occupations and Countries

## Autores (campo «Authors» de arXiv)

Cristian Espinal Maya (Universidad Nacional de Colombia), Santiago Jiménez Londoño (Universidad EAFIT)

- Cristian Espinal Maya — Universidad Nacional de Colombia, Facultad de Minas — ORCID 0009-0000-1009-8388 — autor de contacto (envía)
- Santiago Jiménez Londoño — Universidad EAFIT — ORCID 0009-0007-9862-7133

## Abstract (texto plano, 1657 caracteres de 1.920 permitidos)

```
35.2% of task time in world employment is at least partly delegable to AI agents in 2026, and only 2.5% can be handed over in full. Existing measures score exposure to generative AI, mostly for the United States. We build the Agent Delegability Index (ADI): two language models rate all 18,796 O*NET 30.2 task statements on a frozen, preregistered rubric of delegation levels and barriers; tasks are mapped to 433 ISCO-08 unit groups and weighted by ILOSTAT employment in 146 countries. Four findings. First, delegable employment rises with income, from 22.5% in low-income to 48.7% in high-income countries, a slope of 7.23 percentage points per log point of GDP per capita. This delegation divide is compositional: the physical barrier dominates the jobs poorer countries employ most. Second, at the occupation level ADI tracks exposure closely (r = 0.93 with Eloundou et al. and 0.89 with Felten et al.), above the preregistered bound of 0.80; ADI adds delegation levels and barriers on top of exposure, for the world, not a new ranking of occupations. Third, full delegation is rare and peaks for tasks that take a human about twelve minutes (11.8 minutes). Fourth, the preregistered adoption gap is not supported: across 101 countries, delegability and observed AI usage correlate at r = 0.86, and the gap between them is not wider in middle-income countries (p = 0.27). Model agreement is kappa = 0.77; a blind human rating of 300 tasks agrees with the model consensus at kappa = 0.85, and an agentic panel with web search at kappa = 0.87. We release the index, the atlas, the prompts and an MCP server at https://github.com/Cespial/delegation-divide.
```

## Categorías

- Primaria: **econ.GN** (General Economics)
- Cruzadas: **cs.CY** (Computers and Society), **cs.AI** (Artificial Intelligence)

## Comentarios (campo «Comments»)

```
32 pages, 6 figures, 4 tables. Preregistered at OSF: 10.17605/OSF.IO/9ZNTF. Data and code: doi:10.5281/zenodo.23552918; repository and MCP server: https://github.com/Cespial/delegation-divide
```

## Licencia

CC BY 4.0 (Creative Commons Attribution 4.0 International).

## Otros campos

- MSC/ACM: vacío. JEL (en el texto si se quiere): J24, O33, J21.
- Report number / Journal-ref / DOI: vacío (preprint).
- Archivo a subir: `release/arxiv/delegation-divide-arxiv.tar.gz` (generado por `release/arxiv/empaquetar.sh`,
  compila con pdflatex ×2 sin BibTeX porque trae `main.bbl`).
- Recordatorio del plan: enviar un lunes antes de las 14:00 ET.
