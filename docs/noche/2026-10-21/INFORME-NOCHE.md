# Informe de captura nocturna — 2026-10-21

- Archivos capturados: **134** OK, **11** fallidos
- Volumen: **2.99 GB**

## Por fuente

| Fuente | archivos | GB | fallos |
|---|---|---|---|
| AHC occupation_task_matrix | 1 | 0.002 | 0 |
| AHC occupation_task_summary | 1 | 0.000 | 0 |
| AHC índice previo | 3 | 0.001 | 0 |
| Anthropic Economic Index (HF) | 1 | 0.000 | 0 |
| Banco Mundial API | 7 | 0.003 | 0 |
| DANE GEIH | 32 | 2.056 | 0 |
| DANE catálogo 782 | 1 | 0.000 | 1 |
| DANE catálogo 829 | 1 | 0.000 | 1 |
| ESCO API v1 | 3 | 0.048 | 0 |
| Eisfeldt et al. (copia AHC) | 1 | 0.000 | 0 |
| Eloundou | 1 | 0.000 | 1 |
| Eloundou (copia AHC) | 1 | 0.000 | 0 |
| Eloundou GPTs-are-GPTs | 1 | 0.004 | 0 |
| Felten AIOE (copia AHC) | 1 | 0.000 | 0 |
| GEIH (copia automatizacion_colombia) | 2 | 0.000 | 0 |
| IBGE PNADC | 8 | 0.426 | 6 |
| IBGE PNADC diccionario | 1 | 0.000 | 0 |
| ILO WP140 Gmyrek 2025 | 1 | 0.004 | 0 |
| ILO índice refinado 2025 | 1 | 0.000 | 1 |
| ILOSTAT SDMX DF_EAR_EMTM_SEX_OCU_NB | 1 | 0.013 | 0 |
| ILOSTAT SDMX DF_EMP_NIFL_SEX_OCU_NB | 1 | 0.011 | 0 |
| ILOSTAT SDMX DF_EMP_NIFL_SEX_OCU_RT | 1 | 0.011 | 0 |
| ILOSTAT SDMX DF_EMP_TEMP_SEX_OC2_NB | 1 | 0.030 | 0 |
| ILOSTAT SDMX DF_EMP_TEMP_SEX_OCU_NB | 1 | 0.015 | 0 |
| ILOSTAT SDMX DF_HOW_TEMP_SEX_OCU_NB | 1 | 0.016 | 0 |
| INEGI ENOE | 7 | 0.235 | 1 |
| INEI ENAHO | 4 | 0.044 | 0 |
| Natural Earth 110m | 1 | 0.000 | 0 |
| O*NET | 5 | 0.015 | 0 |
| O*NET 30.2 (copia AHC) | 1 | 0.013 | 0 |
| WB IT.NET.USER.ZS | 1 | 0.000 | 0 |
| WB NY.GDP.PCAP.PP.KD | 1 | 0.000 | 0 |
| WB SL.EMP.TOTL.SP.ZS | 1 | 0.000 | 0 |
| WB SL.TLF.TOTL.IN | 1 | 0.000 | 0 |
| WB SP.POP.TOTL | 1 | 0.000 | 0 |
| Webb 2020 (copia AHC) | 1 | 0.005 | 0 |
| arXiv 2608.20425 fuente | 1 | 0.003 | 0 |
| arXiv 2608.20425 pdf | 1 | 0.003 | 0 |
| arXiv Henseke GAISI | 1 | 0.001 | 0 |
| arXiv Jagged Global Economy | 1 | 0.001 | 0 |
| derivado: 01_onet.py | 1 | 0.000 | 0 |
| derivado: 03_esco.py | 1 | 0.001 | 0 |
| derivado: 05_worldbank.py | 1 | 0.000 | 0 |
| derivado: atlas_insumos.py | 3 | 0.000 | 0 |
| derivado: comparadores_isco.py | 2 | 0.000 | 0 |
| derivado: comparadores_isco.py (release_2026_06_26/aei_claude_ai_2026-06-26.csv) | 1 | 0.000 | 0 |
| derivado: construir_crosswalk.py | 2 | 0.003 | 0 |
| derivado: esco_banco.py | 2 | 0.001 | 0 |
| derivado: esco_isco.py | 2 | 0.002 | 0 |
| derivado: figuras.py | 6 | 0.000 | 0 |
| derivado: indice.py | 8 | 0.004 | 0 |
| derivado: microdatos_enoe.py | 3 | 0.007 | 0 |
| derivado: microdatos_geih.py | 2 | 0.010 | 0 |
| derivado: microdatos_pnadc.py | 2 | 0.002 | 0 |
| derivado: pesos_oes.py | 1 | 0.000 | 0 |
| derivado: robustez_esco.py | 1 | 0.000 | 0 |
| derivado: tablas.py | 3 | 0.000 | 0 |
| https://www.bls.gov/oes/special-requests/oesm24nat.zip | 1 | 0.000 | 0 |
| openai/gdpval (HF) | 1 | 0.000 | 0 |

## Fallos (acción humana)

- `/Users/cristianespinal/delegation-divide/datos/microdatos/geih/GEIH_2024_catalogo.html` ← https://microdatos.dane.gov.co/index.php/catalog/782/download/: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/microdatos/geih/GEIH_2025_catalogo.html` ← https://microdatos.dane.gov.co/index.php/catalog/829/download/: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/comparadores/eloundou/occupation_level_exposure.csv` ← https://raw.githubusercontent.com/openai/GPTs-are-GPTs/main/data/occupation_level_exposure.csv: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/comparadores/ilo_gmyrek/GenAI_exposure_index_2025.xlsx` ← https://www.ilo.org/sites/default/files/2025-05/GenAI_exposure_index_2025.xlsx: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/microdatos/enoe/enoe_2024_trim1_csv.zip` ← https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/enoe_2024_trim1_csv.zip: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/microdatos/pnadc/PNADC_012024.zip` ← https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_012024.zip: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/microdatos/pnadc/PNADC_022024.zip` ← https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_022024.zip: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/microdatos/pnadc/PNADC_032024.zip` ← https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_032024.zip: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/microdatos/pnadc/PNADC_042024.zip` ← https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_042024.zip: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/microdatos/pnadc/PNADC_012025.zip` ← https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2025/PNADC_012025.zip: FALLÓ
- `/Users/cristianespinal/delegation-divide/datos/microdatos/pnadc/PNADC_022025.zip` ← https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2025/PNADC_022025.zip: FALLÓ

## ILOSTAT

- Países con ISCO-08 a 1 dígito: **173** (≥2022: 132)
- Países con ISCO-08 a 2 dígitos: **0** (≥2022: 0)


## Tareas

- Tareas únicas O*NET con CIUO: **18796**
- Grupos unitarios ISCO-08 desde ESCO: **436** (esperados 436)

## Errores en 02_ilostat.log

- 00:39:08 ERROR salario_mes_moneda: sin datos
- 04:35:54 ERROR emp_sexo_edad: sin datos

## Errores en 04_comparadores.log

- 20:16:16 ERROR FALLÓ https://raw.githubusercontent.com/openai/GPTs-are-GPTs/main/data/occupation_level_exposure.csv
- 20:16:56 ERROR FALLÓ https://www.ilo.org/sites/default/files/2025-05/GenAI_exposure_index_2025.xlsx

## Errores en 06_microdatos.log

- 20:13:55 ERROR FALLÓ https://microdatos.dane.gov.co/index.php/catalog/782/download/
- 20:14:06 ERROR FALLÓ https://microdatos.dane.gov.co/index.php/catalog/829/download/
- 20:37:14 ERROR FALLÓ https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/enoe_2024_trim1_csv.zip
- 21:04:11 ERROR FALLÓ https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_012024.zip
- 21:04:43 ERROR FALLÓ https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_022024.zip
- 21:05:14 ERROR FALLÓ https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_032024.zip
- 21:05:48 ERROR FALLÓ https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_042024.zip
- 21:29:29 ERROR FALLÓ https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2025/PNADC_012025.zip
- 22:31:30 ERROR FALLÓ https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2025/PNADC_022025.zip

## Errores en 08_reintentos.log

- 13:02:04 ERROR sigue fallando https://microdatos.dane.gov.co/index.php/catalog/782/download/: código 0
- 13:02:04 ERROR sigue fallando https://microdatos.dane.gov.co/index.php/catalog/829/download/: código 0
- 13:02:05 ERROR sigue fallando https://raw.githubusercontent.com/openai/GPTs-are-GPTs/main/data/occupation_level_exposure.csv: código 0
- 13:02:05 ERROR sigue fallando https://www.ilo.org/sites/default/files/2025-05/GenAI_exposure_index_2025.xlsx: código 0
- 13:05:19 ERROR sigue fallando https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_012024.zip: código 0
- 13:05:19 ERROR sigue fallando https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_022024.zip: código 0
- 13:05:20 ERROR sigue fallando https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_032024.zip: código 0
- 13:05:21 ERROR sigue fallando https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2024/PNADC_042024.zip: código 0