BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_mensaje",
        "system_instruction": (
            "Clasificas mensajes de usuarios de una mesa de ayuda. "
            "Responde unicamente con un objeto JSON valido, sin bloques de markdown, con las claves "
            "'categoria' (una de: 'soporte_tecnico', 'facturacion', 'cuenta', 'otro') "
            "y 'confianza' (numero entre 0 y 1)."
        ),
        "ejemplo_usuario": "hola no puedo entrar a mi cuenta, le di a recuperar clave y no me llega el correo, ya revise spam y nada",
        "claves_esperadas": ["categoria", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "categoria": {"type": "STRING"},
                "confianza": {"type": "NUMBER"},
            },
            "required": ["categoria", "confianza"],
        },
    },
    {
        "nombre": "extraer_datos",
        "system_instruction": (
            "Extraes datos de mensajes de usuarios de una mesa de ayuda. "
            "Responde unicamente con un objeto JSON valido, sin bloques de markdown, con las claves "
            "'producto' (string, o 'desconocido' si no se menciona), "
            "'problema' (string, en maximo 10 palabras) "
            "y 'urgencia' (una de: 'baja', 'media', 'alta')."
        ),
        "ejemplo_usuario": "la app del celu se cierra sola cada vez q intento pagar, desde ayer q esta asi y la cuenta me vence el lunes",
        "claves_esperadas": ["producto", "problema", "urgencia"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "producto": {"type": "STRING"},
                "problema": {"type": "STRING"},
                "urgencia": {"type": "STRING"},
            },
            "required": ["producto", "problema", "urgencia"],
        },
    },
    {
        "nombre": "resumen_corto",
        "system_instruction": (
            "Resumes mensajes de usuarios de una mesa de ayuda para el equipo de soporte. "
            "Responde unicamente con un objeto JSON valido, sin bloques de markdown, con las claves "
            "'resumen' (string, una sola oracion) "
            "y 'palabras_clave' (lista de 1 a 3 strings)."
        ),
        "ejemplo_usuario": (
            "hola compre el plan anual hace como una semana pero me siguen cobrando mensual "
            "y tampoco puedo bajar la factura del portal, q onda?? alguien me ayuda"
        ),
        "claves_esperadas": ["resumen", "palabras_clave"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "resumen": {"type": "STRING"},
                "palabras_clave": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["resumen", "palabras_clave"],
        },
    },
]