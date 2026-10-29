from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from src.cadena_tres_pasos import construir_cadena

def test_cadena_ejecuta_los_tres_pasos_en_orden():
    modelo = MagicMock(side_effect=[
        AIMessage(content="app se cierra\nsubir imagen"),
        AIMessage(content="La app se cierra al subir una imagen."),
        AIMessage(content="- La app se cierra al subir una imagen.")
    ])
    resultado = construir_cadena(modelo).invoke({"mensaje": "La ap se cierra al subir una imagen"})
    assert resultado == "- La app se cierra al subir una imagen."
    assert modelo.call_count == 3