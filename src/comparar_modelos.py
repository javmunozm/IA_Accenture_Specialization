import os
import time 

from src.consumir_gemini import armar_peticion, enviar_peticion, extraer_texto, calcular_costo

MODELOS = {
    "gemini-3.5-flash-lite": {"entrada": 0.30, "salida": 2.50},
    "gemini-3.7-flash": {"entrada": 0.75, "salida": 3.75}, ##intente varias veces con 3.8 pero no respondia
}

PREGUNTA_PRUEBA = "Explica en un párrafo qué es una API."

PREGUNTAS_CALIDAD = [
    "¿Bleach es mejor que naruto?",
    "¿Que es una pregunta de calidad?",
    "¿Como vegeta y goku son tan importantes?",
]

REPETICIONES = 4
PAUSA_SEGUNDOS = 2 #429 avoidance

os.makedirs("docs", exist_ok=True)

for modelo, precio in MODELOS.items():
    precio_entrada = precio["entrada"] / 1_000_000
    precio_salida = precio["salida"] / 1_000_000
    print(f"\n=== {modelo} ===")

    try:
        latencias =[]
        for i in range(REPETICIONES):
            url, headers, body = armar_peticion(PREGUNTA_PRUEBA, modelo)
            inicio = time.perf_counter()
            respuesta_json = enviar_peticion(url, headers, body)
            fin = time.perf_counter()
            latencias.append(fin-inicio)
            print(f"intento {i+1}: {latencias[-1]: .2f} segundos")
            time.sleep(PAUSA_SEGUNDOS)
        print(f"Latencia promedio: {sum(latencias) / len(latencias):.2f} segundos")
        costo = calcular_costo(respuesta_json, precio_entrada, precio_salida)
        print(f"Tokens: {respuesta_json['usageMetadata']}")
        print(f"Costo de la última petición: {costo:.6f} USD")
        print(
            f"Costo por 1000 tokens -> entrada: {precio_entrada * 1000:.6f} USD"
            f" | salida: {precio_salida * 1000:.6f} USD"
        )

        ruta = f"docs/respuestas_{modelo}.txt"
        with open(ruta, "w", encoding="utf-8") as archivo:
            for pregunta in PREGUNTAS_CALIDAD:
                url, headers, body = armar_peticion(pregunta, modelo)
                texto = extraer_texto(enviar_peticion(url, headers, body))
                archivo.write(f"PREGUNTA: {pregunta}\nRESPUESTA:\n{texto}\n\n")
                time.sleep(PAUSA_SEGUNDOS)
        print(f"Respuestas de calidad guardadas en {ruta}")

    except (ValueError, RuntimeError, TimeoutError, FileNotFoundError) as error:
        print(f"No se pudo medir {modelo}: {error}")