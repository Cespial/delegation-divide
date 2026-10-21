#!/bin/zsh
# Sensibilidad preregistrada al envoltorio: las 1.500 tareas de validación con el prompt de sistema por defecto de Claude Code.
cd "${0:A:h:h}" || exit 1
export MAX_LLAMADAS=1000000 ADI_CLI_MINIMO=0; PY=(.venv/bin/python -I); S=scoring/salidas/envoltorio_cc
for mod in haiku sonnet; do
  for k in 0 1 2 3 4 5; do $PY scoring/puntuar.py --modelo $mod --tareas validacion/muestra_1500.csv --particion $k/6 --salida envoltorio_cc --pausa 0 > logs/envoltorio_${mod}_$k.out 2>&1 & done; wait
  cat $S/$mod.p?.jsonl > $S/$mod.jsonl; echo "== $mod $(date): $(wc -l < $S/$mod.jsonl) filas"
done
