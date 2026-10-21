#!/bin/zsh
# Espera a que termine noche.sh, corre la segunda pasada y rehace el informe.
cd "$(dirname "$0")/.." || exit 1
while pgrep -qf 'noche/noche.sh'; do sleep 120; done
.venv/bin/python -I noche/08_reintentos.py
.venv/bin/python -I validacion/muestra.py            # cuotas finales de ILOSTAT
.venv/bin/python -I noche/07_informe.py
echo "== segunda pasada terminada $(date)"
