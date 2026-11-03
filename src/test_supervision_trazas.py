import json
import time

from langchain_core.messages import AIMessage

from src import agente_supervision
from src.agente_completo import construir_agente_con_memoria
from src.agente_supervision import esperar_aprobacion, generar_reembolso, registro_aprobaciones
from src.test_agente_con_herramientas import crear_modelo_falso, pedir_herramienta
from src.trazas_agente import marcar_repeticiones_sospechosas, registrar_traza


def test_esperar_aprobacion_acepta_s(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: " S ")
    assert esperar_aprobacion("¿Aprobar? ", tiempo_limite_segundos=2) is True


def test_esperar_aprobacion_sin_respuesta_a_tiempo_no_aprueba(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: time.sleep(5) or "s")
    inicio = time.monotonic()
    assert esperar_aprobacion("¿Aprobar? ", tiempo_limite_segundos=0.5) is False
    assert time.monotonic() - inicio < 2


def test_generar_reembolso_rechazado_queda_registrado(monkeypatch):
    monkeypatch.setattr(agente_supervision, "esperar_aprobacion", lambda mensaje: False)
    resultado = generar_reembolso.invoke({"numero_pedido": "PED789", "monto": 1500.0})
    assert resultado == "Reembolso no aprobado por el supervisor humano."
    assert registro_aprobaciones[-1]["aprobado"] is False
    assert registro_aprobaciones[-1]["argumentos"] == {"numero_pedido": "PED789", "monto": 1500.0}


def test_agente_registra_traza_del_reembolso_aprobado(monkeypatch, tmp_path):
    monkeypatch.setattr(agente_supervision, "esperar_aprobacion", lambda mensaje: True)
    modelo = crear_modelo_falso(
        pedir_herramienta("generar_reembolso", {"numero_pedido": "P1", "monto": 100.0}),
        AIMessage(content=[{"type": "text", "text": "Reembolso de $100.0 generado para el pedido P1."}]),
    )
    archivo = tmp_path / "trazas_agente.jsonl"
    entrada = "Reembolsa el pedido P1 por $100"
    config = {"configurable": {"session_id": "cliente_456"}}

    resultado = construir_agente_con_memoria(modelo).invoke({"entrada": entrada}, config)
    registrar_traza("cliente_456", entrada, resultado, archivo=str(archivo))

    registro = json.loads(archivo.read_text(encoding="utf-8"))
    assert registro["acciones"][0]["herramienta"] == "generar_reembolso"
    assert registro["acciones"][0]["observacion"] == "Reembolso de $100.0 generado para el pedido P1."
    assert registro["respuesta_final"] == "Reembolso de $100.0 generado para el pedido P1."


def test_marcar_repeticiones_sospechosas(tmp_path, capsys):
    archivo = tmp_path / "trazas_agente.jsonl"
    registros = [
        {"session_id": "cliente_123", "acciones": [{"herramienta": "consultar_estado_ticket"}]},
        {"session_id": "cliente_456", "acciones": [
            {"herramienta": "buscar_solucion_frecuente"},
            {"herramienta": "buscar_solucion_frecuente"},
        ]},
    ]
    archivo.write_text("\n".join(json.dumps(r) for r in registros) + "\n", encoding="utf-8")

    marcar_repeticiones_sospechosas(str(archivo))
    salida = capsys.readouterr().out
    assert "Revisar: cliente_456 uso 'buscar_solucion_frecuente' dos veces seguidas" in salida
    assert "cliente_123" not in salida


def test_marcar_repeticiones_sin_archivo(tmp_path, capsys):
    marcar_repeticiones_sospechosas(str(tmp_path / "no_existe.jsonl"))
    assert "No se encontro" in capsys.readouterr().out