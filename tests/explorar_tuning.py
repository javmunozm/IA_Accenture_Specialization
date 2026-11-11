try:
    from google.genai import types
except ImportError:
    raise SystemExit("No se pudo importar google.genai. Ejecuta pip install google-genai")

try:
    print("Modos de tuning disponibles:")
    for modo in types.TuningMode:
        print(" ", modo)

    print()
    print("Tamaños de adapter disponibles (solo aplica a PEFT):")
    for tamano in types.AdapterSize:
        print(" ", tamano)
except AttributeError as e:
    raise SystemExit(f"Tu version del SDK no expote este tipo: {e}. Actualiza con pip install -U google-genai")

print()
for campo in ["epoch_count", "learning_rate_multiplier", "batch_size"]:
    try:
        descripcion = types.CreateTuningJobConfig.model_fields[campo].description
        print(campo, "->", descripcion)
    except KeyError:
        print(campo, "-> este campo no existe en tu version del SDK")

def explicar_error(error):
    mensaje = str(error)
    if "API key" in mensaje or "401" in mensaje or "403" in mensaje:
        return "Problema de autenticacion: revisa GEMINI_API_KEY en tu archivo .env"
    if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
        return "Cuota o limite de peticiones agotado: espera unos minutos y reintenta."
    if "Connection" in mensaje or "timed out" in mensaje:
        return "Problema de conexion: revisa tu internet y vuelve a intentarlo."
    return "Error inesperado: " + mensaje


print()
ejemplos = [
    Exception("400 INVALID_ARGUMENT. API key not valid. Please pass a valid API key."),
    Exception("429 RESOURCE_EXHAUSTED. Quota exceeded for this project."),
    Exception("Connection reset by peer"),
]
for ejemplo in ejemplos:
    print(explicar_error(ejemplo))
    