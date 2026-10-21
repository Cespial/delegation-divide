# Desviaciones del preregistro

## D1 — 2026-10-20 · Pesos de los grupos unitarios (4 díg.) dentro de cada grupo ISCO que reporta el país

**Preregistro (Indices):** «Within a reported group, unit-group ADIs are averaged with employment weights from countries in the
same World Bank income group that report finer detail (pooled), and with equal weights as a sensitivity check.»

**Qué pasó:** ningún país publica en ILOSTAT empleo por ISCO-08 a 4 dígitos para un año ≥ 2019 (`datos/atlas/paises.parquet`:
127 países a 2 díg., 23 a 1 díg., 0 a 3 o 4 díg.). No existen, por tanto, «países del mismo grupo de ingreso que reportan más
fino» en la fuente preregistrada.

**Qué hacemos (analisis/indice.py):** los 4 díg. dentro de cada grupo reportado se ponderan con el empleo de la GEIH de Colombia
(DANE, 2024-01 a 2026-08, CIUO-08 A.C. a 4 díg., `datos/microdatos/geih_ciuo_resumen.csv`; 426 de 433 grupos con empleo) para
**todos** los países. Para Colombia y el ingreso medio-alto coincide con el espíritu del preregistro (microdato de un país del
mismo grupo que reporta más fino); para ingreso alto, medio-bajo y bajo es un préstamo entre grupos de ingreso. Un grupo cuyas
unidades no tienen empleo GEIH recibe pesos iguales. La sensibilidad preregistrada con pesos iguales se reporta siempre
(`titular.global.l2.iguales`, `h1.pendiente.iguales`, columna 3 de la Tabla 4).

**Pendiente:** cuando PNADC (Brasil, COD ≈ ISCO-08 a 4 díg.) esté completa, agrupar GEIH + PNADC para el ingreso medio; para
ingreso alto, evaluar microdatos de un país de ingreso alto (p. ej. EU-LFS a 3 díg. o OES de EE. UU. vía el puente SOC→ISCO).
