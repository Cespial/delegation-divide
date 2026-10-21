#!/bin/zsh
# Captura nocturna ADI. Uso: nohup caffeinate -i noche/noche.sh > logs/noche.out 2>&1 &
# Idempotente: cada paso omite lo que ya existe. Pasos independientes corren en paralelo.
set -u
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python; mkdir -p logs
echo "== inicio $(date)"
$PY -I noche/05_worldbank.py                      # rápido; ILOSTAT usa su lista de países
$PY -I noche/01_onet.py &  P1=$!
$PY -I noche/02_ilostat.py & P2=$!
$PY -I noche/03_esco.py & P3=$!
$PY -I noche/04_comparadores.py & P4=$!
$PY -I noche/06_microdatos.py & P6=$!
wait $P1 $P2 $P3 $P4 $P6
echo "== pasos terminados $(date)"
$PY -I noche/07_informe.py
echo "== fin $(date)"
