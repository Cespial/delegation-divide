# ADI scoring rubric v1 (frozen at preregistration)

You are rating ONE occupational task for how much of it a current AI agent could carry out.

**Reference technology (fixed): publicly available AI agents as of October 2026.** These are frontier language models with
tool use, code execution, web browsing, computer use (operating a desktop or browser) and file handling, able to work
autonomously on multi-step jobs that take a human several hours. They have **no physical body or robotics**. They act
only through software, documents, messages and digital systems the worker would normally be able to reach.

OCCUPATION: {occupation_title}
TASK: {task_text}

## Definitions (use exactly these)

- **L0 — No meaningful role.** The agent cannot perform or materially speed up any substantial part of the task.
- **L1 — Augmentation.** A human performs the task; the AI assists step by step (drafts, searches, suggestions). The human
  stays in the loop at each step and produces the output.
- **L2 — Partial delegation.** An agent can execute substantial sub-steps of the task end to end from a goal
  specification. A human still has to perform at least one essential step or review and correct the work before use.
- **L3 — Full delegation.** An agent can complete the whole task end to end, to the quality a competent worker would
  accept, given only the goal and access. The human's role is limited to assigning it and accepting the result.

Rate what is **technically feasible** with the reference technology, not what employers currently do, and not what is
legally allowed (the legal barrier is recorded separately below).

## Output

Return ONLY this JSON (no markdown, no commentary):
{{"level": <0|1|2|3>,
 "share_delegable": <int 0-100, percent of the task's working time an agent could take over>,
 "minutes_human": <int, typical minutes a competent human needs for one instance of the task>,
 "barrier_physical": <true|false, task needs physical presence or manipulation>,
 "barrier_accountability": <true|false, law, licence or professional liability requires a human to perform or sign>,
 "barrier_trust": <true|false, task depends on in-person trust, care or persuasion>,
 "barrier_access": <true|false, task depends on systems, data or places an agent would normally not reach>,
 "confidence": "<LOW|MEDIUM|HIGH>"}}
