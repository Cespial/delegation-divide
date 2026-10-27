#!/bin/zsh
# Builds the Editorial Manager package for Technology in Society in tis/envio/:
#   manuscript.tex (single file, anonymized, figures as Figure_N, bibliography inlined) + Figure_N.pdf,
#   title page (.tex/.pdf/.docx), highlights.docx, vitae.docx, cover_letter.docx, and cleaned copies in envio/limpio/.
# Run from anywhere: zsh articulo/tis/empaquetar.sh
set -euo pipefail
TIS=${0:A:h}
cd $TIS
export TEXINPUTS=..:

# 1. Both variants (also refreshes manuscript-anon.bbl for the inlined bibliography)
latexmk -pdf -silent -jobname=manuscript-anon main.tex >/dev/null
latexmk -pdf -silent -jobname=manuscript-full -usepretex='\def\modocompleto{1}' main.tex >/dev/null
latexmk -pdf -silent titlepage.tex >/dev/null

# 2. Flattened anonymized source
rm -rf envio && mkdir -p envio
latexpand --expand-bbl manuscript-anon.bbl --empty-comments main.tex > envio/manuscript.tex
python3 - envio/manuscript.tex <<'EOF'
import re, sys
p = sys.argv[1]; s = open(p).read()
# the flattened file is the review copy: anonymized mode is fixed, no build switch
s = s.replace(r"\ifdefined\modocompleto\anonimofalse\else\anonimotrue\fi", r"\anonimotrue")
s = s.replace(r"\graphicspath{{../}}", "")
# latexpand leaves \InputIfFileExists alone: inline cifras.tex (every result number) in its place
i = s.index(r"\InputIfFileExists{cifras.tex}"); j = s.index("\n", s.index(r"\newcommand{\pval}", i))
s = s[:i] + "%% cifras.tex (generated from salidas/claims.jsonl)\n" + open("../cifras.tex").read() + s[j:]
orden = {"fig1_escalera": 1, "fig2_flujo": 2, "fig3_isco": 3, "fig6_barreras": 4, "fig4_mapa": 5, "fig5_ingreso": 6}
s, n = re.subn(r"\{fig/(fig\d_[a-z]+)\}", lambda m: "{Figure_%d}" % orden[m.group(1)], s)
assert n == 6, n
# the full-version branches still hold identifying text; drop the lines that carry it
s = "\n".join(l for l in s.split("\n") if not re.search(r"Cespial|osf\.io|zenodo|Espinal|Jim\\'enez|balamlabs", l))
open(p, "w").write(s)
EOF
for n in 1 2 3 4 5 6; do cp figuras/Figure_$n.pdf envio/; done

# 3. The flattened file must build on its own
tmp=$(mktemp -d)
cp envio/manuscript.tex envio/Figure_*.pdf $tmp/
(cd $tmp && TEXINPUTS= latexmk -pdf -silent manuscript.tex >/dev/null)
cp $tmp/manuscript.pdf envio/manuscript.pdf
rm -rf $tmp
paginas() { pdfinfo $1 | awk '/^Pages/{print $2}' }
[[ $(paginas envio/manuscript.pdf) == $(paginas manuscript-anon.pdf) ]] || { echo "pages differ"; exit 1 }
ids=$(pdftotext envio/manuscript.pdf - | grep -c "Cespial\|balamlabs\|zenodo\|osf.io\|Espinal\|Jim.nez\|Santiago" || true)
[[ $ids == 0 ]] || { echo "identifiers left: $ids"; exit 1 }

# 4. Title page and editable side files
cp titlepage.tex titlepage.pdf envio/
mv envio/titlepage.tex envio/title_page.tex; mv envio/titlepage.pdf envio/title_page.pdf
pandoc titlepage.tex -o envio/title_page.docx
sed -n 's/^\\item //p' highlights.tex | sed 's/\\%/%/g; s/^/- /' | pandoc -f markdown -o envio/highlights.docx --metadata title=Highlights
awk '/section\*\{Author biographies\}/{f=1;next} /end\{document\}/{f=0} f' titlepage.tex > envio/.vitae.tex
pandoc -f latex envio/.vitae.tex -o envio/vitae.docx --metadata title=Vitae && rm envio/.vitae.tex
sed '1,2d' cover-letter.md | pandoc -f markdown -o envio/cover_letter.docx

# 5. Highlights and abstract limits
awk '{ if (length($0) > 85) { print "highlight too long: " $0; bad=1 } } END { exit bad }' <(sed -n 's/^\\item //p' highlights.tex | sed 's/\\%/%/g')
palabras=$(pdftotext -f 1 -l 2 envio/manuscript.pdf - | awk '/^Abstract/{f=1;next} /^Keywords/{f=0} f' | wc -w | tr -d ' ')
(( palabras <= 250 )) || { echo "abstract: $palabras words"; exit 1 }

# 6. Clean every deliverable
for f in envio/*.pdf envio/*.docx; do limpiadoc $f --perfil personal --autor "" --salida envio/limpio >/dev/null; done
echo "OK · $(paginas envio/manuscript.pdf) pages · abstract $palabras words · $(ls envio/limpio | wc -l | tr -d ' ') clean files in tis/envio/limpio"
