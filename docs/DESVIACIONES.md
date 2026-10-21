# Desviaciones del preregistro

## D1 — 2026-10-20 · Pesos de los grupos unitarios (4 díg.) dentro de cada grupo ISCO que reporta el país

**Preregistro (Indices):** «Within a reported group, unit-group ADIs are averaged with employment weights from countries in the
same World Bank income group that report finer detail (pooled), and with equal weights as a sensitivity check.»

**Qué pasó:** ningún país publica en ILOSTAT empleo por ISCO-08 a 4 dígitos para un año ≥ 2019 (`datos/atlas/paises.parquet`:
127 países a 2 díg., 23 a 1 díg., 0 a 3 o 4 díg.). No existen, por tanto, «países del mismo grupo de ingreso que reportan más
fino» en la fuente preregistrada.

**Qué hacemos (analisis/indice.py; decidido con Cristian el 21-oct-2026, 07:00, antes de mirar resultados reales):** pesos a 4 díg.
por grupo de ingreso, lo más cercano a la regla registrada. **Ingreso alto:** empleo de EE. UU., BLS OES mayo 2024 (831 ocupaciones SOC
2018 → O*NET-SOC 2019 → SOC 2010 → ISCO-08 por `analisis/puente.py`; los SOC agregados de OES se reparten entre los O*NET-SOC de su
grupo de 5 díg.; 433/433 ISCO con empleo, 100 % del empleo llevado; `analisis/pesos_oes.py`). **Ingreso medio-alto, medio-bajo y
bajo:** GEIH de Colombia (DANE, 2024-01 a 2026-08, 426/433 ISCO con empleo). Para medio-bajo y bajo es un préstamo entre grupos de
ingreso, declarado. Un grupo sin empleo en la fuente recibe pesos iguales. **Sensibilidades:** pesos iguales (preregistrada:
`titular.global.l2.iguales`, `h1.pendiente.iguales`) y GEIH para todos (`titular.global.l2.geih`, `h1.pendiente.geih`).

**Pendiente:** cuando PNADC (Brasil, COD ≈ ISCO-08 a 4 díg.) esté completa, agrupar GEIH + PNADC para el ingreso medio; para
ingreso alto, evaluar microdatos de un país de ingreso alto (p. ej. EU-LFS a 3 díg. o OES de EE. UU. vía el puente SOC→ISCO).

## D2 — 2026-10-21 (10:45, antes de abrir cualquier resultado real) · Validación: de 1.500 × 3 humanos a 300 × 1 humano ciego + panel agéntico

**Preregistro (Data collection, Sample size):** tres evaluadores humanos califican a ciegas las mismas 1.500 tareas.

**Qué cambia y por qué:** decisión de los autores por plazo y costo. (1) **Humano ciego:** Santiago Jiménez Londoño (coautor) califica
a ciegas una submuestra de 300 tareas de la muestra de 1.500, estratificada por gran grupo ISCO (mínimo 20 por grupo, semilla
20261025, `validacion/santiago/muestra_300.csv`), con la guía y las 20 tareas de práctica, sin ver calificaciones de modelos ni del
panel. Su α de Krippendorff y κ cuadrático con el consenso de modelos son la cifra humana del paper. Que el evaluador sea coautor se
declara como limitación. (2) **Panel agéntico, reportado como validación NO humana:** Claude Opus 5.5 vía `claude -p` con búsqueda web
(máx. 4 búsquedas por tarea), que no participa como evaluador del índice, investiga y califica las 1.500 tareas con la misma rúbrica y
cita hasta 3 evidencias (`validacion/agentico/panel.py`). Se reporta su acuerdo con los modelos y con Santiago. (3) Los 1.500 × 3
humanos preregistrados quedan como trabajo para la v2 si un árbitro lo pide.

**Actualización 2026-10-21 (cómo se hizo de verdad la calificación humana):** la calificación a ciegas de las 300 tareas
(`validacion/respuestas/hoja_Santiago_LISTA.xlsx`, 300/300 llenas) la lideró Santiago Jiménez Londoño con la ayuda de estudiantes
evaluadores. No se registró qué tarea calificó cada persona, así que la hoja se analiza como UNA sola calificación humana y no se
reporta acuerdo humano–humano (α ni κ entre humanos). No se nombran los estudiantes ni se dice cuántos fueron. Ningún evaluador vio
calificaciones de modelos, del panel ni resultados del paper. El texto del artículo (secciones 1, 2, 4, 7, 8, 9 y resumen) describe la
validación como «calificación humana ciega liderada por un coautor con estudiantes evaluadores», y mantiene como limitación que el
líder es coautor y que, sin registro de contribuciones individuales, no hay α humano–humano.

## D3 — 2026-10-21 (11:05, DESPUÉS de ver los primeros resultados reales) · Exclusión por calidad del dato de empleo

**Qué pasó:** en la primera corrida real Surinam aparecía como el país más delegable (ADI L2 = 0,82). La causa es la fuente: ILOSTAT
trae para Surinam 2022 todo el empleo en el gran grupo 1 (Directores y gerentes). Revisando la cobertura de todos los países
aparecieron otros tres casos donde las ocupaciones reportadas no suman el empleo total.

**Regla añadida (no preregistrada):** se excluye el país-año si sus grupos ocupacionales cubren menos del 75 % del empleo total de
ILOSTAT del mismo año, o si tiene empleo en menos de 6 de los 9 grandes grupos civiles. Excluidos: Surinam 2022 (1 gran grupo),
Senegal 2025 (34 % del empleo), Comoras 2021 (66 %) y Hong Kong 2025 (74,8 %, 6 grandes grupos). El atlas pasa de 150 a 146 países.
Lista en `datos/atlas/EXCLUIDOS_D3.csv`. Como la regla se fijó después de ver resultados, el paper reporta también el titular y H1
con los 150 países originales (sensibilidad).

Sensibilidad con los 150 países originales (corrida 2026-10-21-1103): titular L2 35,20 % · H1 pendiente 7,30 (IC 6,61–7,89).
Con 146 países (corrida 2026-10-21-1104): titular L2 35,17 % · H1 pendiente 7,23 (IC 6,52–7,83). La exclusión no cambia ninguna conclusión.
