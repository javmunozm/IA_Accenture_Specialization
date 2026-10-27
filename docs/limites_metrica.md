# Limites de la métrica de evaluación

## Que mide
Compara las palabras (con repeticiones) de la respuesta de `consultar_modelo` con las de una referencia escrita a mano, después de limpiarlas con `procesar_texto`, y entrega precisión, cobertura y F1 entre 0 y 1. Mide coincidencia de palabras, no si la respuesta es correcta.

## Modos de falla conocidos
- **Sinónimos o paráfrasis:** `que hace la funcion len en python?`, F1 0.07. La respuesta es correcta, pero solo coincide "elementos" (cuenta/número, algo/objeto).
- **Números escritos con letras:** `cuantos bits son un byte?`, F1 0.0. La referencia dice "8" y la respuesta "ocho": ninguna palabra en común.
- **Tildes:** `quien escribio cien años de soledad?`, F1 0.13. "garcia marquez" no coincide con "garcía márquez", así que el nombre correcto pierde 2 de 3 palabras.
- **Variantes de una palabra:** `para que sirve la temperatura en un modelo de lenguaje?`, F1 0.14. "creativa" frente a "creatividad" y "aleatoria" frente a "aleatoriedad" cuentan como palabras distintas.
- **Respuesta más larga que la referencia:** `cual es el oceano mas grande?`, F1 0.33 con cobertura 1.0. Cubre toda la referencia, pero las palabras extra bajan la precisión.
- **Negación:** no apareció en la muestra. Medido con `calcular_metricas`: "Python no es un lenguaje compilado" frente a "Python es un lenguaje compilado" da F1 0.91, aunque una frase dice lo contrario de la otra.

## Muestra revisada
10 casos: los 5 con menor F1 y los 5 con mayor F1, sobre 20 respuestas generadas el 2026-10-27 con `gemini-3.5-flash-lite`. F1 promedio de las 20: 0.25 (precisión 0.17, cobertura 0.59). Calificados a mano con la rúbrica: 10 de 10 respuestas correctas, 1 incompleta (json, no menciona "texto plano") y 0 contradicciones. Todos los F1 bajos fueron falsos negativos: el número castigó respuestas buenas.

## Recomendación de uso
- En este pipeline el F1 no sirve como nota de calidad: con 10 de 10 respuestas correctas, el promedio fue 0.25. Úsalo solo para comparar versiones del cliente o del `SYSTEM_INSTRUCTION` con las mismas 20 referencias: si el F1 cambia mucho entre versiones, revisa qué cambió.
- Revisa siempre a mano las respuestas con fechas, cifras, nombres propios o negaciones, aunque el F1 sea alto: un "no" casi no lo baja y un nombre con tilde lo hunde.
- Antes de la próxima medición: escribir referencias más completas y con tildes, en el mismo estilo que se espera de la respuesta, y evaluar si `limpiar_texto` debe normalizar tildes (cuidando la "ñ").
