# Informe de la segunda noche — 2026-10-21

Generado 2026-10-20T22:51 por `noche/informe2.py`.

## 1. Pasos

| Paso | Estado | Detalle |
|---|---|---|
| 01_onet | OK | 20:13:55 INFO tareas únicas 18796, pares 1261844, ocupaciones CIUO 440 |
| 02_ilostat | OK | 22:51:50 WARNING salario_mes_moneda LTU intento 2: 422 Client Error: Unprocessable Entity for url: https://sdm |
| 02b_ilostat_oc2 | OK | 21:34:38 INFO 2 dígitos: 144 países; ≥2019: 134; ≥2022: 118 |
| 03_esco | OK | 22:47:07 INFO ocupaciones 1800, skills por bajar 11642 |
| 04_comparadores | con errores (2) | 20:38:18 INFO comparadores listos |
| 05_worldbank | OK | 20:13:39 INFO Banco Mundial listo |
| 06_microdatos | con errores (9) | 22:33:19 INFO microdatos: fin (ver manifiesto para fallos) |
| 13_geih | con errores (32) | 22:28:53 INFO panel 916,886 filas; CIUO 4 díg. con datos: 451; empleo mensual medio 23.7 M; informalidad 56.6  |
| esco_isco | OK | 22:51:21 INFO ESCO: 1850 ocupaciones → 424 ISCO-08; pares ocupación-skill 72,361; skills únicos 11,674; esenci |
| comparadores_isco | OK | 22:51:23 INFO AEI por país: release_2026_06_26/aei_claude_ai_2026-06-26.csv → 121 países con usage_per_capita_ |
| 14_pnadc | OK | 22:51:23 WARNING PNADC: sin ZIP completo en /Users/cristianespinal/delegation-divide/datos/microdatos/pnadc (p |
| 15_enoe | OK | 22:51:39 INFO ENOE: p3 mapeado a ISCO 1 díg. 98.5% de ocupados |
| 20_indice | OK | 22:51:44 INFO sincronizar.sh: copiado: adi_isco.csv / copiado: adi_pais.csv / copiado: adi_tarea.csv / copiado |
| 21_figuras | OK | 22:51:46 INFO fig6_barreras.pdf |
| 22_tablas | OK | 22:51:47 INFO tab4_h1.tex |

## 2. Coberturas

- Índice: **SINTÉTICO (prueba del pipeline; no son resultados)**
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
- `INFO ESCO: 1850 ocupaciones → 424 ISCO-08; pares ocupación-skill 72,361; skills únicos 11,674; esenciales 49%; con título ES 100%`
- H3 correlaciones (ISCO 4 díg.): Eloundou r=0.65, Felten r=0.72 · H2 países con uso AEI: 102

## 3. Piloto

| Archivo | filas | válidas | llamadas (registro) | % JSON válido | duración media (s) |
|---|---|---|---|---|---|
| sonnet | 257 | 257 | 257 | 100.0 % | 6.4 |

% JSON válido = filas válidas / llamadas registradas con etiqueta `adi` para ese modelo (incluye reintentos y pasadas de retest).

- Test-retest sonnet: falta sonnet.jsonl o sonnet_r2.jsonl
- Acuerdo sonnet–haiku: falta haiku.jsonl
- Distribución de niveles (sonnet): L0 4%, L1 30%, L2 63%, L3 3%

## 4. QA del PDF

- `articulo/main.pdf`: 24 páginas; marca de agua sintética: sí
- palabras PDF ≈ 10,575 · citas 35 · entradas bib 62 · índice SINTÉTICO (marca de agua)
- errores por origen: 01_intro.tex 1, 02_delegacion.tex 7, 03_datos.tex 10, 04_metodo.tex 1, 08_limites.tex 2, B_crosswalk.tex 43, F_citar.tex 3, entrada de referencias.bib sin citar 27
- QA texto: 94 errores

<details><summary>Errores de qa/texto.py</summary>

```
ERROR 01_intro.tex: número a mano «403» … 'tasks to ISCO-08 unit groups that keeps 403 distinct task sets'
ERROR 02_delegacion.tex: número a mano «50» … 'the task with equal quality by at least 50\\%.\n link ten AI app'
ERROR 02_delegacion.tex: número a mano «52» … '.\n link ten AI application areas to the 52 O*NET abilities and'
ERROR 02_delegacion.tex: número a mano «702» … 'bility of computerisation & Occupation (702) & 70 hand-labelled'
ERROR 02_delegacion.tex: número a mano «70» … 'of computerisation & Occupation (702) & 70 hand-labelled occup'
ERROR 02_delegacion.tex: número a mano «52» … 'ional exposure via abilities & Ability (52) & Expert links, AI'
ERROR 02_delegacion.tex: número a mano «50» … 'ores & O*NET-SOC & US & Y & N \\\\\n     & 50\\% time reduction wi'
ERROR 02_delegacion.tex: número a mano «888,000» … 'skills & Task & Embedding similarity to 888,000 agent skill files &'
ERROR 03_datos.tex: número a mano «923» … 'ase contains 18,796 task statements for 923 O*NET-SOC  occupati'
ERROR 03_datos.tex: número a mano «403» … 'covers 433 of the 436 unit groups with 403 distinct task sets;'
ERROR 03_datos.tex: número a mano «0110,» … 't task sets; the three military groups (0110, 0210, 0310) have no'
ERROR 03_datos.tex: número a mano «0210,» … 'sets; the three military groups (0110, 0210, 0310) have no O*NET'
ERROR 03_datos.tex: número a mano «0310» … 'the three military groups (0110, 0210, 0310) have no O*NET task'
ERROR 03_datos.tex: número a mano «440» … 'C to ISCO at one digit and so collapsed 440 Colombian occupatio'
ERROR 03_datos.tex: número a mano «1.2» … 'cupations classification (ESCO, version 1.2) attaches to each o'
ERROR 03_datos.tex: número a mano «28» … 'out a crosswalk, and it is available in 28 languages.\nIts unit'
ERROR 03_datos.tex: número a mano «173» … 'rough its SDMX interface.\nAt one digit, 173 countries report em'
ERROR 03_datos.tex: número a mano «144» … 'ountries form the atlas.\nAt two digits, 144 countries report su'
ERROR 04_metodo.tex: número a mano «100» … '{ADIs}_o =  _{t} w_{ot}\\,  { {share}_t}{100}.\n  \n {equation}\nTh'
ERROR 08_limites.tex: número a mano «193» … 'sharpest in agriculture.\nO*NET has only 193 task statements tha'
ERROR 08_limites.tex: número a mano «193» … 'orkers in low-income countries, and all 193 fall in the human-v'
ERROR B_crosswalk.tex: número a mano «923» … 'Task Statements} (18,796 statements for 923 O*NET-SOC  occupati'
ERROR B_crosswalk.tex: número a mano «1,110» … 'crosswalk, O*NET Resource Center (CSV; 1,110 codes of  to 1,012'
ERROR B_crosswalk.tex: número a mano «1,012» … 'esource Center (CSV; 1,110 codes of  to 1,012 codes of ).\n    SOC'
ERROR B_crosswalk.tex: número a mano «1,131» … 'e for Structural Research (IBS), file : 1,131 rows linking 839 si'
ERROR B_crosswalk.tex: número a mano «839» … 'search (IBS), file : 1,131 rows linking 839 six-digit SOC  code'
ERROR B_crosswalk.tex: número a mano «97» … 'code that descends from several  codes (97 cases) divides its'
ERROR B_crosswalk.tex: número a mano «19» … '*NET-SOC  are not in the IBS crosswalk: 19-1020 (biological sc'
ERROR B_crosswalk.tex: número a mano «29» … 'road group used as a detailed code) and 29- (surgical technolo'
ERROR B_crosswalk.tex: número a mano «19» … 'des of the same minor group. It assigns 19-1020 to 19-1029, wh'
ERROR B_crosswalk.tex: número a mano «19» … 'same minor group. It assigns 19-1020 to 19-1029, which the IBS'
ERROR B_crosswalk.tex: número a mano «2131» … '9-1029, which the IBS file maps to ISCO 2131 (biologists, botani'
ERROR B_crosswalk.tex: número a mano «29» … 'logists and related professionals), and 29- to 29-, mapped to'
ERROR B_crosswalk.tex: número a mano «29» … 'and related professionals), and 29- to 29-, mapped to ISCO 32'
ERROR B_crosswalk.tex: número a mano «3259» … 'ionals), and 29- to 29-, mapped to ISCO 3259 (health associate p'
ERROR B_crosswalk.tex: número a mano «15» … 'onomy and have no row in the crosswalk: 15-1299.04 (penetratio'
ERROR B_crosswalk.tex: número a mano «15» … 'walk: 15-1299.04 (penetration testers), 15-1299.05 (informatio'
ERROR B_crosswalk.tex: número a mano «15» … '99.05 (information security engineers), 15-1299.06 (digital fo'
ERROR B_crosswalk.tex: número a mano «15» … '299.06 (digital forensics analysts) and 15-1299.07 (blockchain'
ERROR B_crosswalk.tex: número a mano «15» … 'ers). They are assigned by hand to SOC  15-1199 (computer occu'
ERROR B_crosswalk.tex: número a mano «2519» … 'other), which the IBS file maps to ISCO 2519 (software and appli'
ERROR B_crosswalk.tex: número a mano «2529» … 'analysts not elsewhere classified) and 2529 (database and netwo'
ERROR B_crosswalk.tex: número a mano «683» … 'it groups with weight . In the IBS file 683 codes map to one gr'
ERROR B_crosswalk.tex: número a mano «102» … 'he IBS file 683 codes map to one group, 102 to two, 30 to three'
ERROR B_crosswalk.tex: número a mano «30» … '683 codes map to one group, 102 to two, 30 to three and 24 to'
ERROR B_crosswalk.tex: número a mano «24» … 'one group, 102 to two, 30 to three and 24 to four or more (ma'
ERROR B_crosswalk.tex: número a mano «17» … 'o three and 24 to four or more (maximum 17). The mapping weigh'
ERROR B_crosswalk.tex: número a mano «30,549» … 'one pair per ISCO group. The result is 30,549 pairs covering 18,7'
ERROR B_crosswalk.tex: número a mano «48» … 's and 433 unit groups, with a median of 48 tasks per group (mi'
ERROR B_crosswalk.tex: número a mano «860» … '48 tasks per group (minimum 5, maximum 860), and 403 distinct'
ERROR B_crosswalk.tex: número a mano «403» … 'per group (minimum 5, maximum 860), and 403 distinct task sets,'
ERROR B_crosswalk.tex: número a mano «0110» … 'litary.} The three armed-forces groups, 0110 (commissioned armed'
ERROR B_crosswalk.tex: número a mano «0210» … '0 (commissioned armed forces officers), 0210 (non-commissioned a'
ERROR B_crosswalk.tex: número a mano «0310» … 'commissioned armed forces officers) and 0310 (armed forces occup'
ERROR B_crosswalk.tex: número a mano «3413» … 'ISCO-08 & Unit group \\\\\n     \n    3413 & Religious associa'
ERROR B_crosswalk.tex: número a mano «3511» … 'eligious associate professionals \\\\\n    3511 & Information and c'
ERROR B_crosswalk.tex: número a mano «4213» … 'echnology operations technicians \\\\\n    4213 & Pawnbrokers and m'
ERROR B_crosswalk.tex: número a mano «7133» … '& Pawnbrokers and money-lenders \\\\\n    7133 & Building structur'
ERROR B_crosswalk.tex: número a mano «8155» … '33 & Building structure cleaners \\\\\n    8155 & Fur and leather p'
ERROR B_crosswalk.tex: número a mano «8159» … 'ther preparing machine operators \\\\\n    8159 & Textile, fur and'
ERROR B_crosswalk.tex: número a mano «9613» … 'erators not elsewhere classified \\\\\n    9613 & Sweepers and rela'
ERROR B_crosswalk.tex: número a mano «440» … 'and distributed tasks downward, so that 440 four-digit occupati'
ERROR B_crosswalk.tex: número a mano «77» … 'sk sets and the median task belonged to 77 occupations.\nThat m'
ERROR B_crosswalk.tex: número a mano «403» … 'm a statistician.\nThe chain above keeps 403 distinct task sets'
ERROR F_citar.tex: número a mano «3166» … 'intervals and version.\n    takes an ISO 3166-1 alpha-3 code and'
ERROR F_citar.tex: número a mano «4.0» … 'bric under Creative Commons Attribution 4.0 (CC BY 4.0).\nO*NET,'
ERROR F_citar.tex: número a mano «4.0» … 'Creative Commons Attribution 4.0 (CC BY 4.0).\nO*NET, ESCO, ILOS'
ERROR entrada de referencias.bib sin citar: albanesi2023new
ERROR entrada de referencias.bib sin citar: anthropic2024mcp
ERROR entrada de referencias.bib sin citar: arntz2016risk
ERROR entrada de referencias.bib sin citar: autor2003skill
ERROR entrada de referencias.bib sin citar: autor2015why
ERROR entrada de referencias.bib sin citar: autor2024applying
ERROR entrada de referencias.bib sin citar: bick2024rapid
ERROR entrada de referencias.bib sin citar: brynjolfsson2018what
ERROR entrada de referencias.bib sin citar: brynjolfsson2023generative
ERROR entrada de referencias.bib sin citar: brynjolfsson2025canaries
ERROR entrada de referencias.bib sin citar: cazzaniga2024gen
ERROR entrada de referencias.bib sin citar: chen2023large
ERROR entrada de referencias.bib sin citar: chiang2024chatbot
ERROR entrada de referencias.bib sin citar: danaher2019automation
ERROR entrada de referencias.bib sin citar: dellacqua2023navigating
ERROR entrada de referencias.bib sin citar: dingel2020how
ERROR entrada de referencias.bib sin citar: gmyrek2023generative
ERROR entrada de referencias.bib sin citar: gmyrek2024buffer
ERROR entrada de referencias.bib sin citar: gottlieb2021working
ERROR entrada de referencias.bib sin citar: humlum2025large
ERROR entrada de referencias.bib sin citar: kapoor2024agents
ERROR entrada de referencias.bib sin citar: nedelkoska2018automation
ERROR entrada de referencias.bib sin citar: noy2023experimental
ERROR entrada de referencias.bib sin citar: patwardhan2025gdpval
ERROR entrada de referencias.bib sin citar: pew2026silicon
ERROR entrada de referencias.bib sin citar: pizzinelli2023labor
ERROR entrada de referencias.bib sin citar: tomlinson2025working
```
</details>

## 5. Pendientes

- [ ] El índice es SINTÉTICO: falta la corrida principal (requiere docs/OSF_DOI.txt) y `MODO="--entrada scoring/salidas/main"` en reproducir.sh.
- [ ] PNADC: los ZIP siguen incompletos (.parcial); reintentar descarga y correr analisis/microdatos_pnadc.py.
- [ ] ESCO skills.jsonl no existe aún: esco_isco.py usa los títulos enlazados desde ocupaciones.
- [ ] Validación humana: faltan validacion/respuestas/*.xlsx (α y κ humanos salen como «--»).
- [ ] Robustez ESCO (robustez.esco.h1.pendiente): requiere puntuar el banco de skills ESCO.
- [ ] Validar la decisión de pesos 4 díg. GEIH para todos los países (docs/DESVIACIONES.md).
- [ ] Corregir en articulo/referencias.bib los comentarios % dentro de entradas (BibTeX los reporta como errores) y citar o quitar entradas sin citar.
- [ ] Revisar los números a mano que qa/texto.py marca en las secciones del agente de redacción.
