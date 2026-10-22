#!/bin/zsh
# Publicación de ADI v2026.1. Cada paso se corre a mano, en orden, desde la raíz del repo:
#   zsh release/publicar.sh <paso>     pasos: github | pages | release | pypi | hf | todo
# Requisitos: gh autenticado (Cespial); `pip install twine` + token PyPI; `pip install huggingface_hub` + `hf auth login`.
set -e; cd "${0:A:h:h}"
REPO=Cespial/delegation-divide; VER=v2026.1
paso=${1:-todo}
github() {
  git remote get-url origin >/dev/null 2>&1 || gh repo create $REPO --public --source=. --remote=origin \
    --description "The Delegation Divide: an open index of AI-agent delegability across occupations and countries (ADI)"
  git push -u origin main
  gh repo edit $REPO --add-topic ai-agents --add-topic labor-economics --add-topic isco-08 --add-topic onet --add-topic open-data --add-topic mcp
  echo "✔ https://github.com/$REPO"
}
pages() {
  # rama gh-pages con release/pages (API estática + llms.txt); Pages sirve en https://cespial.github.io/delegation-divide/
  tmp=$(mktemp -d); cp -R release/pages/. "$tmp"/
  git -C "$tmp" init -q -b gh-pages && git -C "$tmp" add -A && git -C "$tmp" -c user.name="Cristian Espinal Maya" -c user.email="cristian@inplux.co" commit -qm "ADI $VER static API"
  git -C "$tmp" push -f "https://github.com/$REPO.git" gh-pages
  gh api -X POST repos/$REPO/pages -f 'source[branch]=gh-pages' -f 'source[path]=/' >/dev/null 2>&1 || gh api -X PUT repos/$REPO/pages -f 'source[branch]=gh-pages' -f 'source[path]=/' >/dev/null
  echo "✔ en unos minutos: https://cespial.github.io/delegation-divide/adi/v2026.1/isco/2512.json"
}
release() {
  # ANTES: activar el repo en https://zenodo.org/account/settings/github/ (toggle ON) para que esta versión acuñe DOI.
  git tag -f $VER && git push origin $VER
  gh release create $VER --title "ADI $VER" --notes-file release/v2026.1/DATA_DICTIONARY.md \
    release/v2026.1/adi_isco.csv release/v2026.1/adi_pais.csv release/v2026.1/adi_tarea.csv \
    release/v2026.1/ratings_sonnet.jsonl.gz release/v2026.1/ratings_haiku.jsonl.gz release/v2026.1/claims.jsonl release/v2026.1/SHA256SUMS \
    release/arxiv/delegation-divide-arxiv.tar.gz
  echo "✔ release $VER · DOI de Zenodo en https://zenodo.org/account/settings/github/ (pegarlo en README, CITATION.cff, F_citar.tex)"
}
pypi() {
  for p in adi-index adi-mcp; do (cd herramientas/$p && ../../.venv/bin/python -m twine upload dist/*); done
  echo "✔ pip install adi-index · uvx adi-mcp"
}
hf() {
  hf upload cespial/adi release/v2026.1 . --repo-type dataset --commit-message "ADI $VER"
  hf upload cespial/adi release/hf/README.md README.md --repo-type dataset
  echo "✔ https://huggingface.co/datasets/cespial/adi"
}
case $paso in github|pages|release|pypi|hf) $paso;; todo) github; pages; release; pypi; hf;; *) echo "paso desconocido"; exit 1;; esac
