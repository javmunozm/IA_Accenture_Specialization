###prueba sin api
###from src.Modulo_1.Bloque_5_6_7.consumir_gemini import calcular_costo
'''
datos = {"usageMetadata": {"promptTokenCount": 850, "candidatesTokenCount": 320, "totalTokenCount": 1170}}

costo = calcular_costo(datos,  0.00000010, 0.00000040)
print(costo)
print(f"{costo:.6f}")
'''
from src.Modulo_1.Bloque_5_6_7.consumir_gemini import armar_peticion, enviar_peticion, calcular_costo

url, headers, body = armar_peticion("¿Qué es un token? Responde en una frase.")
respuesta_json = enviar_peticion(url, headers, body)
print(respuesta_json["usageMetadata"])
print(f"Costo real de esta petición: {calcular_costo(respuesta_json, 0.00000010, 0.00000040):.6f} USD")