# Modelos evaluadores (se congela antes de la corrida principal)

Regla del preregistro: «regla + versión exacta». Ningún modelo se agrega ni se quita después de ver resultados de la corrida principal.

| Rol | Modelo | Ruta | Identificador exacto | Temperatura | Estado |
|---|---|---|---|---|---|
| Primario | Claude Sonnet | `claude -p --model sonnet` (CLI de Claude Code, suscripción) | se registra el `model` que devuelve el CLI + versión del CLI (`2.1.305` el 20-oct) | no controlable → test-retest reportado | piloto en curso |
| Secundario | Claude Haiku | `claude -p --model haiku` | ídem | ídem | piloto en curso |
| Pesos abiertos 1 | DeepSeek V4-Pro | API `api.deepseek.com` (`DEEPSEEK_API_KEY`) | `deepseek-v4-pro` + fecha | 0 | falta recarga (≈ US$10) |
| Pesos abiertos 2 | Kimi K2.6 | API `api.moonshot.ai/v1` (`MOONSHOT_API_KEY`) | id exacto de la consola Moonshot | 0 | falta recarga (≈ US$25) |
| Sensibilidad | DeepSeek V4-Flash | API DeepSeek | `deepseek-v4-flash` | 0 | opcional |

Costo estimado por pasada completa (18.796 tareas; 12,7 M tokens de entrada, 1,7 M de salida): Flash ≈ US$2, V4-Pro ≈ US$7 (promo) a
US$28 (tarifa plena), Kimi K2.6 ≈ US$19. Claves en `~/.config/adi/.env`, nunca en el repo.

Ritmo medido de la ruta CLI (piloto 20-oct): ≈ 6,5 s por llamada en serie → la corrida principal necesita 6–8 procesos en paralelo
o lotes de varias tareas por llamada (decisión tras el informe del piloto, antes de registrar).

Enmienda pendiente del borrador OSF (campo 344-40, «Models»): reemplazar «flagship de OpenAI y de Google + mejor pesos abiertos de
LMArena» por la tabla de arriba. El borrador no está registrado: es una edición, no una desviación.
