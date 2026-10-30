import logging
import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough

from src.cadena_tres_pasos import construir_modelo

logger = logging.getLogger(__name__)

PAUSA_SEGUNDOS = 2
MENSAJE_RESPALDO = (
    "No pudimos procesar tu mensaje en este momento. "
    "Intenta de nuevo mas tarde."
)

RESPUESTA_GENERICA = RunnableLambda(
    lambda _: "Gracias por tu mensaje. Un miembro de nuestro equipo te va a responder pronto."
)
INSTRUCCION_PREGUNTA = "Responde esta pregunta tecnica con precision."
INSTRUCCION_QUEJA = (
    "Responde a esta queja con empatia, reconociendo el problema "
    "antes de ofrecer una solucion u/o alternativa."
)
INSTRUCCION_SUGERENCIA = (
    "Agradece esta sugerencia y explica como se evaluara "
    "(dentro del producto)."
)

#stupid lambda
def normalizar_categoria(texto: str) -> str:
    return texto.strip().lower()

def construir_cadena_respuesta(modelo, instruccion):
    plantilla = PromptTemplate.from_template(instruccion + "\n\nMensaje: {mensaje}")
    return plantilla | modelo | StrOutputParser()


def construir_paso_clasificacion(modelo):
    plantilla = PromptTemplate.from_template(
        "Clasifica el siguiente mensaje de soporte en una sola palabra: "
        "pregunta, queja o sugerencia. Responde solo con esa palabra. \n\n"
        "Mensaje: {mensaje}"
    )
    return (
        plantilla
        | modelo
        | StrOutputParser()
        | RunnableLambda(normalizar_categoria)  #RunnableLambda(lambda texto: str(texto).strip().lower()) oh, funciona si hago un cast de texto..pero colapsa si no llega texto

    )

def construir_cadena_con_enrutamiento(
        paso_clasificacion,
        cadena_queja=None,
        cadena_sugerencia=None,
        cadena_pregunta=None,
):
    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja or RESPUESTA_GENERICA),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia or RESPUESTA_GENERICA),
        cadena_pregunta or RESPUESTA_GENERICA,
    )
    return RunnablePassthrough.assign(categoria=paso_clasificacion) | bifurcacion


def construir_cadena_queja_segura(cadena_queja):
    return cadena_queja.with_fallbacks([RESPUESTA_GENERICA])


def construir_flujo(modelo):
    return construir_cadena_con_enrutamiento(
        construir_paso_clasificacion(modelo),
        cadena_queja=construir_cadena_queja_segura(construir_cadena_respuesta(modelo, INSTRUCCION_QUEJA)),
        cadena_sugerencia=construir_cadena_respuesta(modelo, INSTRUCCION_SUGERENCIA),
        cadena_pregunta=construir_cadena_respuesta(modelo, INSTRUCCION_PREGUNTA),
    )

def procesar_mensaje_seguro(cadena, mensaje):
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error("Error procesando mensaje: %s", error)
        return MENSAJE_RESPALDO


if __name__ == "__main__":
    MENSAJES = [
        "¿Como cambio mi password?",
        "La app se cierra cada vez que subo una imagen.",
        "Estaria bueno que la app tenga modo obscuro",
    ]
    try:
        flujo = construir_flujo(construir_modelo())
    except Exception as error:
        print("No se pudo crear el modelo:", error)
    else:
        for mensaje in MENSAJES:
            print(f"> {mensaje}\n{procesar_mensaje_seguro(flujo, mensaje)}\n")
            time.sleep(PAUSA_SEGUNDOS)