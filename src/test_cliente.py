from unittest.mock import Mock, patch

import pytest

import cliente
from cliente import con_reintento, consultar_modelo, enviar_peticion, registrar_costo

URL, HEADERS, BODY = "https://ejemplo.test", {}, {"contents": []}
POST = "src.consumir_gemini.requests.post"

@pytest.fixture(autouse=True)
def entorno_limpio(monkeypatch):
    cliente.costo_total_sesion = 0
    monkeypatch.setenv("GEMINI_API_KEY","clave_de_prueba")
    yield

#enviat_peticion

def test_enviar_peticion_credencial_invalida():
    with patch(POST, return_value=Mock(status_code=401)):
        with pytest.raises(ValueError):
            enviar_peticion(URL, HEADERS, BODY)


def test_enviar_peticion_bad_request():
    with patch(POST, return_value=Mock(status_code=400)):
        with pytest.raises(ValueError):
            enviar_peticion(URL, HEADERS, BODY)


def test_enviar_peticion_limite_de_uso():
    with patch(POST, return_value=Mock(status_code=429)):
        with pytest.raises(TimeoutError):
            enviar_peticion(URL, HEADERS, BODY)


def test_enviar_peticion_exito():
    falsa = Mock(status_code=200)
    falsa.json.return_value = {"texto":"respuesta simulada"}
    with patch(POST, return_value=falsa):
        assert enviar_peticion(URL, HEADERS, BODY) == {"texto":"respuesta simulada"}


def test_enviar_peticion_modelo_no_existe():
    with patch(POST, return_value=Mock(status_code=404)):
        with pytest.raises(FileNotFoundError):
            enviar_peticion(URL, HEADERS, BODY)


def test_enviar_peticion_error_del_proveedor():
    with patch(POST, return_value=Mock(status_code=503)):
        with pytest.raises(TimeoutError):
            enviar_peticion(URL, HEADERS, BODY)


# con_reintento retry

def test_con_reintento_reintenta_y_espera():
    llamadas = {"n": 0}

    def falla_una_vez():
        llamadas["n"] += 1
        if llamadas["n"] == 1:
            raise TimeoutError("simulado")
        return "ok"

    with patch("cliente.time.sleep") as mock_sleep:
        assert con_reintento(falla_una_vez) == "ok"
    mock_sleep.assert_called_once()


def test_con_reintento_agota_intentos():
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep") as mock_sleep:
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3)
    assert mock_sleep.call_count == 2


def test_con_reintento_no_reintenta_value_error():
    llamadas = {"n": 0}

    def credencial_mala():
        llamadas["n"] += 1
        raise ValueError("simulado")

    with patch("cliente.time.sleep") as mock_sleep:
        with pytest.raises(ValueError):
            con_reintento(credencial_mala)
    assert llamadas["n"] == 1
    mock_sleep.assert_not_called()


# registrar_costo

def test_registrar_costo_acumula():
    respuesta_falsa = {"usageMetadata": {"totalTokenCount": 1000}}
    costo = registrar_costo(respuesta_falsa)
    registrar_costo(respuesta_falsa)
    assert costo == cliente.COSTO_POR_1000_TOKENS
    assert cliente.costo_total_sesion == pytest.approx(2 * cliente.COSTO_POR_1000_TOKENS)


# consultar_modelo

def test_consultar_modelo_flujo_exitoso():
    respuesta_falsa = {
        "candidates": [{"content": {"parts": [{"text": "Santiago"}]}}],
        "usageMetadata": {"totalTokenCount": 500},
    }
    with patch("cliente.enviar_peticion", return_value=respuesta_falsa):
        assert consultar_modelo("¿Capital de Chile?") == "Santiago"
    assert cliente.costo_total_sesion == pytest.approx(0.5 * cliente.COSTO_POR_1000_TOKENS)


def test_consultar_modelo_convierte_error():
    with patch("cliente.con_reintento", side_effect=TimeoutError("simulado")):
        with pytest.raises(RuntimeError):
            consultar_modelo("pregunta de prueba")


def test_consultar_modelo_propaga_value_error():
    with patch("cliente.con_reintento", side_effect=ValueError("simulado")):
        with pytest.raises(ValueError):
            consultar_modelo("pregunta de prueba")


def test_consultar_modelo_reintenta_ante_503():
    exitosa = Mock(status_code=200)
    exitosa.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "ok"}]}}],
        "usageMetadata": {"totalTokenCount": 10},
    }
    with patch(POST, side_effect=[Mock(status_code=503), exitosa]), patch("cliente.time.sleep") as mock_sleep:
        assert consultar_modelo("pregunta de prueba") == "ok"
    mock_sleep.assert_called_once()