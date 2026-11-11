import os
from importlib.metadata import version, PackageNotFoundError

from dotenv import load_dotenv

load_dotenv()

try:
    print("google-genai instalado, version", version("google-genai"))
except PackageNotFoundError:
    raise SystemExit("La libreria no se encuentra, Ejecuta pip install google-genai python-dotev")

if os.environ.get("GEMINI_API_KEY"):
    print("GEMINI_API_KEY detectada")
else:
    raise SystemExit('Falta GEMINI_API_KEY. Agregala al archivo ".env" de tu proyecto')
