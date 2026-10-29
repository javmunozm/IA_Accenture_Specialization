from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.consumir_gemini import MODELO_POR_DEFECTO


def construir_modelo():
    return ChatGoogleGenerativeAI(model = MODELO_POR_DEFECTO, temperature=0)


def construir_cadena(modelo):
    plantilla_puntos = PromptTemplate.from_template(
        "Extrae los puntos clave del mensaje del  cliente. "
        "Responde solo con los puntos, uno por linea. \n\nMensaje: {mensaje}"
    )

    plantilla_resumen = PromptTemplate.from_template(
        "Resume estos puntos clave en 1 o 2 oraciones, en lenguaje simple.\n\n"
        "Puntos: {puntos}"
    )
    plantilla_lista = PromptTemplate.from_template(
        "Convierte ese texto en una lista de viñetas, sin introduccion. \n\n"
        "Texto: {resumen}"
    )

    return (
        plantilla_puntos
        | modelo
        | StrOutputParser()
        | (lambda puntos: {"puntos": puntos})
        | plantilla_resumen
        | modelo
        |StrOutputParser()
        | (lambda resumen: {"resumen": resumen})
        | plantilla_lista
        | modelo
        | StrOutputParser()
    )

if __name__ == "__main__":
    MENSAJE = (
        "Hola, desde ayer la app falla cuando intento subir una imagen "
        "y la he reinstalado dos veces. Necesito subir un comprobante hoy."
    )
    try:
        print(construir_cadena(construir_modelo()).invoke({"mensaje": MENSAJE}))
    except Exception as error:
        print("No se pudo completar la operacion:",  error)