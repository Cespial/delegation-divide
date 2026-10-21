# The Delegation Divide — estructura del paper para arXiv

## Contexto

Espinal Maya y Jiménez Londoño comparten una línea de medición con LLM en economía laboral (AHC, 2604.01066 y 2604.02403), microdatos GEIH y ética de la IA. Tras dos rondas (20-oct-2026) se eligió la opción **B**: un índice abierto de delegabilidad a agentes de IA por ocupación ISCO-08, con atlas de 190 países. Hueco verificado: la OIT (Gmyrek 2025) mide GenAI en ISCO-08; el Agentic Adoption Index (2608.20425) mide adopción en O*NET; nadie tiene delegación a agentes en la clasificación que usan todos los países. Objetivo explícito: **máximo de citas**, de autores y de agentes (Claude Code y similares que leen repos y papers).

Principio de diseño: cada pieza es una **unidad citable** por separado: un nombre, un número, una definición, una tabla comparativa, un dataset con DOI, una herramienta.

## 1. Las siete unidades citables

| # | Unidad | Por qué la citan |
|---|---|---|
| 1 | **Nombre e acrónimo**: *Agent Delegability Index (ADI)* | Un índice sin nombre no se cita. «ADI» no colisiona con AEI (Anthropic) ni AIOE (Felten). |
| 2 | **El número**: «el X % de las tareas del empleo mundial es delegable a agentes; Y % en ingreso medio vs Z % en ingreso alto» | Frey-Osborne vive de un número. Va en la primera frase del abstract. |
| 3 | **La definición de 3 capas**: aumentación / delegación parcial / delegación completa, cada una en una frase citable | Da vocabulario. Quien use «delegación completa» cita la fuente. |
| 4 | **Tabla 1 comparativa**: ADI vs Eloundou, Felten, ILO-Gmyrek, Agentic Adoption Index, Anthropic Economic Index (qué mide, unidad, cobertura, año, licencia) | Las tablas comparativas se citan como «ver Tabla 1 en…». |
| 5 | **Dataset con DOI**: ISCO-08 4 dígitos × 3 capas × modelo, ESCO ocupación, atlas país | Cada uso = cita. Zenodo + Hugging Face + GitHub, versionado `v2026.1`. |
| 6 | **Herramienta para agentes**: paquete `pip install adi-index`, JSON estático, **servidor MCP** (`adi_lookup(isco | esco | título)`) | Un agente que use la herramienta la cita en su salida. Es el ángulo que nadie tiene. |
| 7 | **La «delegation divide»**: hallazgo nombrado (países de ingreso medio: más delegable, menos adopción) | Los hallazgos con nombre se repiten en prensa y reviews. |

## 2. Título y abstract

Título: **The Delegation Divide: An Open Index of AI-Agent Delegability for 436 Occupations and 190 Countries**
Corto (header): *The Delegation Divide*.

Abstract (fórmula, ≤ 250 palabras, en este orden):
1. Número titular (frase 1).
2. Qué falta en la literatura (una frase: exposición ≠ delegación; O*NET ≠ mundo).
3. Qué es ADI (3 capas, ESCO→ISCO-08, 4 modelos, validación humana con κ).
4. Tres hallazgos numerados.
5. «We release the index, the country atlas, the prompts, and an MCP server at <URL>.»

## 3. Estructura del paper (25–30 pp. + apéndices)

1. **Introduction** (2 pp.): el número, la brecha, 5 contribuciones en viñetas (cada una = unidad citable).
2. **From exposure to delegation** (2 pp.): definiciones de las 3 capas; Figura 1 «escalera de delegación»; **Tabla 1** comparativa.
3. **Data** (2 pp.): ESCO v1.2 (3.000 ocupaciones, tareas en 28 idiomas, mapa a ISCO-08), ILOSTAT empleo por ISCO (190 países), microdatos para subgrupos (GEIH Colombia, ENOE México, PNAD Brasil, ENAHO Perú). Tabla 2: cobertura.
4. **Method** (4 pp.): rúbrica por tarea (texto completo en apéndice), 4 modelos (Claude 5.5 Sonnet, GPT, Gemini, un modelo abierto), agregación tarea→ocupación→país, validación humana (1.500 tareas × 3 evaluadores, κ, α de Krippendorff), convergencia con índices previos (r), análisis de sensibilidad. Figura 2: flujo.
5. **The index** (4 pp.): Tabla 3 top-20 / bottom-20 ocupaciones; distribución por grupo ISCO 1 dígito; Figura 3 escalera por ocupación.
6. **The atlas** (4 pp.): Figura 4 mapa mundial; Figura 5 dispersión ingreso per cápita vs delegabilidad (la «divide»); por sexo, edad e informalidad donde hay microdato.
7. **Validation against observed adoption** (3 pp.): ADI vs Anthropic Economic Index y Agentic Adoption Index (EE. UU.); ADI vs dinámica salarial GEIH 2023–2026. Aquí va la sección dinámica de la opción C como subsección (2023→2026, sin proyección como titular).
8. **Limitations and ethics** (2 pp.): delegabilidad técnica ≠ despliegue; sesgo de modelos; marco de deshumanización (Santiago).
9. **Conclusion** (1 p.): repite el número y el enlace.

Apéndices: A rúbrica y prompts completos; B crosswalk ESCO↔ISCO↔O*NET; C tablas completas por país; D protocolo de validación humana; E card del dataset; F **BibTeX y cómo citar** (página final, también en README).

## 4. Diseño para que los agentes lo citen

- `README.md` del repo con 10 líneas que resumen el paper, el número y el BibTeX **arriba del todo**.
- `llms.txt` y `llms-full.txt` en el repo y en el sitio del dataset.
- `CITATION.cff` + `codemeta.json`.
- `claims.jsonl`: cada cifra del paper con id, valor, intervalo y script que la produce (patrón ya usado en el paper del sismo).
- JSON estático por ocupación en GitHub Pages: `/adi/v2026.1/isco/2512.json`.
- Servidor MCP (`adi-mcp`) con tres herramientas: `lookup_occupation`, `country_profile`, `cite`. La respuesta de `cite` devuelve el BibTeX. Publicado en el registro de MCP y en PyPI.
- Figuras **CC-BY** en SVG y PNG en el repo: reuso de figura = cita.
- Cross-list: econ.GN (primario), cs.CY, cs.AI. Enviar lunes antes de las 14:00 ET.

## 5. Reglas de redacción

- Cada constructo se define una sola vez en una frase autocontenida y citable.
- El número titular aparece en título o abstract, intro, conclusión y README.
- «We release…» explícito en abstract e intro.
- Sin siglas sin definir; sin frases vacías; verbos en presente.
- Inglés; versión de lectura en español después (columna de Santiago).

## 6. Plan de ejecución (8 semanas)

| Sem. | Entrega |
|---|---|
| 1 | Preregistro OSF (rúbrica, modelos, hipótesis de la divide). Descarga ESCO, ILOSTAT, crosswalks. Repo público desde el día 1. |
| 2 | Rúbrica piloto en 300 tareas, 4 modelos; ajuste; costo real. |
| 3 | Scoring completo (~14.000 tareas ESCO × 4 modelos). Validación humana lanzada (3 evaluadores, EAFIT/UNAL). |
| 4 | Agregación, índice v0, Tabla 3, convergencia con índices previos. |
| 5 | Atlas: ILOSTAT × ADI; microdatos CO/MX/BR/PE; Figuras 4–5. |
| 6 | Validación contra adopción (AEI, AAI, GEIH). Sección dinámica. |
| 7 | Texto completo; 3 árbitros simulados; QA de cifras (`claims.jsonl`), referencias en Crossref. Paquete MCP + pip + llms.txt. |
| 8 | Zenodo DOI, HF dataset, arXiv. Lanzamiento coordinado (ver §7). |

Reusar: pipeline y scoring de `augmented_human_capital`; `reproducir.sh`, `qa/verificar_bib.py`, `generar_cifras.py`, `cartografia.py` del paper del sismo; crosswalk SOC→ISCO→CIUO de `automatizacion_colombia`.

## 7. Lanzamiento (misma semana)

arXiv + Zenodo + HF + GitHub release + MCP en registro + hilo en X/LinkedIn (Cristian) + columna en La República (Santiago) + Medium en inglés + correo a autores de ILO-Gmyrek, Agentic Adoption Index, Eloundou, Felten, y a BID/BM que publican sobre IA y empleo en LatAm + alphaXiv + Papers with Code. Enviar después a *Nature Human Behaviour* o *PNAS Nexus*; plan B *JEBO*.

## 8. Verificación

- Preregistro antes de la primera llamada al modelo.
- Cada cifra del texto sale de `claims.jsonl` por macro; `reproducir.sh` reconstruye el PDF de cero.
- κ ≥ 0,6 entre humanos; r con Eloundou y Felten reportado aunque sea bajo.
- Placebo: ocupaciones con tareas permutadas.
- Las 3 herramientas MCP responden en una prueba fría desde un Claude Code nuevo y devuelven el BibTeX.
- Referencias 100 % verificadas en Crossref.
