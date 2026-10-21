BATCH MODE. The OCCUPATION and TASK fields above are given in the numbered TASKS list below instead. Rate each listed task
on its own, exactly as if it were the only task you were shown: do not compare tasks with each other, do not spread levels
across the list, and do not let one task's rating influence another's.

Return ONLY a JSON array (no markdown, no commentary) with exactly one object per listed task, in the same order. Each object
starts with "task_id" (the number in brackets) followed by the eight fields of the JSON above:
[{{"task_id": <id>, "level": ..., "share_delegable": ..., "minutes_human": ..., "barrier_physical": ..., "barrier_accountability": ...,
  "barrier_trust": ..., "barrier_access": ..., "confidence": ...}}, ...]

TASKS ({n}):
{lista}
