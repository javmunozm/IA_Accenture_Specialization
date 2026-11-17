import os
import sys
from importlib.metadata import version, PackageNotFoundError

PAQUETES = ["langchain-core", "langchain-chroma", "langchain-google-genai", "google-genai",
            "langgraph", "python-dotenv", "pytest"]
VARIABLES = ["GEMINI_API_KEY"]
INDICE_DIR = "vectorstore"  # (CARPETA_VECTORSTORE)
# from dotenv import load_dotenv

# load_dotenv()

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# try:
#     print("google-genai instalado, version", version("google-genai"))
# except PackageNotFoundError:
#     raise SystemExit("La libreria no se encuentra, Ejecuta pip install google-genai python-dotev")

# if os.environ.get("GEMINI_API_KEY"):
#     print("GEMINI_API_KEY detectada")
# else:
#     raise SystemExit('Falta GEMINI_API_KEY. Agregala al archivo ".env" de tu proyecto')

problemas = []
print("Python:", sys.version.split()[0])
if sys.version_info < (3, 10):
    problemas.append("usar Python 3.10 o superior")

for paquete in PAQUETES:
    try:
        print(f"{paquete}: {version(paquete)}")
    except PackageNotFoundError:
        print(f"{paquete}: No instalado")
        problemas.append(f"instalar {paquete}")

for nombre in VARIABLES:
    estado = "definida" if os.getenv(nombre) else "FALTA"
    print(f"{nombre}: {estado}")
    if estado == "FALTA":
        problemas.append(f"definir {nombre} en el archivo .env")

if os.path.isdir(INDICE_DIR) and os.listdir(INDICE_DIR):
    print(f"indice en {INDICE_DIR}/: ok")
else:
    print(f"indice en {INDICE_DIR}/: NO existe o esta vacio")
    problemas.append("indexar el corpus")

print()
if problemas:
    print("Pendientes: " + "; ".join(problemas))
    sys.exit(1)
print("Entorno listo para la corrida final")
