import json
import os
import time

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)
from prompts.banco import BANCO_DE_PROMPTS

INTENTOS = 3
PAUSA_SEGUNDOS = 2  # sube a 3 si aparecen errores 429
RUTA_REGISTRO = "prompts/registro_resultados.json"

registro = {}

for prompt in BANCO_DE_PROMPTS:
    exitos = 0
    print(f"--- {prompt['nombre']} ---")

    for intento in range(INTENTOS):
        try:
            url, headers, body = armar_peticion(
                prompt["ejemplo_usuario"],
                system_instruction=prompt["system_instruction"],
                response_schema=prompt.get("response_schema"),
            )
            respuesta = enviar_peticion(url, headers, body)
            texto = extraer_texto(respuesta)
            parsear_respuesta_json(texto, claves_requeridas=prompt["claves_esperadas"])
            exitos += 1
        except (ValueError, RuntimeError, TimeoutError, FileNotFoundError) as error:
            print(f"  intento {intento + 1} falló: {error}")
        time.sleep(PAUSA_SEGUNDOS)

    print(f"{prompt['nombre']}: {exitos}/{INTENTOS} respuestas válidas")
    registro[prompt["nombre"]] = {"exitos": exitos, "intentos": INTENTOS}

os.makedirs("prompts", exist_ok=True)
with open(RUTA_REGISTRO, "w", encoding="utf-8") as archivo:
    json.dump(registro, archivo, indent=2, ensure_ascii=False)

print(f"\nRegistro guardado en {RUTA_REGISTRO}")