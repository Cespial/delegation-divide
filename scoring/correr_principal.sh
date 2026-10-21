#!/bin/zsh
# Corrida principal (preregistro osf.io/9zntf): Sonnet y Haiku, una tarea por llamada, claude -p en modo neutro, 6 procesos.
# Reanudable: cada partición tiene su checkpoint. Al final une, corre test-retest (100) y el paper con datos reales.
cd "${0:A:h:h}" || exit 1
export MAX_LLAMADAS=1000000 ADI_CLI_MINIMO=1; PY=(.venv/bin/python -I); M=scoring/salidas/main; mkdir -p $M logs
for mod in sonnet haiku; do
  echo "== $mod inicio $(date)"
  for k in 0 1 2 3 4 5; do $PY scoring/puntuar.py --modelo $mod --particion $k/6 --pausa 0 > logs/main_${mod}_$k.out 2>&1 & done; wait
  cat $M/$mod.p?.jsonl > $M/$mod.jsonl; echo "== $mod fin $(date): $(wc -l < $M/$mod.jsonl) filas, $(grep -c '"error"' $M/$mod.jsonl) con error"
done
# test-retest: 100 tareas (semilla del piloto) calificadas dos veces por cada modelo, en carpeta aparte
for mod in sonnet haiku; do $PY scoring/puntuar.py --modelo $mod --piloto 100 --repetir 2 --salida retest --pausa 0 > logs/retest_$mod.out 2>&1 & done; wait
echo "== corrida terminada $(date)"
MODO="--entrada scoring/salidas/main" zsh articulo/reproducir.sh > logs/reproducir_real.out 2>&1; echo "reproducir rc=$?"
$PY noche/informe2.py > logs/informe2_real.out 2>&1
echo "== fin $(date)"
