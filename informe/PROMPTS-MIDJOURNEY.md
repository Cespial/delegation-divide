# Ilustraciones de apertura — informe ADI v2026.1

Ocho aperturas (introducción + capítulos 1–7). Todas con el mismo sufijo de estilo; tras elegir la primera se fija como `--sref`
para las demás. Se generan monocromas y se tiñen a duotono teal al convertirlas (sin filtros CSS). Reglas: sin texto, sin letras,
sin logos, sin rostros reconocibles (Midjourney escribe mal y el informe no lleva personas identificables).
Originales en `informe/img-src/` (fuera de git); derivados duotono `informe/img/<id>.jpg` (1800 px).

Sufijo: `editorial engraving illustration, fine black ink linework and stippling on white paper, monochrome, calm and precise, generous negative space, no text, no letters, no logos, no faces --ar 9:5 --style raw`

| id | Tema | Prompt (antes del sufijo) | Elegida |
|---|---|---|---|
| introduccion | Humano y agente comparten el trabajo | a long work desk seen from above, a human hand and a mechanical arm passing sheets of paper between them, | 80b37180…/0_0 |
| cap1 | De la exposición a la delegación | a staircase of four steps built from stacked paper documents, a small distant figure carrying a folder up the steps, | 9a29e190…/0_0 |
| cap2 | Datos | an endless archive of wooden card-catalogue drawers, one drawer open with index cards, | c5df72d8…/0_3 |
| cap3 | Método | drafting instruments, rulers and calipers measuring small cards laid out on a grid, | c14e09dd…/0_2 |
| cap4 | El índice | many small work stations in isometric view, an office desk, a workshop bench, a field with a tractor, a counter, | 7e8356ba…/0_0 |
| cap5 | El atlas | a world map engraved in fine contour lines, some regions shaded with denser cross-hatching, | 3ef90d14…/0_2 (mapa uniforme: otra variante oscurecía África y contradecía los datos) |
| cap6 | Validación | a balance scale weighing two stacks of index cards, | 87906072…/0_3 |
| cap7 | Límites | a straight road across an open plain that ends at a low fence near the horizon, | 21383dd8…/0_1 |

Generadas el 22-oct-2026 en la cuenta de Midjourney de INPLUX (versión por defecto de la cuenta, `--style raw`). Descarga: `fetch` desde la pestaña de `/jobs/<id>` al receptor local `informe/receptor.py`, que imprime un token al arrancar; la pestaña lo manda en la cabecera `X-Token`.
