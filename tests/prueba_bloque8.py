from src.Modulo_1.Bloque_5_6_7.consumir_gemini import armar_peticion, enviar_peticion, extraer_texto

url, headers, body = armar_peticion("¿Que es un token? Responde en una frase")
respuesta_json = enviar_peticion(url, headers, body)
print(extraer_texto(respuesta_json))
print(respuesta_json["usageMetadata"])
