from src.consumir_gemini import armar_peticion, enviar_peticion, extraer_texto

SYSTEM_INSTRUCTION = "Eres un asistente tecnico, responde siempre maximo en 3 oraciones"
PREGUNTA = "Explica que es una API en terminos simples"

try:
    url, headers, body = armar_peticion(PREGUNTA,system_instruction=SYSTEM_INSTRUCTION)
    respuesta_json = enviar_peticion(url, headers, body)
    texto = extraer_texto(respuesta_json)
    print(texto)
except (ValueError, RuntimeError, TimeoutError, FileNotFoundError) as error:
    print("No se puede completar la operacion:", error)