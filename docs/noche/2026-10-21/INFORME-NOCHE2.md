# Informe de la segunda noche — 2026-10-21

Generado 2026-10-21T10:39 por `noche/informe2.py`.

## 1. Pasos

| Paso | Estado | Detalle |
|---|---|---|
| 01_onet | OK | 20:13:55 INFO tareas únicas 18796, pares 1261844, ocupaciones CIUO 440 |
| 02_ilostat | con errores (2) |  |
| 02b_ilostat_oc2 | OK | 21:34:38 INFO 2 dígitos: 144 países; ≥2019: 134; ≥2022: 118 |
| 03_esco | OK | 10:38:09 INFO skills 10500/12549 |
| 04_comparadores | con errores (2) | 20:38:18 INFO comparadores listos |
| 05_worldbank | OK | 20:13:39 INFO Banco Mundial listo |
| 06_microdatos | con errores (9) | 22:33:19 INFO microdatos: fin (ver manifiesto para fallos) |
| 13_geih | con errores (32) | 22:28:53 INFO panel 916,886 filas; CIUO 4 díg. con datos: 451; empleo mensual medio 23.7 M; informalidad 56.6  |
| esco_isco | OK | 10:38:50 INFO ESCO: 2909 ocupaciones → 424 ISCO-08; pares ocupación-skill 112,550; skills únicos 12,549; esenc |
| comparadores_isco | OK | 10:38:52 INFO AEI por país: release_2026_06_26/aei_claude_ai_2026-06-26.csv → 121 países con usage_per_capita_ |
| 14_pnadc | OK | 10:38:53 WARNING PNADC: sin ZIP completo en /Users/cristianespinal/delegation-divide/datos/microdatos/pnadc (p |
| 15_enoe | OK | 10:39:07 INFO ENOE: p3 mapeado a ISCO 1 díg. 98.5% de ocupados |
| 20_indice | OK | 10:39:13 INFO titular L2 35.2 % · H1 pendiente 7.30 (p=0.000) · 219 claims · 4 s |
| 21_figuras | OK | 10:39:15 INFO fig6_barreras.pdf |
| 22_tablas | OK | 10:39:15 INFO tab4_h1.tex |

## 2. Coberturas

- Índice: **REAL**
- Países en el atlas: **150** (2 díg. 127, 1 díg. 23); empleo cubierto **2,341.1 M**
- ISCO-08 4 díg. con tareas: **433** de 436 (7 imputados); con empleo GEIH (pesos dentro de grupo): **426**
- Tareas puntuadas con consenso: 18,796 de 18,796
- GEIH: 451 códigos CIUO-08 A.C. con empleo; empleo mensual medio 23.7 M
- ENOE (México, ISCO 1 díg. por tabla manual SINCO): 9 grupos, empleo 60.9 M
- PNADC (Brasil, COD 4 díg.): no disponible
- `INFO Eloundou tareas: 19,265 en el archivo; emparejadas 18,739 de 18,796`
- `INFO AEI task_penetration: 17,964 textos; emparejadas por texto normalizado 18,684 de 18,796`
- `INFO cobertura ISCO-08 (de 433): eloundou_beta 433; eloundou_gpt4_beta 433; aei_penetracion 433; eloundou_occ_dv_beta 426; eloundou_occ_human_beta 426; felten_aioe 429; webb_pct_ai 426; webb_pct_software 426; webb_pct_robot 426; eisfeldt_genaiexp 433; aei_exposicion_obs 427`
- `INFO AEI por país: release_2026_06_26/aei_claude_ai_2026-06-26.csv → 121 países con usage_per_capita_index (media de 2 meses)`
- `INFO ESCO: 2909 ocupaciones → 424 ISCO-08; pares ocupación-skill 112,550; skills únicos 12,549; esenciales 53%; con título ES 100%`
- H3 correlaciones (ISCO 4 díg.): Eloundou r=0.93, Felten r=0.89 · H2 países con uso AEI: 102

## 3. Piloto

| Archivo | filas | válidas | llamadas (registro) | % JSON válido | duración media (s) |
|---|---|---|---|---|---|
| haiku | 300 | 300 | 19378 | 1.5 % | 7.9 |
| sonnet | 300 | 300 | 19708 | 1.5 % | 4.4 |
| sonnet_r2 | 100 | 100 | 19708 | 0.5 % | 4.4 |

% JSON válido = filas válidas / llamadas registradas con etiqueta `adi` para ese modelo (incluye reintentos y pasadas de retest).

- Test-retest sonnet: 100 tareas comunes · exacto 89.0 % · ±1 100.0 % · κ cuadrático 0.84
- Acuerdo sonnet–haiku: 300 tareas comunes · exacto 67.0 % · ±1 98.0 % · κ cuadrático 0.60
- Distribución de niveles (sonnet): L0 4%, L1 32%, L2 61%, L3 3%

## 4. QA del PDF

- `articulo/main.pdf`: 27 páginas; marca de agua sintética: no
- palabras PDF ≈ 11,831 · citas 63 · entradas bib 63 · índice real
- errores por origen: ninguno
- QA texto: OK

<details><summary>Errores de qa/texto.py</summary>

```
```
</details>

## 5. Pendientes

- [ ] PNADC: los ZIP siguen incompletos (.parcial); reintentar descarga y correr analisis/microdatos_pnadc.py.
- [ ] Validación humana: faltan validacion/respuestas/*.xlsx (α y κ humanos salen como «--»).
- [ ] Robustez ESCO (robustez.esco.h1.pendiente): requiere puntuar el banco de skills ESCO.
- [ ] Validar la decisión de pesos 4 díg. GEIH para todos los países (docs/DESVIACIONES.md).
- [ ] Corregir en articulo/referencias.bib los comentarios % dentro de entradas (BibTeX los reporta como errores) y citar o quitar entradas sin citar.
- [ ] Revisar los números a mano que qa/texto.py marca en las secciones del agente de redacción.
