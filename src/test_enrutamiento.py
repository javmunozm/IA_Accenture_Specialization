from unittest.mock import MagicMock

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.enrutamiento import construir_cadena_con_enrutamiento, construir_paso_clasificacion


def construir_con_categoria(categoria):
    modelo = MagicMock(return_value=AIMessage(content=categoria))
    return construir_cadena_con_enrutamiento(
        construir_paso_clasificacion(modelo),
        cadena_queja=RunnableLambda(lambda _: "respuesta de queja"),
        cadena_sugerencia=RunnableLambda(lambda _: "respuesta de sugerencia"),
        cadena_pregunta=RunnableLambda(lambda _: "respuesta de pregunta"),
    )

def test_clasificacion_normaliza_antes_de_comparar():
    modelo = MagicMock(return_value=AIMessage(content=" Queja \n"))
    resultado = construir_paso_clasificacion(modelo).invoke({"mensaje": "algo salio mal"})
    assert resultado == "queja"

def test_enrutamiento_va_a_cadena_queja():
    resultado = construir_con_categoria("queja").invoke({"mensaje": "no funciona"})
    assert resultado == "respuesta de queja"


def test_enrutamiento_va_a_cadena_sugerencia():
    resultado = construir_con_categoria("sugerencia").invoke({"mensaje": "agreguen modo obscuro"})
    assert resultado == "respuesta de sugerencia"

def test_enrutamiento_va_a_cadena_pregunta():
    resultado = construir_con_categoria("pregunta").invoke({"mensaje": "¿como cambio mi password?"})
    assert resultado == "respuesta de pregunta"


def test_enrutamiento_usa_default_ante_categoria_desconocida():
    resultado = construir_con_categoria("categoria_inventada").invoke({"mensaje": "mensaje ambiguo"})
    assert resultado == "respuesta de pregunta"