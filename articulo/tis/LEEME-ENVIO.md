# Envío a Technology in Society (Editorial Manager)

Construir todo con `zsh articulo/tis/empaquetar.sh` (desde la raíz del repo). Se sube **solo** lo de `tis/envio/limpio/`
más `tis/envio/manuscript.tex` (la fuente LaTeX no lleva metadatos que limpiar).

## Antes de entrar

- [ ] Biblioteca UNAL confirma cupo APC Elsevier (borrador: `docs/difusion/biblioteca-apc.md`).
- [ ] Página de título sin «[to confirm]»: direcciones postales, vínculo con INPLUX, biografía de Santiago.
- [ ] Santiago aprueba CRediT, bio, declaración de IA y los dos párrafos nuevos (Murugan et al.; implicaciones de política).
- [ ] Declaración de conflictos generada en la herramienta de Elsevier → `declaration_of_interests.docx`, pasada por limpiadoc.
- [ ] Volver a correr `empaquetar.sh` después de cualquier cambio.

## Archivos, en el orden en que los pide EM

| Tipo de ítem en EM | Archivo |
|---|---|
| Cover Letter | `limpio/cover_letter.docx` |
| Title Page (with Author Details) | `limpio/title_page.docx` (y `limpio/title_page.pdf` si pide PDF) |
| Highlights | `limpio/highlights.docx` |
| Manuscript (anonymized) | `manuscript.tex` (fuente) + `limpio/manuscript.pdf` (referencia) |
| Figure | `limpio/Figure_1.pdf` … `limpio/Figure_6.pdf` |
| Author Biography / Vitae | `limpio/vitae.docx` |
| Declaration of Interest Statement | `declaration_of_interests.docx` (herramienta de Elsevier) |

## Campos que se escriben a mano

- **Article type:** Full Length Article / Research Paper.
- **Title:** The Delegation Divide: An Open Index of AI-Agent Delegability across Occupations and Countries
- **Abstract:** copiar de la página 2 de `limpio/manuscript.pdf` (248 palabras).
- **Keywords (7):** AI agents; delegation; automation; occupations; ISCO-08; labour markets; developing countries
- **Authors:** Cristian Espinal Maya (corresponding, cespinal@unal.edu.co, Universidad Nacional de Colombia) · Santiago Jiménez Londoño (Universidad EAFIT). Mismo orden que la página de título.
- **Funding:** «This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.»
- **Data statement:** «Data and code are openly available on Zenodo (doi:10.5281/zenodo.23552918) under CC BY 4.0 (data) and MIT (code).» El DOI va en el formulario, no en el manuscrito anónimo.
- **Preprint en SSRN:** No (ya está en arXiv:2610.30752).
- **Suggested reviewers:** `revisores-sugeridos.md` (opcional).
- **Generative AI:** ya está como sección en el manuscrito; si EM pregunta, «Yes» y copiar ese texto.
