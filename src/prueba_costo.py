###prueba sin api
###from src.Modulo_1.Bloque_5_6_7.consumir_gemini import calcular_costo
'''
datos = {"usageMetadata": {"promptTokenCount": 850, "candidatesTokenCount": 320, "totalTokenCount": 1170}}

costo = calcular_costo(datos,  0.00000010, 0.00000040)
print(costo)
print(f"{costo:.6f}")
'''
from src.consumir_gemini import armar_peticion, enviar_peticion, calcular_costo
### no tiene manejo de errores...
'''

url, headers, body = armar_peticion("¿Que es un token? Responde en una frase.")
respuesta_json = enviar_peticion(url, headers, body)
print(respuesta_json["usageMetadata"])
print(f"Costo real de esta peticion: {calcular_costo(respuesta_json, 0.00000010, 0.00000040):.6f} USD")
'''
PRECIO_ENTRADA = 0.30 / 1_000_000
PRECIO_SALIDA = 2.50 / 1_000_000

try:
    url, headers, body = armar_peticion("¿Que es un token? Responde en una frase.")
    respuesta_json = enviar_peticion(url, headers, body)
    print(respuesta_json["usageMetadata"])
    costo = calcular_costo(respuesta_json, PRECIO_ENTRADA, PRECIO_SALIDA)
    print(f"Costo real de esta peticion: {costo:.6f} USD")
except (ValueError, RuntimeError) as error:
    print("No se pudo completar la operacion:", error)
