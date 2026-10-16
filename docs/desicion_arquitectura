# Decisión de arquitectura: modelo para la miniaplicación

Fecha: 15-10-2026
Estado: Aceptada

## Contexto

La app recibe una pregunta del usuario y la responde usando la API de Gemini. El flujo está en `src/Modulo_1/Bloque_5_6_7/consumir_gemini.py`: `armar_peticion` → `enviar_peticion` → `extraer_texto`, y `calcular_costo` calcula el costo de cada petición a partir de `usageMetadata`. El diagrama completo está en `docs/diagrama_arquitectura.png`.

Las preguntas de prueba son preguntas abiertas de usuarios sobre anime y cultura pop. Para este tipo de uso, el usuario espera una respuesta en pocos segundos y la aplicación puede recibir muchas peticiones, por lo que el costo por petición se multiplica.

Había que elegir qué modelo usar por defecto (`MODELO_POR_DEFECTO`).

## Opciones consideradas

1. **gemini-3.5-flash-lite**: modelo económico y rápido, sin razonamiento previo.
2. **gemini-3.7-flash**: modelo más capaz, que razona antes de responder (saturado y lento).

## Evidencia

Medido el 15-10-2026 con `src/Modulo_1/Bloque_8_9/comparar_modelos.py`. Detalle completo en `docs/comparacion_modelos.md` y `docs/mediciones.txt`.

| Criterio | gemini-3.5-flash-lite | gemini-3.7-flash |
| --- | --- | --- |
| Latencia promedio | 1,89 s | 5,46 s (sin el intento atípico de 26,62 s) |
| Costo real por petición | 0,000346 USD | 0,002468 USD |
| Costo mensual (50.000 peticiones) | 17,28 USD | 123,38 USD |
| Calidad | Buena, con errores menores en nombres propios | Muy buena, pero 2 de 3 preguntas superaron el timeout de 30 s |

## Decisión

Se usa **gemini-3.5-flash-lite** como modelo por defecto.

Los criterios que más pesan para esta miniaplicación son la latencia y valor, ademas cada repeticion cuesta dinero... gemini-3.5-flash-lite es casi 3 veces mas rapido 7 veces mas barato
para lo de este curso, y la calidad de respeusta requerida, gemini 3.5 flash lite es muy superior

gemini-3.7-flash dio mejores respuesta, pero tardaba mas y es cuando RESPONDIA

## Consecuencias

- **A favor:** respuesta mas rapidas, suficientes y baratas.
- **En contra:** se aceptan errores ocasionales y es bueno para recrear ciertos nombres.
- **Mitigación:** el modelo es un parámetro de `armar_peticion`, así que cambiarlo solo requiere modificar `MODELO_POR_DEFECTO`.

## Cuándo revisar esta decisión

- Si existen muchos reportes de respuestas inventadas
- Si suben el precio.
- Si se vuelve lento