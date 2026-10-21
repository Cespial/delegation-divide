#!/bin/sh
# NO SUBE NADA. Imprime los comandos que correría Cristian para publicar el dataset en Hugging Face.
# Publicar es una acción externa: requiere su aprobación y su sesión (`huggingface-cli login`).
# Uso: sh release/hf/subir.sh   → imprime los comandos; revisarlos y pegarlos a mano.
set -eu
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
REPO="cespial/adi"   # usuario u organización de HF: confirmar antes de subir
VER="v2026.1"
cat <<CMD
# 1) Integridad del paquete local
(cd "$RAIZ/release/$VER" && shasum -a 256 -c SHA256SUMS)
# 2) Datos de la versión (upload crea el repo de dataset si no existe)
huggingface-cli upload $REPO "$RAIZ/release/$VER" . --repo-type dataset --commit-message "ADI $VER"
# 3) Dataset card (YAML con configs adi_isco / adi_pais / adi_tarea)
huggingface-cli upload $REPO "$RAIZ/release/hf/README.md" README.md --repo-type dataset --commit-message "Dataset card $VER"
# 4) Etiqueta de versión
huggingface-cli tag $REPO $VER --repo-type dataset
CMD
