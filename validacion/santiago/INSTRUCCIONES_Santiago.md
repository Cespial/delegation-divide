# Validación humana ciega del ADI — Instrucciones para Santiago

**Paper:** *The Delegation Divide: An Open Index of AI-Agent Delegability across Occupations and Countries* · preregistro osf.io/9zntf
**Tu archivo:** `hoja_Santiago.xlsx` · **Entrega:** `hoja_Santiago_LISTA.xlsx` a Cristian · **Tiempo:** ≈ 5–6 h (puedes partirlo en sesiones)

## Qué es y por qué importa

Dos modelos de lenguaje calificaron las 18.796 tareas de O*NET con una rúbrica de cuatro niveles. Tú eres **el evaluador humano
del estudio**: calificas a ciegas 300 de esas tareas y tu juicio es la cifra con la que medimos si los modelos aciertan. Por eso lo
único que importa es que la calificación sea **tuya** y **a ciegas**.

## Qué tienes que hacer

1. Lee este documento completo (≈ 15 min). La rúbrica íntegra también está en la pestaña **rubrica** del Excel.
2. Califica las **20 tareas de práctica** (pestaña `1_practica_20`). No cuentan; sirven para calibrarte.
3. Califica las **300 tareas** de la pestaña `2_tareas_300`, en el orden en que vienen. Llena todas las columnas de cada fila.
4. Guarda como **`hoja_Santiago_LISTA.xlsx`** y envíaselo a Cristian.

## Reglas (no negociables)

- **No uses ninguna IA** (ChatGPT, Claude, Gemini, Copilot…) para calificar, consultar ni redactar. Si usas un modelo, la comparación
  humano–modelo pierde sentido. Diccionarios y descripciones ocupacionales públicas sí se pueden consultar.
- **No mires nada del estudio hasta entregar:** ni el repositorio, ni el PDF, ni los resultados, ni preguntes a Cristian cómo
  calificaron los modelos o cuál es el número titular.
- No compartas el archivo ni las tareas fuera del estudio.
- Si la rúbrica no te queda clara en algún caso, escribe la duda a Cristian; la aclaración queda registrada.

## La pregunta

Para cada tarea respondes una sola cosa: **¿cuánto de esta tarea podría ejecutar hoy un agente de IA?** Califica lo **técnicamente
posible**, no lo que las empresas hacen ni lo que la ley permite (la barrera legal se marca aparte).

**Tecnología de referencia (fija):** agentes de IA disponibles al público en octubre de 2026: modelos de frontera con uso de
herramientas, ejecución de código, navegación web, uso del computador (operar escritorio o navegador) y manejo de archivos, capaces de
trabajar solos varias horas en un encargo de varios pasos. **No tienen cuerpo ni robótica.** Actúan solo mediante software,
documentos, mensajes y sistemas digitales a los que el trabajador normalmente tendría acceso.

## La rúbrica

| Nivel / Level | Definición / Definition |
|---|---|
| **L0 · Sin papel significativo · No meaningful role** | ES: El agente no puede ejecutar ni acelerar de forma material ninguna parte sustancial de la tarea. · EN: The agent cannot perform or materially speed up any substantial part of the task. |
| **L1 · Aumentación · Augmentation** | ES: Una persona hace la tarea; la IA ayuda paso a paso (borradores, búsquedas, sugerencias). La persona sigue en el circuito en cada paso y produce el resultado. · EN: A human performs the task; the AI assists step by step (drafts, searches, suggestions). The human stays in the loop at each step and produces the output. |
| **L2 · Delegación parcial · Partial delegation** | ES: Un agente puede ejecutar de punta a punta subpasos sustanciales de la tarea a partir de un objetivo. Una persona todavía debe hacer al menos un paso esencial, o revisar y corregir el trabajo antes de usarlo. · EN: An agent can execute substantial sub-steps of the task end to end from a goal specification. A human still has to perform at least one essential step or review and correct the work before use. |
| **L3 · Delegación completa · Full delegation** | ES: Un agente puede completar toda la tarea de punta a punta, con la calidad que aceptaría un trabajador competente, dados solo el objetivo y el acceso. El papel de la persona se limita a asignarla y aceptar el resultado. · EN: An agent can complete the whole task end to end, to the quality a competent worker would accept, given only the goal and access. The human's role is limited to assigning it and accepting the result. |

**L2 vs. L3:** si le pasaras la tarea a un agente con el mismo acceso que el trabajador y te fueras a almorzar, ¿al volver estaría
hecha y lista para usarse (L3), o tendrías que hacer algo antes de usarla (L2)?
**L1 vs. L2:** ¿el agente ejecuta un tramo completo sin que intervengas en cada paso (L2), o solo propone y tú ejecutas (L1)?

**Dos aclaraciones.** (a) Una barrera legal no baja por sí sola el nivel: califica la factibilidad técnica y marca la barrera; pero
si la ley exige que la persona *ejecute* un paso esencial, el máximo es L2. (b) Si la tarea mezcla partes físicas y digitales,
califícala como un todo y usa `share_delegable` para el porcentaje de tiempo que el agente podría asumir.

## Ejemplos resueltos (inventados; ninguno está en tu hoja)

### Ejemplos resueltos · Worked examples

Las tareas de ejemplo son inventadas; ninguna está en su hoja. / The example tasks are invented; none is in your sheet.

**L0**
1. *Masajista: «Aplicar presión con las manos sobre los músculos del cliente para aliviar la tensión.»* → **L0**. El agente no tiene cuerpo. No hay parte sustancial que pueda hacer ni acelerar. Barreras: física = S, confianza = S. / *Massage therapist: "Apply pressure with the hands to the client's muscles to relieve tension."* → L0. No body; no substantial part can be done or sped up. Barriers: physical = Y, trust = Y.
2. *Bombero: «Entrar en un edificio en llamas para rescatar a personas atrapadas.»* → **L0**. Presencia física y decisión en el sitio. Barreras: física = S. / *Firefighter: "Enter a burning building to rescue trapped people."* → L0. Physical presence and on-site judgement. Barriers: physical = Y.

**L1**
3. *Médico de urgencias: «Examinar al paciente y decidir si requiere hospitalización.»* → **L1**. El agente puede resumir la historia, sugerir diagnósticos diferenciales y redactar la nota; la exploración, la decisión y la firma son del médico en cada paso. Barreras: física = S, responsabilidad = S. / *Emergency physician: "Examine the patient and decide whether admission is required."* → L1. The agent can summarise the record, suggest differentials and draft the note; the examination, the decision and the signature stay with the physician at every step. Barriers: physical = Y, accountability = Y.
4. *Profesor de secundaria: «Dirigir una discusión en clase sobre un texto literario.»* → **L1**. El agente prepara preguntas y materiales; la discusión en vivo la conduce la persona. Barreras: confianza = S. / *Secondary teacher: "Lead a classroom discussion on a literary text."* → L1. The agent prepares questions and materials; the live discussion is led by the human. Barriers: trust = Y.

**L2**
5. *Contador: «Preparar la declaración trimestral de impuestos de una pequeña empresa.»* → **L2**. Con acceso al sistema contable, el agente concilia, clasifica y llena el formulario completo; una persona revisa y firma porque la ley lo exige. Barreras: responsabilidad = S. / *Accountant: "Prepare a small firm's quarterly tax return."* → L2. With access to the accounting system the agent reconciles, classifies and fills the whole form; a human reviews and signs because the law requires it. Barriers: accountability = Y.
6. *Ingeniero civil: «Diseñar el sistema de drenaje de una vía secundaria.»* → **L2**. El agente modela caudales, dimensiona tuberías y produce planos preliminares; el ingeniero verifica supuestos de campo y firma el diseño. Barreras: responsabilidad = S, acceso = S (datos de campo). / *Civil engineer: "Design the drainage system for a secondary road."* → L2. The agent models flows, sizes pipes and produces preliminary drawings; the engineer checks field assumptions and signs. Barriers: accountability = Y, access = Y (field data).

**L3**
7. *Analista de datos: «Elaborar el informe mensual de ventas por región a partir de la base de datos de la empresa.»* → **L3**. Con acceso a la base, el agente consulta, calcula, grafica y entrega el informe con la calidad que aceptaría un analista competente. Barreras: ninguna. / *Data analyst: "Produce the monthly sales report by region from the company database."* → L3. With database access the agent queries, computes, charts and delivers the report to the quality a competent analyst would accept. Barriers: none.
8. *Asistente administrativo: «Programar reuniones con varios participantes y enviar las invitaciones de calendario.»* → **L3**. El agente lee las agendas, propone horarios, resuelve conflictos por correo y envía las invitaciones. Barreras: ninguna (acceso = N si tiene el calendario). / *Administrative assistant: "Schedule meetings with several participants and send the calendar invitations."* → L3. The agent reads calendars, proposes times, resolves conflicts by email and sends the invitations. Barriers: none (access = N given calendar access).

**Dos aclaraciones / Two clarifications.** (a) Una barrera legal (responsabilidad) no baja por sí sola el nivel: califique la factibilidad técnica y marque la barrera. Pero si la ley exige que la persona *ejecute* un paso esencial, el nivel máximo es L2. / A legal barrier (accountability) does not by itself lower the level: rate technical feasibility and tick the barrier. But if the law requires the human to *perform* an essential step, the ceiling is L2. (b) Si el enunciado mezcla partes físicas y digitales, califique la tarea como un todo y use `share_delegable` para el porcentaje de tiempo que el agente podría asumir. / If the statement mixes physical and digital parts, rate the task as a whole and use `share_delegable` for the share of time the agent could take over.

---

## Cómo llenar cada columna

| Columna / Column | Qué poner / What to enter |
|---|---|
| `task_id`, `occupation`, `task` | No modificar. / Do not edit. |
| `level (0-3)` | Un entero 0, 1, 2 o 3. / One integer, 0, 1, 2 or 3. |
| `share_delegable (0-100)` | Porcentaje del tiempo de trabajo de la tarea que un agente podría asumir. L0 suele ser 0–10; L3 suele ser 80–100. / Percent of the task's working time an agent could take over. L0 is usually 0–10; L3 usually 80–100. |
| `minutes_human` | Minutos que una persona competente tarda en una instancia típica de la tarea (entero; si la tarea dura días, convierta a minutos). / Minutes a competent human needs for one typical instance (integer; convert days to minutes). |
| `barrier_physical (S/N)` | S si la tarea exige presencia o manipulación física. / Y if the task needs physical presence or manipulation. |
| `barrier_accountability (S/N)` | S si una ley, licencia o responsabilidad profesional exige que una persona ejecute o firme. / Y if law, licence or professional liability requires a human to perform or sign. |
| `barrier_trust (S/N)` | S si la tarea depende de confianza, cuidado o persuasión en persona. / Y if the task depends on in-person trust, care or persuasion. |
| `barrier_access (S/N)` | S si depende de sistemas, datos o lugares a los que un agente normalmente no llegaría. / Y if it depends on systems, data or places an agent would normally not reach. |
| `confidence (LOW/MEDIUM/HIGH)` | Su seguridad en el nivel asignado. / Your confidence in the level. |
| `comentario` | Opcional. Útil cuando el enunciado es ambiguo. / Optional. Useful when the statement is ambiguous. |


Escribe **S** o **N** en las barreras (Y/N también vale). No dejes filas vacías: si una tarea es incomprensible, pon tu mejor
estimación, `confidence = LOW` y un comentario. Guarda con frecuencia.

## Al terminar

Revisa que las 300 filas tengan `level`, guarda como `hoja_Santiago_LISTA.xlsx` y envíalo. Solo después de entregar podrás ver los
resultados del estudio. ¡Gracias!

---
Muestra: 300 tareas estratificadas por gran grupo ISCO-08 de la muestra de validación de 1.500 (semilla 20261025; orden aleatorio,
semilla 20261026). Desviación D2 del preregistro.
