from unittest.mock import MagicMock

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.enrutamiento import (
    MENSAJE_RESPALDO,
    construir_cadena_con_enrutamiento,
    construir_cadena_queja_segura,
    #construir_paso_clasificacion,
    procesar_mensaje_seguro,
)


def fallar_a_proposito(_):
    raise Exception("Error de red simulada")

'''
##pruebas erroneas

def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():
    modelo = MagicMock(return_value=AIMessage(content="queja"))
    cadena = construir_cadena_con_enrutamiento(
        construir_paso_clasificacion(modelo),
        cadena_queja=RunnableLambda(fallar_a_proposito),
    )
    assert cadena.invoke({"mensaje": "algo"}) == MENSAJE_RESPALDO

def test_procesar_mensaje_seguro_no_propaga_excepcion():
    cadena = RunnableLambda(fallar_a_proposito)
    assert procesar_mensaje_seguro(cadena, "mensaje de prueba") == MENSAJE_RESPALDO


def test_procesar_mensaje_seguro_ante_fallo_en_clasificacion():
    modelo = MagicMock(side_effect=ConnectionError("sin red"))
    cadena = construir_cadena_con_enrutamiento(construir_paso_clasificacion(modelo))
    assert procesar_mensaje_seguro(cadena, "mensaje de prueba") == MENSAJE_RESPALDO
'''

def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():
    cadena_queja_segura = construir_cadena_queja_segura(RunnableLambda(fallar_a_proposito))
    resultado = cadena_queja_segura.invoke({"mensaje": "esto no funciona"})
    assert "equipo" in resultado.lower()


def test_procesar_mensaje_seguro_no_propaga_excepciones():
    clasificacion_falsa = MagicMock(side_effect=ConnectionError("simulado"))
    cadena_falsa = construir_cadena_con_enrutamiento(paso_clasificacion=clasificacion_falsa)
    resultado = procesar_mensaje_seguro(cadena_falsa, "mensaje de prueba")
    assert "no pudimos procesar" in resultado.lower()