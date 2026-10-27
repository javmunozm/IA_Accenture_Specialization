import pytest

from src.pipeline_texto import limpiar_texto, procesar_texto
from src.metricas import calcular_metricas, contar_coincidencias, resumir_metricas

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

#bloque 16
# sigo sufriendo con el nombre de las funciones...
def test_contar_coincidencias_respeta_repeticiones():
    assert contar_coincidencias(["el", "gato"], ["el", "gato", "el", "gato"]) == 2

def test_calcular_metricas_ejemplo_a_mano():
    metricas = calcular_metricas("El gato duerme en el sillon", "El gato duerme en el sofa todo el dia")
    assert metricas["cobertura"] == pytest.approx(5 / 6)
    assert metricas["f1"] == pytest.approx(2 / 3)

def test_calcular_metricas_respuesta_vacia_no_divide_por_cero():
    assert calcular_metricas("El cielo es azul.","¡¡¡...!!!") == {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

def test_resumir_metricas_promedia_y_tolera_lista_vacia():
    resultados = [
        {"precision": 1.0, "cobertura": 0.5, "f1": 0.6},
        {"precision": 0.5, "cobertura": 0.5, "f1": 0.4},
    ]
    resumen = resumir_metricas(resultados)
    assert resumen["precision_promedio"] == pytest.approx(0.75)
    assert resumen["f1_promedio"] == pytest.approx(0.5)
    assert resumir_metricas([])["f1_promedio"] == 0

def test_limite_conocido_la_negacion_casi_no_baja_el_f1():
    metricas = calcular_metricas("Python no es un lenguaje compilado","Python es un lenguaje compilado")
    assert metricas["f1"] > 0.9
