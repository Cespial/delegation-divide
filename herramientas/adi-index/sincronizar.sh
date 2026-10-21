#!/bin/sh
# Copia los CSV del índice desde salidas/ (raíz del repo) a adi/data/ para empaquetarlos.
# Uso: herramientas/adi-index/sincronizar.sh   (desde cualquier directorio)
set -eu
AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../.." && pwd)"
DEST="$AQUI/adi/data"
mkdir -p "$DEST"
n=0
for f in "$RAIZ"/salidas/adi_*.csv; do
  [ -f "$f" ] || continue
  cp "$f" "$DEST/"
  n=$((n+1))
  echo "copiado: $(basename "$f")"
done
if [ -f "$RAIZ/datos/esco/isco08_grupos_unitarios.csv" ]; then
  cp "$RAIZ/datos/esco/isco08_grupos_unitarios.csv" "$DEST/"
  echo "copiado: isco08_grupos_unitarios.csv (referencia ISCO-08)"
fi
[ "$n" -gt 0 ] || { echo "AVISO: no hay salidas/adi_*.csv en $RAIZ" >&2; exit 1; }
if grep -qi "true" "$DEST/adi_isco.csv" 2>/dev/null && head -1 "$DEST/adi_isco.csv" | grep -q "sintetico"; then
  if awk -F, 'NR>1 && tolower($NF)=="true"{f=1} END{exit !f}' "$DEST/adi_isco.csv"; then
    echo "AVISO: adi_isco.csv contiene filas sintetico=true (datos PLACEHOLDER)" >&2
  fi
fi
echo "sincronizado en $DEST"
