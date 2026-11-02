import pytest
from langchain_core.messages import AIMessage
from pydantic import ValidationError

from src.agente_completo import (
    cerrar_sesion,
    consultar_ticket_detallado,
    construir_agente_con_memoria,
    historiales,
    obtener_historial,
)
from src.test_agente_con_herramientas import crear_modelo_falso

def test_herramienta_usa_incluir_historial_y_nombre_explicito():
    assert consultar_ticket_detallado.name == "consultar_ticket_con_historial"
    solo_actual = consultar_ticket_detallado.invoke({"numero_ticket": "TK1001"})
    con_historial = consultar_ticket_detallado.invoke({"numero_ticket": "TK1001", "incluir_historial": True})
    assert solo_actual == "en revision por el equipo tecnico"
    assert "historial:" in con_historial

def test_args_schema_rechaza_tipo_invalido():
    with pytest.raises(ValidationError):
        consultar_ticket_detallado.invoke({"numero_ticket": "TK1001", "incluir_historial": "tal vez"})

def test_memoria_guarda_turnos_y_no_mezcla_sesiones():
    historiales.clear()
    modelo = crear_modelo_falso(
        AIMessage(content=[{"type": "text", "text": "Anotado, ticket TK1001."}]),
        AIMessage(content=[{"type": "text", "text": "sigue en revision."}]),
        AIMessage(content=[{"type": "text", "text": "No mencionaste ningun ticket todavia."}]),
    )

    agente_con_memoria = construir_agente_con_memoria(modelo)
    config_cliente_1 = {"configurable": {"session_id": "cliente_1"}}
    config_cliente_2 = {"configurable": {"session_id": "cliente_2"}}

    agente_con_memoria.invoke({"entrada": "Pregunto por el ticket TK1001."}, config_cliente_1)
    agente_con_memoria.invoke({"entrada": "¿Y como va?"}, config_cliente_1)
    agente_con_memoria.invoke({"entrada": "¿De que ticket te pregunte?"}, config_cliente_2)


    assert len(obtener_historial("cliente_1").messages) == 4
    assert len(obtener_historial("cliente_2").messages) == 2
    cerrar_sesion("cliente_1")
    assert "cliente_1" not in historiales
