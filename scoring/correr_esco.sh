#!/bin/zsh
# Robustez ESCO (exploratoria preregistrada, OSF 344-83): skills/competencias esenciales ESCO puntuadas SOLO con Sonnet, misma rúbrica,
# claude -p en modo neutro (ADI_CLI_MINIMO=1), una tarea por llamada, 6 particiones. Reanudable (checkpoint por partición).
# Al terminar une las particiones en scoring/salidas/esco/sonnet.jsonl y corre analisis/robustez_esco.py.
# Lanzar: nohup caffeinate -is zsh scoring/correr_esco.sh > logs/esco.out 2>&1 &
# Solo unir/analizar (p. ej. tras reanudar a mano): zsh scoring/correr_esco.sh --unir
cd "${0:A:h:h}" || exit 1
export MAX_LLAMADAS=1000000 ADI_CLI_MINIMO=1; PY=(.venv/bin/python -I); S=scoring/salidas/esco; mkdir -p $S logs
if [[ ${1:-} != --unir ]]; then
  echo "== esco sonnet inicio $(date): $($PY -c 'import pandas as pd; print(len(pd.read_parquet("datos/esco_banco.parquet")))') skills"
  for k in 0 1 2 3 4 5; do $PY scoring/puntuar.py --modelo sonnet --banco esco --particion $k/6 --pausa 0 > logs/esco_sonnet_$k.out 2>&1 & done; wait
fi
cat $S/sonnet.p?.jsonl > $S/sonnet.jsonl
echo "== esco sonnet fin $(date): $(wc -l < $S/sonnet.jsonl) filas, $(grep -c '"error"' $S/sonnet.jsonl) con error"
$PY analisis/robustez_esco.py && tail -8 salidas_robustez/claims_esco.jsonl
echo "== fin $(date)"
