# ADI v2026.1 — data dictionary

Agent Delegability Index (ADI), release `v2026.1`. Paper: *The Delegation Divide: An Open Index of AI-Agent
Delegability across Occupations and Countries* (Espinal Maya & Jiménez Londoño, 2026). Preregistration:
doi:10.17605/OSF.IO/9ZNTF. Repository: https://github.com/Cespial/delegation-divide.
Licence of this folder: CC BY 4.0 (data); see "Third-party sources" at the end.

Every file comes as CSV (UTF-8, comma, header row, `.` decimal) and, for the three tables, as Parquet (zstd) with the
same columns and the types below. Integrity: `sha256sum -c SHA256SUMS` from this folder.

## Rating scale (verbatim from `scoring/prompts/rubrica_v1.md`, frozen at preregistration, SHA-256 `bcd076fb…0ea0e46`)

- **L0 — No meaningful role.** The agent cannot perform or materially speed up any substantial part of the task.
- **L1 — Augmentation.** A human performs the task; the AI assists step by step (drafts, searches, suggestions). The human
  stays in the loop at each step and produces the output.
- **L2 — Partial delegation.** An agent can execute substantial sub-steps of the task end to end from a goal
  specification. A human still has to perform at least one essential step or review and correct the work before use.
- **L3 — Full delegation.** An agent can complete the whole task end to end, to the quality a competent worker would
  accept, given only the goal and access. The human's role is limited to assigning it and accepting the result.

Reference technology (fixed): publicly available AI agents as of October 2026 — frontier language models with tool use,
code execution, web browsing, computer use and file handling, no physical body or robotics. Ratings record technical
feasibility, not adoption and not legality.

Raters: Claude Sonnet 5.5 (primary) and Claude Haiku 5.5 (secondary). Consensus per task = modal level, ties resolved to
the lower level (with two raters: the lower of the two when they disagree).

## `adi_isco.csv` / `.parquet` — one row per ISCO-08 unit group (433 rows)

| column | type | unit | definition |
|---|---|---|---|
| isco08 | string (4 digits, zero-padded) | code | ISCO-08 unit group. 433 of the 436 groups; the three armed-forces groups (0110, 0210, 0310) have no O\*NET tasks. |
| titulo | string | — | ISCO-08 unit group title (English, from ESCO v1.2). |
| adi_l2 | float64 | share 0–1 | **ADI_o**: task-weighted share of the occupation's tasks whose consensus level is L2 or L3 (partial delegation or better). Headline index. |
| adi_l3 | float64 | share 0–1 | **ADI3_o**: task-weighted share at L3 (full delegation). |
| adi_share | float64 | percent 0–100 | **ADIs_o**: task-weighted mean of `share_delegable`, the percent of a task's working time an agent could take over. |
| n_tareas | int64 | count | O\*NET task statements mapped to the unit group through the crosswalk. |
| barrera_fisica | float64 | share 0–1 | Task-weighted fraction of model ratings flagging `barrier_physical` (task needs physical presence or manipulation). |
| barrera_responsabilidad | float64 | share 0–1 | Same for `barrier_accountability` (law, licence or professional liability requires a human to perform or sign). |
| barrera_confianza | float64 | share 0–1 | Same for `barrier_trust` (task depends on in-person trust, care or persuasion). |
| barrera_acceso | float64 | share 0–1 | Same for `barrier_access` (task depends on systems, data or places an agent would normally not reach). |
| ic_lo, ic_hi | float64 | percent 0–100 | 95 % percentile interval of `adi_share` from 1,000 bootstrap draws (tasks resampled within occupation, seed 20261020). |
| sintetico | bool | — | `false` for every row in this release. `true` would mark a placeholder row; never cite such rows. |

Task weights `w_ot` = importance × mean frequency category (O\*NET 30.2 Task Ratings), normalised within the O\*NET-SOC
occupation, multiplied by the crosswalk weight 1/k (SOC code mapping to k ISCO groups) and renormalised to sum to 1
within the unit group. Seven unit groups (3413, 3511, 4213, 7133, 8155, 8159, 9613) inherit the tasks of their
three-digit minor group (`imputado = true` in the API JSON).

## `adi_pais.csv` / `.parquet` — one row per country (146 rows)

| column | type | unit | definition |
|---|---|---|---|
| iso3 | string | code | ISO 3166-1 alpha-3. |
| pais | string | — | Country name (World Bank). |
| ingreso | string | category | World Bank income group, FY2026: `high`, `upper-middle`, `lower-middle`, `low`. |
| anio | int64 | year | Reference year of the ILOSTAT employment-by-occupation series used (latest available, ≥ 2019). |
| resolucion | string | category | Finest ISCO-08 level the country reports and that passes the completeness rule: `isco08_2d` (sub-major groups) or `isco08_1d` (major groups). |
| adi_l2 | float64 | share 0–1 | **ADI_c**: employment-weighted mean of ADI_o. Within a reported group, unit groups are weighted with four-digit employment from BLS OES 2024 (high income) or Colombia's GEIH (other groups); see paper §4.3. |
| adi_l3 | float64 | share 0–1 | Employment-weighted mean of ADI3_o. |
| adi_share | float64 | percent 0–100 | Employment-weighted mean of ADIs_o. |
| empleo_total | int64 | persons | Total employment (ILOSTAT, `EMP_TEMP_SEX_OCU_NB`) used as weights. |
| sintetico | bool | — | `false` for every row in this release. |

World and income-group headlines (in `claims.jsonl`) are the employment-weighted means of `adi_l2`/`adi_l3` over these rows.

## `adi_tarea.csv` / `.parquet` — one row per O\*NET task statement (18,796 rows)

| column | type | unit | definition |
|---|---|---|---|
| task_id | int64 | code | O\*NET 30.2 `Task ID`. Key to `ratings_*.jsonl.gz`. |
| titulo | string | — | O\*NET-SOC 2019 occupation title the statement belongs to (the title shown to the rater). |
| texto | string | — | Task statement, verbatim from O\*NET 30.2. |
| nivel | float64 | level 0–3 | Consensus level across models (lower level on ties). Empty if no model returned a valid rating. |
| share | float64 | percent 0–100 | Consensus `share_delegable` (median across models; with two models, their mean). |
| minutos | float64 | minutes | Consensus `minutes_human`: typical minutes a competent human needs for one instance (median across models). |
| n_modelos | int64 | count | Number of models with a valid rating (0–2). |
| barrera_fisica, barrera_responsabilidad, barrera_confianza, barrera_acceso | float64 | share 0–1 | Fraction of models flagging each barrier (0, 0.5 or 1). |
| nivel_haiku | float64 | level 0–3 | Level from Claude Haiku 5.5 (empty if its call failed validation). |
| nivel_sonnet | float64 | level 0–3 | Level from Claude Sonnet 5.5. |
| sintetico | bool | — | `false` for every row in this release. |

## `ratings_sonnet.jsonl.gz`, `ratings_haiku.jsonl.gz` — raw model outputs (one JSON object per line)

| field | type | unit | definition |
|---|---|---|---|
| task_id | int | code | O\*NET `Task ID`. |
| level | int | 0–3 | Rubric level (L0–L3 above). |
| share_delegable | int | percent 0–100 | Percent of the task's working time an agent could take over. |
| minutes_human | int | minutes | Typical minutes a competent human needs for one instance of the task. |
| barrier_physical, barrier_accountability, barrier_trust, barrier_access | bool | — | Barrier flags as defined in the rubric. |
| confidence | string | LOW/MEDIUM/HIGH | Rater's self-reported confidence. |
| modelo | string | — | `sonnet` or `haiku`. |
| rubrica_sha | string | hex | First 16 hex digits of the rubric's SHA-256 (must be `bcd076fb705f0f36`). |
| ts | string | ISO 8601 | Local time of the call on the rating machine (no time zone). |

Main pass only; test–retest passes are not included. Gzip is deterministic (mtime 0), so checksums are reproducible.

## `claims.jsonl` — every number reported in the paper

One JSON object per line: `id` (stable identifier, e.g. `titular.global.l2`), `valor` (number or string; percentages are
in percent 0–100, correlations and kappas in −1–1), `t` (time the analysis wrote it), `sintetico` (always `false`) and,
for some entries, `nota`. Values that were still pending in this version (marked `--` in the working file: human
validation, Sonnet wrapper sensitivity, ESCO robustness) are omitted rather than published empty; duplicated ids are kept
once. The LaTeX source of the paper reads its numbers only from these ids.

Key ids: `titular.global.l2` (world, % L2+), `titular.global.l3` (world, % L3), `titular.ingreso.{alto,medio_alto,medio_bajo,bajo}.l2`,
`h1.pendiente` (pp per log GDP), `h4.pico.minutos` (task length at which P(L3) peaks), `agree.kappa.sonnet_haiku`.

## `api/` — static JSON for tools and agents

See `api/README.md`.

## Third-party sources

Task statements and importance/frequency ratings: O\*NET 30.2 Database by the U.S. Department of Labor, Employment and
Training Administration (USDOL/ETA), used under the CC BY 4.0 license; `adi_tarea.texto` reproduces the statements
verbatim. Occupation titles: ESCO v1.2 (European Commission). Employment: ILOSTAT (ILO). Income groups and GDP per
capita: World Bank. Four-digit weights: BLS OES (May 2024) and DANE GEIH. Inputs other than O\*NET text are
redistributed only as derived aggregates.
