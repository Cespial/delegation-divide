#!/bin/zsh
# Única vía al informe PDF: claims → cifras.json → figuras SVG → tablas HTML → informe.html → PDF → verificación.
# Uso: zsh informe/construir.sh      (supone salidas/claims.jsonl ya generado por articulo/reproducir.sh)
# Python del repo para datos; Python del sistema (con playwright y pypdf) para el render.
set -e -o pipefail
cd ${0:A:h:h}
PY=(.venv/bin/python -I); PYR=${PYR:-/opt/homebrew/bin/python3}
$PY informe/cifras.py
$PY analisis/figuras.py --estilo informe fig3 fig4 fig5 fig6
$PY analisis/tablas.py --html
$PY informe/ensamblar.py
$PYR informe/render.py
$PY informe/verificar.py
echo "== informe listo: informe/out/delegation-divide-report-2026.pdf"
