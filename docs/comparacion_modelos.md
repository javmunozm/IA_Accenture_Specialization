# Comparación de modelos candidatos

Fecha: 15-10-2026
Fuente : https://ai.google.dev/gemini-api/docs/pricing
Pregunta de prueba de latencia y costo: "Explica en un párrafo qué es una API." (4 repeticiones por modelo)
Preguntas de calidad: "¿Bleach es mejor que Naruto?", "¿Qué es una pregunta de calidad?", "¿Cómo Vegeta y Goku son tan importantes?"
Evidencia: docs/mediciones.txt, docs/respuestas_gemini-3.5-flash-lite.txt, docs/respuestas_gemini-3.7-flash.txt

## Tabla comparativa

| Criterio | gemini-3.5-flash-lite | gemini-3.7-flash |
| --- | --- | --- |
| Costo por 1000 tokens de entrada | 0,000300 USD | 0,000750 USD |
| Costo por 1000 tokens de salida | 0,002500 USD | 0,003750 USD |
| Latencia promedio observada | 1,89 s (4 intentos, entre 1,36 y 2,35 s) | 5,46 s (3 intentos estables; el primero, 26,62 s, se excluye como atípico) |
| Tokens de la petición de prueba | 10 entrada + 137 salida = 147 | 10 entrada + 159 salida + 497 de razonamiento = 666 |
| Costo real por petición (incluye razonamiento) | 0,000346 USD | 0,002468 USD |
| Costo mensual estimado (50.000 peticiones) | 17,28 USD | 123,38 USD |
| Calidad de respuesta para mi caso | Buena: respondió las 3 preguntas y bien completas. Errores menores en nombres  ("Taito Kubo" por Tite Kubo, "Sos Aizen" por Sōsuke Aizen). | Muy buena en la única respuesta obtenida: nombres correctos y comparación más matizada. Las otras 2 preguntas superaron el timeout de 30 s. |

## Observaciones de la medición

- **Tokens de razonamiento.** gemini-3.7-flash razona antes de responder: usó 497 tokens de razonamiento (`thoughtsTokenCount`) para una respuesta visible de 159. Gemini cobra esos tokens al precio de salida. Usando la formula de la pauta del curso, que solo suma `candidatesTokenCount`, el costo daba 0,000604 USD; el costo real es 0,002468 USD, unas 4 veces mas... gemini-3.5-flash-lite no razona?.
- **Latencia.** El primer intento de gemini-3.7-flash tardó 26,62 s, bastante mas lento que 3.5, en promedio casi 3 veces mas lento...
- **Timeout.** 2 de las 3 preguntas de calidad de gemini-3.7-flash superaron el límite de 30 s de `enviar_peticion`. En la app eso se recibe como error.
- **Calidad.** Ambos modelos entregan respuestas extensas y bien estructuradas. La diferencia observada es en los detalles (nombres propios), no de utilidad general de la respuesta.
- **Precios.** Los valores por 1000 tokens son los que se cargaron en `comparar_modelos.py`; deben coincidir con la página oficial en la fecha indicada.

## Decisión

Ver docs/decision_arquitectura.md. Resumen: se elige **gemini-3.5-flash-lite**.