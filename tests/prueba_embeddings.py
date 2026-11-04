import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit('Falta GEMINI_API_KEY. Definela en tu archivo ".env" y vuelve a ejecutar.')

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

try:
    vector = embeddings.embed_query("El cliente reintenta ante un error")
except Exception as error:
    mensaje = str(error)
    if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
        print("limite de peticiones alcanzado. Espera un minuto y vuelve a ejecutar.")
    elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
        print('la API rechazo tu clave. Revisa el valor de GEMINI_API_KEY en tu ".env".')
    else:
        print("No se pudo generar el embedding:", type(error).__name__)
    print("Detalle tecnico:", mensaje)
    raise SystemExit(1)

print(len(vector))
print(vector[:5])