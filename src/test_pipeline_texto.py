import pytest

from src.pipeline_texto import limpiar_texto, procesar_texto

#bloque 15

def test_procesar_texto_normaliza_mayuscula_y_puntuacion(): # por que no solo dice texto_normalizado en la pauta...
    resultado = procesar_texto("El Cielo, es AZUL!")
    assert resultado ==["el", "cielo", "es", "azul"]

def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    resultado = procesar_texto(" ¡¡¡...!!!")
    assert resultado == []

def test_limpiar_texto_conserva_tildes_y_enie(): # es la eñe que sino saldria caracter raro
    assert limpiar_texto("¡El Vuelo esta bien!") == "el vuelo esta bien"

def test_limpiar_texto_rechaza_lo_que_no_es_texto():
    with pytest.raises(TypeError):
        limpiar_texto(None)