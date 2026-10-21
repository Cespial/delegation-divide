# Modelos evaluadores (congelados en el registro osf.io/9zntf, 21-oct-2026)

| Rol | Modelo (id devuelto por el CLI) | Ruta |
|---|---|---|
| Primario | Claude Sonnet 5.5 (`claude-sonnet-5-5`) | `claude -p --model sonnet` |
| Secundario | Claude Haiku 5.5 (`claude-haiku-5-5`) | `claude -p --model haiku` |

Configuración neutra (`scoring/llm_cli.py`, `ADI_CLI_MINIMO=1`): `--tools "" --strict-mcp-config --no-session-persistence
--system-prompt "You are an expert rater of occupational tasks. Follow the user instructions exactly."`. Una tarea por llamada.
Claude Code 2.1.306. Sin control de temperatura: test-retest en 100 tareas por modelo (`scoring/salidas/retest/`).

Piloto (descartado, `scoring/salidas/piloto/INFORME.md`): JSON válido 100 %; lotes de 25 rechazados (κ 0,60 Sonnet, 0,56 Haiku
frente a la llamada individual; regla ≥ 0,80); envoltorio por defecto de Claude Code da nivel medio 1,64 frente a 1,33 del neutro
(κ 0,70) → sensibilidad preregistrada sobre las 1.500 tareas de validación. Cuota: ≈ US$0,009 por llamada en modo neutro.
DeepSeek y Kimi retirados antes del registro.
