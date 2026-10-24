from src.consumir_gemini import armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json


SYSTEM_INSTRUCTION = (
    "Clasificas mensajes de usuarios de una mesa de ayuda. "
    "Responde únicamente con un objeto JSON válido, sin usar bloques de markdown. "
    "El JSON debe tener exactamente estas claves: "
    "'categoria' (string) y 'confianza' (número entre 0 y 1)."
)


RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "categoria": {"type": "STRING"},
        "confianza": {"type": "NUMBER"},
    },
    "required": ["categoria", "confianza"],
}


PREGUNTA = "Necesito ayuda para resetear mi contraseña, no me llega el correo de verificación."


try:
    url, headers, body = armar_peticion(
        PREGUNTA,
        system_instruction=SYSTEM_INSTRUCTION,
        response_schema=RESPONSE_SCHEMA,
    )
    respuesta_json = enviar_peticion(url, headers, body)
    texto = extraer_texto(respuesta_json)
    datos = parsear_respuesta_json(texto)

    print(datos)
    print(type(datos))
    print(f"categoria: {datos['categoria']} | Confianza: {datos['confianza']}")
except (ValueError, RuntimeError, TimeoutError, FileNotFoundError) as error:
    print("No se pudo completar la operacion:", error)
