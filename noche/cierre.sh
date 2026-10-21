#!/bin/zsh
# Espera a que terminen el panel agéntico y la sensibilidad de envoltorio; une particiones y regenera el paper con datos reales.
cd "${0:A:h:h}" || exit 1
P='validacion/agentico/panel'; E='scoring/envoltorio'
while pgrep -qf "$P.py" || pgrep -qf "$E.sh"; do sleep 120; done
cat validacion/agentico/salidas/panel.p?.jsonl validacion/agentico/salidas/panel.jsonl > validacion/agentico/salidas/panel_1500.jsonl 2>/dev/null
echo "== panel y envoltorio listos $(date)"
MODO="--entrada scoring/salidas/main" zsh articulo/reproducir.sh > logs/reproducir_cierre.out 2>&1; echo "reproducir rc=$?"
.venv/bin/python -I noche/informe2.py > logs/informe2_cierre.out 2>&1; echo "== cierre $(date)"
