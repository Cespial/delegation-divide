# adi-index

Python package and CLI for the **Agent Delegability Index (ADI)** — AI-agent delegability
for 433 ISCO-08 occupations and 146 countries (*The Delegation Divide*, Espinal Maya &
Jiménez Londoño, 2026). Data is bundled; no network access.

```bash
pip install adi-index
adi lookup 2631          # one ISCO-08 unit group → JSON with citation
adi search economist     # title substring
adi country COL          # atlas profile
adi top -n 10 --level l3 # highest full-delegation scores
adi cite [bibtex|apa|text]
adi version
```

```python
import adi
adi.lookup("2631")["adi_l3"]
adi.country("COL")["adi_share"]
adi.top(5, level="l2")
print(adi.cite("bibtex"))
```

Every record carries `citation` (BibTeX, key `espinal2026delegation`, with the preregistration
DOI 10.17605/OSF.IO/9ZNTF) and `version`. The bundled data is the real ADI v2026.1
(`sintetico=false`). Only if `ADI_DATA_DIR` points at CSVs with `sintetico=true` rows do responses
carry a `warning` field: **do not cite placeholder values**.

Columns: `adi_l2` share of tasks at level ≥ L2 (partial delegation), `adi_l3` share at L3 (full
delegation), `adi_share` percent of working time delegable, `barrera_*` share of tasks with each
barrier (physical, accountability, trust, access), `ic_lo`/`ic_hi` 95 % interval of `adi_share`.

Data: `sincronizar.sh` copies `salidas/adi_*.csv` from the repo root into `adi/data/`.
Override the data directory with `ADI_DATA_DIR=/path`.

Licence: code MIT, data CC-BY 4.0. Repo: https://github.com/Cespial/delegation-divide
