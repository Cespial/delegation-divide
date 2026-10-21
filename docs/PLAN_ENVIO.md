# Plan de cierre y envío — The Delegation Divide (ADI v2026.1)

Estado al 21-oct-2026 17:40. Paper completo con cifras reales (corrida 2026-10-21-1539), QA 0 errores, tarball arXiv compila.
Lo que queda son acciones externas con cuenta de Cristian y la lectura de Santiago. Orden recomendado; cada paso dice quién lo hace.

## 0. Hoy (21-oct)
| # | Acción | Quién | Cómo |
|---|---|---|---|
| 0.1 | Enviar a Santiago el PDF + `ADI_OSF_aprobacion_Santiago.md` (Desktop) y pedirle comentarios sobre §7, §8 y conclusión | Cristian | correo/WhatsApp |
| 0.2 | Cerrar las 8 referencias [VERIFY] del .bib y las 2 celdas «?» de la Tabla 1 | Claude (en curso) | `qa/verificar_bib.py` |
| 0.3 | Comprobar endoso en arXiv para econ.GN (si nunca enviaste ahí, pedirlo hoy) | Cristian | arxiv.org/user → *Start new submission* muestra si pide endorsement |

## 1. Cuando Santiago apruebe el embargo en OSF (o a las 48 h, noche del 22-oct)
| # | Acción | Quién | Cómo |
|---|---|---|---|
| 1.1 | Verificar que https://doi.org/10.17605/OSF.IO/9ZNTF resuelve | Claude | curl |
| 1.2 | **Terminar el embargo** para que el preregistro sea público al enviar (osf.io/9zntf → *End embargo early*; requiere aprobación de ambos admins) | Cristian + Santiago | OSF web |

## 2. Publicar los enlaces que el paper cita (todo preparado en `release/`)
Correr en orden desde la raíz del repo, con `! zsh release/publicar.sh <paso>`:
| # | Paso | Qué hace | Requisito |
|---|---|---|---|
| 2.1 | `github` | crea el repo público Cespial/delegation-divide y sube `main` | gh autenticado (ya) |
| 2.2 | `pages` | rama gh-pages con la API JSON (`release/pages/`) y activa GitHub Pages → cespial.github.io/delegation-divide/adi/v2026.1/… | 2.1 |
| 2.3 | activar el repo en Zenodo: https://zenodo.org/account/settings/github/ → toggle ON | Cristian (web) | 2.1 |
| 2.4 | `release` | tag + GitHub Release v2026.1 con datos y tarball → Zenodo acuña el DOI | 2.3 |
| 2.5 | pegar el DOI de Zenodo en README.md, CITATION.cff, `.zenodo.json` no (lo lee Zenodo), `articulo/secciones/F_citar.tex`, `herramientas/adi-index/adi/__init__.py` (cite) y `release/v2026.1/api` (regenerar con `release/construir_release.py`) | Claude | commit + push + release v2026.1.1 si cambia el paquete |
| 2.6 | `pypi` | sube `adi-index` y `adi-mcp` 2026.1 (dists ya construidos en `herramientas/*/dist/`) | `pip install twine` + token PyPI de Cristian |
| 2.7 | `hf` | sube el dataset a huggingface.co/datasets/cespial/adi | `hf auth login` de Cristian; confirmar que el usuario HF es `cespial` |
| 2.8 | registrar `adi-mcp` en el MCP Registry (registry.modelcontextprotocol.io) | Cristian | tras 2.6 |

## 3. Con los comentarios de Santiago
| # | Acción | Quién |
|---|---|---|
| 3.1 | Incorporar comentarios; regenerar: `MODO="--entrada scoring/salidas/main" zsh articulo/reproducir.sh` y `release/arxiv/empaquetar.sh` | Claude |
| 3.2 | Santiago aprueba la versión final por escrito (correo) | Santiago |

## 4. arXiv
| # | Acción | Quién |
|---|---|---|
| 4.1 | arxiv.org/submit: subir `release/arxiv/delegation-divide-arxiv.tar.gz`; campos de `release/arxiv/METADATOS.md` (título, abstract, econ.GN + cs.CY, cs.AI, comentarios con DOI de OSF y Zenodo, licencia CC BY 4.0); añadir a Santiago como autor | Cristian |
| 4.2 | Al salir el ID: ponerlo en README, CITATION.cff, `.zenodo.json` (related_identifiers), llms.txt, OSF (campo «article DOI» del registro) y HF card; commit + push | Claude |
| 4.3 | Anuncio: LinkedIn/X con el titular (35,2 % / 2,5 %), el atlas y `pip install adi-index` | Cristian |

## Fuera de la v1 (v2, 2027)
3 evaluadores humanos externos × 1.500 tareas (diseño registrado); PNADC/ENOE como pesos alternativos; gradientes por sexo/edad/informalidad; versión 2027.1 del índice.
