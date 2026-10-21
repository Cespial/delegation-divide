#!/bin/zsh
# Reparte lo que falta de Haiku en 12 procesos (no repite tareas ya hechas en haiku.p?.jsonl) y luego sigue la cola de correr_principal.
cd "${0:A:h:h}" || exit 1
export MAX_LLAMADAS=1000000 ADI_CLI_MINIMO=1 ADI_HECHOS='haiku.p?.jsonl' ADI_SUFIJO=q; PY=(.venv/bin/python -I); M=scoring/salidas/main
for k in {0..11}; do $PY scoring/puntuar.py --modelo haiku --particion $k/12 --pausa 0 > logs/main_haiku_q$k.out 2>&1 & done; wait
cat $M/haiku.p?.jsonl $M/haiku.q*.jsonl > $M/haiku.jsonl; echo "== haiku fin $(date): $(wc -l < $M/haiku.jsonl) filas, $(grep -c '"error"' $M/haiku.jsonl) con error"
wait_retest=0; while pgrep -qf "salida retest"; do sleep 20; done
echo "== corrida terminada $(date)"
MODO="--entrada scoring/salidas/main" zsh articulo/reproducir.sh > logs/reproducir_real.out 2>&1; echo "reproducir rc=$?"
$PY noche/informe2.py > logs/informe2_real.out 2>&1
echo "== fin $(date)"
