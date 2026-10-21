#!/bin/zsh
# Segunda noche: espera a que terminen noche/noche.sh, noche/despues.sh y noche/03_esco.py; luego GEIH, reproducir.sh e informe.
# Uso (lo lanza el orquestador): nohup caffeinate -i zsh noche/noche2.sh > logs/noche2.out 2>&1 &
# MODO="--entrada scoring/salidas/main" para el índice real (por defecto sintético). Un paso que falla no detiene los siguientes.
set -u
SCRIPT=${0:A}; cd "${SCRIPT:h:h}" || exit 1
[[ -z "${NOCHE2_CAFE:-}" ]] && command -v caffeinate >/dev/null && NOCHE2_CAFE=1 exec caffeinate -i zsh "$SCRIPT" "$@"
PY=(.venv/bin/python -I); mkdir -p logs
echo "== noche2 inicio $(date)"
while pgrep -qf 'noche/noche.sh' || pgrep -qf 'noche/despues.sh' || pgrep -qf 'noche/03_esco.py' || pgrep -qf 'scoring/piloto.sh'; do
  echo "   esperando ($(date +%H:%M)): $(pgrep -lf 'noche/(noche|despues).sh|noche/03_esco.py' | awk '{print $NF}' | tr '\n' ' ')"; sleep 120
done
echo "== insumos listos $(date)"
paso() { local n=$1; shift; local t0=$SECONDS
  echo "-- $n $(date +%H:%M:%S)"; "$@" > logs/$n.log 2>&1; local rc=$?
  echo "   $n rc=$rc ($((SECONDS - t0)) s)"; echo "$n rc=$rc segundos=$((SECONDS - t0)) fin=$(date +%FT%T)" >> logs/noche2_pasos.txt; }
: > logs/noche2_pasos.txt
paso 13_geih_noche2 $PY analisis/microdatos_geih.py
paso reproducir     zsh articulo/reproducir.sh ${=MODO:---sintetico}
paso informe2       $PY noche/informe2.py
echo "== noche2 fin $(date)"
