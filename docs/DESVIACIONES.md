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
