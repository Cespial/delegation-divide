#!/bin/zsh
# Piloto (preregistro §Pilot): 300 tareas, semilla 20261020, se descarta. Mide JSON válido, ritmo, límites y test-retest (100 × 2).
cd "$(dirname "$0")/.." || exit 1
export NOCHE_DIR=scoring/salidas/piloto MAX_LLAMADAS=800; mkdir -p $NOCHE_DIR
PY=.venv/bin/python
$PY -I scoring/puntuar.py --modelo sonnet --piloto 300 --pausa 0
$PY -I scoring/puntuar.py --modelo haiku  --piloto 300 --pausa 0
$PY -I scoring/puntuar.py --modelo sonnet --piloto 300 --repetir 2 --n 100 --pausa 0
echo "== piloto terminado $(date)"
