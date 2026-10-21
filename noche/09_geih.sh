#!/bin/zsh
# GEIH (DANE) ene-2024 → ago-2026. IDs de recurso sacados del catálogo NADA (819=2024, 853=2025, 900=2026) el 20-oct-2026.
# El enlace /catalog/<id>/download/<recurso> entrega el ZIP sin sesión. Reanudable.
cd "$(dirname "$0")/.." || exit 1
D=datos/microdatos/geih; mkdir -p $D
while IFS='|' read cat rec nombre; do
  f="$D/${cat}_${rec}_${nombre// /_}"
  [[ -s "$f" ]] && unzip -tq "$f" >/dev/null 2>&1 && { echo "ya está $f"; continue; }
  curl -L -C - --retry 8 --retry-all-errors --retry-delay 15 -A "Mozilla/5.0 (Macintosh)" -sS -o "$f" "https://microdatos.dane.gov.co/index.php/catalog/$cat/download/$rec" \
    && unzip -tq "$f" >/dev/null 2>&1 && echo "OK $f $(du -h "$f" | cut -f1)" || echo "FALLÓ $f"
  .venv/bin/python -I -c "import sys; sys.path.insert(0,'noche'); from comun import *; p=RAIZ/'$f'; registrar(p,'DANE GEIH','https://microdatos.dane.gov.co/index.php/catalog/$cat/download/$rec', ok=p.exists() and p.stat().st_size>1e6)"
  sleep 3
done <<'L'
819|23313|Ene_2024.zip
819|23362|Febrero_2024.zip
819|23596|Marzo 2024.zip
819|23496|Abril 2024.zip
819|23598|Mayo_2024 1.zip
819|23625|Junio_2024.zip
819|23631|Julio_2024.zip
819|23651|Agosto_2024.zip
819|23671|Septiembre_2024.zip
819|23677|Octubre_2024.zip
819|23729|Noviembre_ 2024.zip
819|23794|Diciembre_2024.zip
853|24263|Enero 2025.zip
853|24264|Febrero 2025.zip
853|24267|Marzo 2025.zip
853|24269|Abril 2025.zip
853|24268|Mayo 2025.zip
853|24266|Junio 2025.zip
853|24265|Julio 2025.zip
853|24307|Agosto 2025.zip
853|24324|Septiembre 2025.zip
853|24382|Octubre 2025.zip
853|24406|Noviembre 2025.zip
853|24463|Diciembre 2025.zip
900|24530|Enero 2026.zip
900|24594|Febrero 2026.zip
900|24674|Marzo 2026.zip
900|24703|Abril 2026.zip
900|24731|Mayo 2026.zip
900|24760|Junio 2026.zip
900|24791|Julio 2026.zip
900|24811|Agosto 2026.zip
L
echo "== GEIH terminada $(date)"
