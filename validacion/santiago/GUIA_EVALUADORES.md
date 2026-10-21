# Guía para evaluadores · Rater guide
## Agent Delegability Index (ADI) · validación humana / human validation

**ES** Gracias por participar. Usted es uno de tres evaluadores independientes. Su trabajo sirve para comprobar si las calificaciones de los modelos de lenguaje coinciden con el juicio de personas formadas. Nadie verá sus respuestas individuales fuera del equipo del estudio; en el artículo se publican solo estadísticas agregadas.

**EN** Thank you for taking part. You are one of three independent raters. Your ratings test whether the language models' ratings agree with the judgement of trained people. Nobody outside the study team will see your individual answers; the paper reports only aggregate statistics.

---

## 1. La tarea · The task

**ES** Recibirá 1.500 enunciados de tareas laborales tomados de O*NET (la base de datos ocupacional de Estados Unidos), cada uno con el título de su ocupación. Para cada tarea debe responder una sola pregunta: **¿cuánto de esta tarea podría ejecutar hoy un agente de IA?** Califica lo que es técnicamente posible con la tecnología de referencia, no lo que las empresas hacen ni lo que la ley permite (la barrera legal se anota aparte).

**Tecnología de referencia (fija):** agentes de IA disponibles al público en octubre de 2026: modelos de lenguaje de frontera con uso de herramientas, ejecución de código, navegación web, uso del computador (operar un escritorio o navegador) y manejo de archivos, capaces de trabajar solos varias horas en un encargo de varios pasos. **No tienen cuerpo ni robótica.** Actúan solo mediante software, documentos, mensajes y sistemas digitales a los que el trabajador normalmente tendría acceso.

**EN** You will receive 1,500 work-task statements from O*NET (the United States occupational database), each with its occupation title. For every task you answer one question: **how much of this task could an AI agent carry out today?** Rate what is technically feasible with the reference technology, not what employers do and not what the law allows (the legal barrier is recorded separately).

**Reference technology (fixed):** publicly available AI agents as of October 2026: frontier language models with tool use, code execution, web browsing, computer use (operating a desktop or browser) and file handling, able to work autonomously for hours on a multi-step job. **They have no body and no robotics.** They act only through software, documents, messages and digital systems the worker would normally reach.

---

## 2. La rúbrica · The rubric

Use exactamente estas definiciones (son las mismas que recibe el modelo; el texto íntegro está en la hoja «rubrica» de su archivo). / Use exactly these definitions (the model receives the same ones; the full text is in the "rubrica" sheet of your workbook).

| Nivel / Level | Definición / Definition |
|---|---|
| **L0 · Sin papel significativo · No meaningful role** | ES: El agente no puede ejecutar ni acelerar de forma material ninguna parte sustancial de la tarea. · EN: The agent cannot perform or materially speed up any substantial part of the task. |
| **L1 · Aumentación · Augmentation** | ES: Una persona hace la tarea; la IA ayuda paso a paso (borradores, búsquedas, sugerencias). La persona sigue en el circuito en cada paso y produce el resultado. · EN: A human performs the task; the AI assists step by step (drafts, searches, suggestions). The human stays in the loop at each step and produces the output. |
| **L2 · Delegación parcial · Partial delegation** | ES: Un agente puede ejecutar de punta a punta subpasos sustanciales de la tarea a partir de un objetivo. Una persona todavía debe hacer al menos un paso esencial, o revisar y corregir el trabajo antes de usarlo. · EN: An agent can execute substantial sub-steps of the task end to end from a goal specification. A human still has to perform at least one essential step or review and correct the work before use. |
| **L3 · Delegación completa · Full delegation** | ES: Un agente puede completar toda la tarea de punta a punta, con la calidad que aceptaría un trabajador competente, dados solo el objetivo y el acceso. El papel de la persona se limita a asignarla y aceptar el resultado. · EN: An agent can complete the whole task end to end, to the quality a competent worker would accept, given only the goal and access. The human's role is limited to assigning it and accepting the result. |

**Pregunta guía para distinguir L2 de L3 / Guiding question for L2 vs L3:** si usted le pasara la tarea a un agente con acceso a los mismos sistemas que el trabajador y se fuera a almorzar, ¿al volver estaría hecha y lista para usarse (L3), o tendría que hacer algo usted antes de usarla (L2)? / If you handed the task to an agent with the worker's access and went to lunch, would it be done and usable when you return (L3), or would you have to do something before using it (L2)?

**Pregunta guía para distinguir L1 de L2 / for L1 vs L2:** ¿el agente ejecuta un tramo completo sin que usted intervenga en cada paso (L2), o solo propone y usted ejecuta (L1)? / Does the agent run a whole stretch without you at each step (L2), or does it only suggest while you execute (L1)?

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

## 3. Cómo llenar la hoja · How to fill the sheet

Su archivo es `hoja_E1.xlsx`, `hoja_E2.xlsx` o `hoja_E3.xlsx` (el número es el suyo; no lo cambie). Tiene dos pestañas: **tareas** (lo que usted llena) y **rubrica** (solo lectura). El orden de las tareas es aleatorio y distinto para cada evaluador. / Your file is `hoja_E1.xlsx`, `hoja_E2.xlsx` or `hoja_E3.xlsx` (the number is yours; do not change it). It has two sheets: **tareas** (what you fill in) and **rubrica** (read only). Task order is random and differs across raters.

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

Escriba **S** o **N** en las barreras (en inglés puede escribir Y/N; ambos se aceptan). No deje filas vacías: si una tarea es incomprensible, ponga su mejor estimación, `confidence = LOW` y un comentario. Guarde con frecuencia y conserve el nombre del archivo. / Write **S** or **N** in the barrier columns (Y/N is also accepted). Leave no row empty: if a statement is unintelligible, give your best estimate, `confidence = LOW` and a comment. Save often and keep the file name.

---

## 4. Tiempo estimado · Time estimate

**ES** Alrededor de un minuto por tarea una vez tomada práctica: unas 25 horas en total. Recomendamos sesiones de máximo dos horas y terminar en tres semanas. Al final de cada sesión, anote hasta qué fila llegó. / **EN** About one minute per task once you are in rhythm: around 25 hours in all. We suggest sessions of at most two hours and completion within three weeks. At the end of each session note the row you reached.

---

## 5. Confidencialidad y reglas · Confidentiality and rules

**ES**
- **No use ninguna herramienta de IA** (ChatGPT, Claude, Gemini, Copilot u otras) para calificar, consultar o redactar. El estudio compara su juicio con el de los modelos; si usa un modelo, la comparación deja de tener sentido. Puede consultar diccionarios y descripciones ocupacionales públicas.
- No comente las tareas ni sus calificaciones con los otros evaluadores hasta que los tres hayan entregado.
- No comparta el archivo ni las tareas fuera del estudio.
- Usted no verá ninguna calificación de los modelos, por diseño.
- Si tiene dudas sobre la rúbrica, escriba al investigador principal; las aclaraciones se enviarán a los tres evaluadores por igual y quedarán registradas.

**EN**
- **Do not use any AI tool** (ChatGPT, Claude, Gemini, Copilot or others) to rate, look up or draft. The study compares your judgement with the models'; if you use a model, the comparison is meaningless. Dictionaries and public occupational descriptions are fine.
- Do not discuss the tasks or your ratings with the other raters until all three have delivered.
- Do not share the file or the tasks outside the study.
- You will not see any model rating, by design.
- If the rubric is unclear, write to the principal investigator; clarifications go to all three raters alike and are logged.

---

## 6. Práctica: 20 tareas · Practice: 20 tasks

**ES** Antes de abrir su hoja, califique estas 20 tareas (archivo `practica_20.csv`, mismas columnas que su hoja). Ninguna está en la muestra de 1.500. Después compararemos las tres hojas de práctica en una reunión corta de calibración y aclararemos las diferencias; esa reunión es la única ocasión en la que se discuten calificaciones entre evaluadores. El grupo 6 de la CIUO (agricultura) no aparece aquí porque todas sus tareas están en la muestra. / **EN** Before opening your sheet, rate these 20 tasks (file `practica_20.csv`, same columns as your sheet). None is in the 1,500-task sample. We then compare the three practice sheets in a short calibration meeting and clarify differences; that meeting is the only occasion on which ratings are discussed between raters. ISCO major group 6 (agriculture) is absent here because all its tasks are in the sample.

| # | task_id | Ocupación / Occupation | Tarea / Task |
|---|---|---|---|
| 1 | 8277 | Helpers--Carpenters | Secure stakes to grids for constructions of footings, nail scabs to footing forms, and vibrate and float concrete. |
| 2 | 5455 | School Psychologists | Maintain student records, including special education reports, confidential records, records of services provided, and behavioral data. |
| 3 | 2355 | Nannies | Instruct children in safe behavior, such as seeking adult assistance when crossing the street and avoiding contact with unsafe objects. |
| 4 | 3080 | Helpers--Installation, Maintenance, and Repair Workers | Tend and observe equipment and machinery to verify efficient and safe operation. |
| 5 | 15609 | Clinical Research Coordinators | Code, evaluate, or interpret collected study data. |
| 6 | 21560 | Appraisers and Assessors of Real Estate | Conduct regular reviews of property within jurisdictions to determine changes in property due to construction or demolition. |
| 7 | 2940 | Automotive Body and Related Repairers | Mix polyester resins and hardeners to be used in restoring damaged areas. |
| 8 | 23067 | Police and Sheriff's Patrol Officers | Investigate traffic accidents and other accidents to determine causes and to determine if a crime has been committed. |
| 9 | 11048 | Poets, Lyricists and Creative Writers | Plan project arrangements or outlines, and organize material accordingly. |
| 10 | 23501 | Loading and Moving Machine Operators, Underground Mining | Handle high voltage sources and hang electrical cables. |
| 11 | 22821 | Radiologic Technologists and Technicians | Provide assistance in dressing or changing seriously ill or injured patients or patients with disabilities. |
| 12 | 20284 | Secretaries and Administrative Assistants, Except Legal, Medical, and Executive | Compose, type, and distribute meeting notes, routine correspondence, or reports, such as presentations or expense, statistical, or monthly reports. |
| 13 | 11678 | Telecommunications Equipment Installers and Repairers, Except Line Installers | Address special issues or situations, such as illegal or unauthorized use of equipment, or cases of electrical or acoustic shock. |
| 14 | 9606 | Landscaping and Groundskeeping Workers | Use irrigation methods to adjust the amount of water consumption and to prevent waste. |
| 15 | 8441 | Camera and Photographic Equipment Repairers | Examine cameras, equipment, processed film, or laboratory reports to diagnose malfunction, using work aids and specifications. |
| 16 | 15674 | Investment Fund Managers | Evaluate the potential of new product developments or market opportunities, according to factors such as business plans, technologies, or market potential. |
| 17 | 6128 | Nursing Instructors and Teachers, Postsecondary | Collaborate with colleagues to address teaching and research issues. |
| 18 | 8007 | Gambling and Sports Book Writers and Runners | Collect bets in the form of cash or chips, verifying and recording amounts. |
| 19 | 11152 | Food Servers, Nonrestaurant | Place food servings on plates or trays according to orders or instructions. |
| 20 | 9806 | Logging Equipment Operators | Grade logs according to characteristics such as knot size and straightness, and according to established industry or company standards. |

---

*Protocolo preregistrado en OSF. Rúbrica congelada `scoring/prompts/rubrica_v1.md` (SHA-256 `bcd076fb…0ea0e46`). Contacto: Cristian Espinal Maya, Universidad Nacional de Colombia. / Protocol preregistered on OSF. Frozen rubric `scoring/prompts/rubrica_v1.md` (SHA-256 `bcd076fb…0ea0e46`). Contact: Cristian Espinal Maya, Universidad Nacional de Colombia.*
