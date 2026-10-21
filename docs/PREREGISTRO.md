# Preregistro — The Delegation Divide (Agent Delegability Index, ADI)

Borrador para OSF. Autores: Cristian Espinal Maya (UNAL, ORCID 0009-0000-1009-8388) y Santiago Jiménez Londoño (EAFIT,
ORCID 0009-0007-9862-7133). Fecha del borrador: 2026-10-20. **Ninguna puntuación de modelos de la corrida principal
existe al registrar.** El piloto (≤ 300 tareas) sirve solo para ajustar la redacción de la rúbrica y se descarta.

## 1. Preguntas

- P1. ¿Qué fracción de las tareas del empleo mundial es delegable a agentes de IA (niveles L2 y L3) con la tecnología
  de octubre de 2026?
- P2. ¿Cómo varía esa fracción con el nivel de ingreso de los países?
- P3. ¿Concuerda la delegabilidad medida con la adopción observada (Anthropic Economic Index, Agentic Adoption Index)?

## 2. Hipótesis (direccionales)

- H1 (*delegation divide*). La fracción del empleo en tareas L3 es **menor** en países de ingreso bajo y medio-bajo que en
  los de ingreso alto, porque su empleo se concentra en ocupaciones con barrera física (ISCO 6, 7, 9).
- H2. Dentro de los países de ingreso medio, la brecha entre delegabilidad técnica y adopción observada es **mayor** que
  en los de ingreso alto.
- H3. ADI correlaciona positivamente con Eloundou et al. (β) y Felten et al. (AIOE), con r entre 0,4 y 0,8: suficiente
  para validez convergente, menor que 0,9 porque delegación ≠ exposición.
- H4. La proporción de tareas L3 crece con la duración humana de la tarea hasta un umbral y luego cae (forma de U
  invertida en `minutes_human`).

## 3. Datos

- Tareas: O*NET 30.2 Task Statements (18.796), ponderadas por importancia × frecuencia.
- Puente a ISCO-08: O*NET-SOC 2019 → 2010 (O*NET Center) → SOC 2010 → ISCO-08 (Hardy, Keister y Lewandowski, IBS).
  433 de 436 grupos unitarios; militares (0110, 0210, 0310) fuera; 7 residuales imputados del grupo de 3 dígitos.
- Banco secundario: skills esenciales de ESCO v1 por ocupación, para robustez.
- Empleo por país: ILOSTAT (SDMX), ISCO-08 a 2 dígitos donde exista y a 1 dígito como mínimo, año más reciente ≥ 2019.
- Ingreso: clasificación del Banco Mundial (FY2026) y PIB per cápita PPA.

## 4. Medición

- Rúbrica `scoring/prompts/rubrica_v1.md` (congelada; su SHA-256 va en la ficha de OSF).
- Modelos: Claude Sonnet 5.5 (principal), un modelo de OpenAI, uno de Google y uno de pesos abiertos; Claude Haiku 5.5
  para sensibilidad. Temperatura 0, una tarea por llamada, sin ejemplos de tareas reales en el prompt.
- Puntaje de tarea: nivel modal entre modelos; empate → el menor. `share_delegable` = mediana entre modelos.
- Ocupación: ADI_o = Σ peso_tarea × 1[nivel ≥ 2] (principal); variantes L3 y `share_delegable` ponderado.
- País: ADI_c = Σ_o empleo_c,o × ADI_o / Σ_o empleo_c,o, a la resolución disponible (2 díg. promedia los 4 díg.
  con pesos de empleo de EE. UU. dentro del grupo; se declara).

## 5. Validación humana

- Muestra de 1.500 tareas estratificada por gran grupo ISCO (proporcional al empleo mundial, mínimo 60 por grupo),
  semilla fija 20261020 (`validacion/muestra.py`).
- 3 evaluadores independientes, ciegos al modelo y entre sí, con la misma rúbrica.
- Métricas: κ ponderado cuadrático y α de Krippendorff (ordinal) entre humanos y entre humanos y modelo.
- Umbral de aceptación: α humano-modelo ≥ 0,60. Si no se alcanza, se publica igual y se reporta como limitación.

## 6. Análisis principal y robustez

- Número titular: fracción del empleo mundial (ponderado por ILOSTAT) en tareas L2+ y L3.
- H1: regresión de ADI_c sobre log PIB pc PPA y dummies de ingreso; IC por bootstrap de tareas (1.000).
- Robustez: por modelo; con skills ESCO en vez de tareas O*NET; con pesos de tarea uniformes; sin imputados.
- Placebo: tareas permutadas entre ocupaciones (1.000 permutaciones) para la distribución nula del ADI ocupacional.

## 7. Desviaciones

Toda desviación se registra con fecha en `docs/DESVIACIONES.md` y en el apéndice del paper.
