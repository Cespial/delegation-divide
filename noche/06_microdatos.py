"""Paso 6: microdatos de hogares para subgrupos (sexo, edad, informalidad): GEIH (CO), ENOE (MX), PNADC (BR), ENAHO (PE).
Mejor esfuerzo: cada fuente registra éxito o fallo en el manifiesto; no bloquea a las demás."""
import sys, subprocess; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
lg = log("06_microdatos"); d = DATOS / "microdatos"
# Colombia: primero lo que ya exista en el proyecto hermano automatizacion_colombia
AUTO = AHC.parent / "automatizacion_colombia"
hallados = list(AUTO.rglob("*.parquet")) + list(AUTO.rglob("*.csv")) if AUTO.exists() else []
geih = [p for p in hallados if "geih" in str(p).lower()][:40]
lg.info(f"automatizacion_colombia: {len(hallados)} tablas, {len(geih)} de GEIH")
for p in geih:
    copiar(p, d / "geih_automatizacion" / p.relative_to(AUTO), "GEIH (copia automatizacion_colombia)", lg)
# DANE GEIH 2024–2025 por el catálogo NADA (requiere descarga manual si pide sesión): se intenta el ZIP del mes
for cat, nombre in [(782, "GEIH_2024"), (829, "GEIH_2025")]:
    descargar(f"https://microdatos.dane.gov.co/index.php/catalog/{cat}/download/", d / f"geih/{nombre}_catalogo.html", f"DANE catálogo {cat}", lg, reintentos=1, minimo=50)
# México ENOE trimestral 2024T1–2025T2
for a in (2024, 2025):
    for t in (1, 2, 3, 4):
        if a == 2025 and t > 2: break
        descargar(f"https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/enoe_{a}_trim{t}_csv.zip", d / f"enoe/enoe_{a}_trim{t}_csv.zip", "INEGI ENOE", lg, reintentos=2)
# Brasil PNAD Contínua trimestral 2024–2025 + diccionario
for a in (2024, 2025):
    for t in (1, 2, 3, 4):
        if a == 2025 and t > 2: break
        descargar(f"https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/{a}/PNADC_0{t}{a}.zip", d / f"pnadc/PNADC_0{t}{a}.zip", "IBGE PNADC", lg, reintentos=2)
descargar("https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/Documentacao/Dicionario_e_input_20221031.zip", d / "pnadc/Dicionario_e_input.zip", "IBGE PNADC diccionario", lg, reintentos=2)
# Perú ENAHO 2024 (966) y 2023 (906): módulo 05 empleo e ingresos, módulo 02 características de los miembros
for cod, a in ((966, 2024), (906, 2023)):
    for mod in ("02", "05"):
        descargar(f"https://proyectos.inei.gob.pe/iinei/srienaho/descarga/CSV/{cod}-Modulo{mod}.zip", d / f"enaho/enaho_{a}_m{mod}.zip", "INEI ENAHO", lg, reintentos=2)
lg.info("microdatos: fin (ver manifiesto para fallos)")
