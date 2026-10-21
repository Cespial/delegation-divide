---
license: cc-by-4.0
pretty_name: "Agent Delegability Index (ADI) v2026.1"
language:
  - en
size_categories:
  - 10K<n<100K
task_categories:
  - tabular-classification
  - text-classification
tags:
  - ai-agents
  - delegation
  - automation
  - labor-economics
  - occupations
  - isco-08
  - onet
  - ilostat
  - economics
  - llm-as-a-judge
  - delegation-divide
configs:
  - config_name: adi_isco
    default: true
    data_files:
      - split: train
        path: adi_isco.parquet
  - config_name: adi_pais
    data_files:
      - split: train
        path: adi_pais.parquet
  - config_name: adi_tarea
    data_files:
      - split: train
        path: adi_tarea.parquet
---

# Agent Delegability Index (ADI) v2026.1

**35.2 % of task time in world employment is at least partly delegable to AI agents (L2 or L3) in 2026; only 2.5 % can
be handed over in full (L3).** Delegable employment rises with income — 22.5 % in low-income, 28.3 % in lower-middle,
35.0 % in upper-middle and 48.7 % in high-income countries — the *delegation divide* (7.23 percentage points per log point
of GDP per capita, 146 countries).

Dataset of the paper *The Delegation Divide: An Open Index of AI-Agent Delegability across Occupations and Countries*
(Espinal Maya & Jiménez Londoño, 2026). Preregistered at OSF: [doi:10.17605/OSF.IO/9ZNTF](https://doi.org/10.17605/OSF.IO/9ZNTF).
Code, rubric, MCP server and full pipeline: <https://github.com/Cespial/delegation-divide>.

## Configs

| config | rows | unit |
|---|---:|---|
| `adi_isco` (default) | 433 | ISCO-08 unit group (4 digits) |
| `adi_pais` | 146 | country (ISO 3166-1 alpha-3) |
| `adi_tarea` | 18,796 | O\*NET 30.2 task statement, with each model's level |

```python
from datasets import load_dataset
occ = load_dataset("cespial/adi", "adi_isco", split="train")
countries = load_dataset("cespial/adi", "adi_pais", split="train")
tasks = load_dataset("cespial/adi", "adi_tarea", split="train")
```

The repository also carries the same tables as CSV, `claims.jsonl` (every number in the paper), the raw model outputs
(`ratings_sonnet.jsonl.gz`, `ratings_haiku.jsonl.gz`), a static JSON API (`api/isco/<code>.json`,
`api/country/<ISO3>.json`, `api/index.json`), `DATA_DICTIONARY.md` and `SHA256SUMS`.

## Rating scale (verbatim from the frozen rubric)

- **L0 — No meaningful role.** The agent cannot perform or materially speed up any substantial part of the task.
- **L1 — Augmentation.** A human performs the task; the AI assists step by step (drafts, searches, suggestions). The human
  stays in the loop at each step and produces the output.
- **L2 — Partial delegation.** An agent can execute substantial sub-steps of the task end to end from a goal
  specification. A human still has to perform at least one essential step or review and correct the work before use.
- **L3 — Full delegation.** An agent can complete the whole task end to end, to the quality a competent worker would
  accept, given only the goal and access. The human's role is limited to assigning it and accepting the result.

Reference technology: publicly available AI agents as of October 2026 (tool use, code execution, browsing, computer use,
file handling; no physical body). Ratings measure technical feasibility, not adoption or legality. Each task also carries
the share of working time an agent could take over, the minutes a human needs, and four barrier flags (physical,
accountability, trust, access).

## Main columns

- `adi_isco`: `isco08`, `titulo`, `adi_l2` (share 0–1 of task weight at L2+), `adi_l3` (share at L3), `adi_share` (% of
  working time delegable), `n_tareas`, `barrera_{fisica,responsabilidad,confianza,acceso}`, `ic_lo`/`ic_hi` (95 % bootstrap
  interval of `adi_share`).
- `adi_pais`: `iso3`, `pais`, `ingreso` (World Bank FY2026), `anio`, `resolucion` (ISCO level of the employment data),
  `adi_l2`, `adi_l3`, `adi_share` (employment-weighted), `empleo_total`.
- `adi_tarea`: `task_id` (O\*NET), `titulo`, `texto`, consensus `nivel`, `share`, `minutos`, barrier fractions,
  `nivel_sonnet`, `nivel_haiku`.

Types, units and definitions for every column: `DATA_DICTIONARY.md`.

## How it was built

Raters: Claude Sonnet 5.5 (primary) and Claude Haiku 5.5 (secondary), one task per call, neutral configuration, rubric
hash checked before every run. Consensus: lower level when the models disagree (quadratic-weighted κ = 0.77 between them).
Tasks are weighted by O\*NET importance × frequency and carried to ISCO-08 through O\*NET-SOC 2019 → SOC 2010 → ISCO-08
(433 of 436 unit groups). Country scores weight unit groups by ILOSTAT employment (latest year ≥ 2019, 2-digit or 1-digit
ISCO) with within-group four-digit weights from BLS OES (high income) or Colombia's GEIH (other groups).

## Limitations

- Ratings come from two models of one developer; human validation (blind rater, 300 tasks) is in progress and not yet
  reported in v2026.1.
- O\*NET describes work in the United States; the same task mix is carried to every country, so cross-country
  differences are compositional.
- Technical delegability is an upper bound on delegation, not a forecast of employment effects.

## Licence and attribution

CC BY 4.0. Includes information from the O\*NET 30.2 Database by the U.S. Department of Labor, Employment and Training
Administration (USDOL/ETA), used under the CC BY 4.0 license (task statements are reproduced verbatim in `adi_tarea`).
ESCO, ILOSTAT, World Bank, BLS and DANE inputs are used only as derived aggregates.

## Citation

```bibtex
@article{espinal2026delegation,
  title   = {The Delegation Divide: An Open Index of AI-Agent Delegability across Occupations and Countries},
  author  = {Espinal Maya, Cristian and Jim{\'e}nez Londo{\~n}o, Santiago},
  journal = {arXiv preprint},
  year    = {2026},
  url     = {https://github.com/Cespial/delegation-divide},
  note    = {Preregistration: doi:10.17605/OSF.IO/9ZNTF}
}
```
