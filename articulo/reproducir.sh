#!/bin/zsh
# Única vía al PDF (adaptado del paper del sismo): insumos → índice (claims congelados en salidas/corridas/<fecha-hora>/) →
# figuras → tablas → cifras → LaTeX → QA. Supone los crudos ya descargados (noche/noche.sh).
# Uso: zsh articulo/reproducir.sh                      # índice SINTÉTICO (prueba del pipeline, marca de agua)
#      zsh articulo/reproducir.sh --entrada scoring/salidas/main   # índice real
#      MODO="--entrada scoring/salidas/main" zsh articulo/reproducir.sh
# Un paso de insumos que falla no detiene los siguientes; el código de salida es el de LaTeX.
set -u -o pipefail
cd ${0:A:h:h}
PY=(.venv/bin/python -I); T=$(date +%F-%H%M); OUT=salidas/corridas/$T; mkdir -p $OUT
if (( $# )); then MODO="$*"; else MODO=${MODO:---sintetico}; fi
echo "== reproducir $T · modo $MODO"
[[ -f salidas/claims.jsonl ]] && mv salidas/claims.jsonl $OUT/claims_previos.jsonl
paso() { local n=$1; shift; local t0=$SECONDS
  if eval "$@" > $OUT/$n.log 2>&1; then echo "  ok    $n ($((SECONDS - t0)) s)"; else echo "  FALLO $n ($((SECONDS - t0)) s) → $OUT/$n.log"; fi; }
paso atlas        $PY analisis/atlas_insumos.py
paso esco         $PY analisis/esco_isco.py
paso comparadores $PY analisis/comparadores_isco.py
paso pnadc        $PY analisis/microdatos_pnadc.py
paso enoe         $PY analisis/microdatos_enoe.py
paso diseno       $PY analisis/claims_diseno.py
paso pesos_oes    $PY analisis/pesos_oes.py
paso indice       $PY analisis/indice.py $MODO
[[ -f salidas/claims.jsonl ]] || { echo "sin salidas/claims.jsonl: el índice falló, ver $OUT/indice.log"; exit 1; }
cp salidas/claims.jsonl $OUT/claims.jsonl
paso figuras      $PY analisis/figuras.py
paso tablas       $PY analisis/tablas.py
paso cifras       $PY articulo/generar_cifras.py
# -f: los errores de BibTeX (p. ej. comentarios % dentro de una entrada de referencias.bib) no detienen la compilación;
# el éxito se juzga por el PDF nuevo y la ausencia de errores fatales de LaTeX, y los errores de BibTeX se informan.
rm -f articulo/main.pdf
cd articulo && latexmk -pdf -f -interaction=nonstopmode main.tex > ../$OUT/latex.log 2>&1; cd ..
LX=0; [[ -f articulo/main.pdf ]] && ! grep -q "^! " articulo/main.log || LX=1
NB=$(grep -c "^I was expecting\|^Repeated entry\|error message" articulo/main.blg 2>/dev/null || true)
(( LX == 0 )) && echo "  ok    latex → articulo/main.pdf (BibTeX: ${NB:-0} avisos de error en main.blg)" || echo "  FALLO latex → $OUT/latex.log"
$PY qa/texto.py > $OUT/qa_texto.log 2>&1; tail -3 $OUT/qa_texto.log
[[ -f articulo/main.pdf ]] && cp articulo/main.pdf $OUT/main.pdf
echo "== corrida $T lista en $OUT ($SECONDS s)"
exit $LX
