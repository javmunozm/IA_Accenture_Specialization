from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from src.agente_con_herramientas import (
    buscar_solucion_frecuente,
    consultar_estado_ticket,
    construir_agente,
    herramientas_usadas,
)


class ModeloFalso(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self

def crear_modelo_falso(*respuestas):
    return ModeloFalso(messages=iter(respuestas), disable_streaming=True)

def pedir_herramienta(nombre, argumentos):
    return AIMessage(
        content="",
        tool_calls =[{"name": nombre, "args": argumentos, "id": "llamada_1"}],
    )

def test_herramientas_responden_sin_modelo():
    assert consultar_estado_ticket.invoke({"numero_ticket": "TK1001"}) == "en revision por el equipo tecnico"
    assert "No se encontro" in consultar_estado_ticket.invoke({"numero_ticket": "TK9999"})
    assert "Perfil > Seguridad" in buscar_solucion_frecuente.invoke({"problema": "olvide mi contraseña"})

def test_agente_elige_consultar_estado_ticket():
    modelo = crear_modelo_falso(
        pedir_herramienta("consultar_estado_ticket", {"numero_ticket": "TK1001"}),
        AIMessage(content=[{"type": "text", "text": "Tu ticket TK1001 esta en revision."}])
    )
    resultado = construir_agente(modelo).invoke({"entrada": "¿Como va mi ticket TK1001?"})
    assert herramientas_usadas(resultado) == ["consultar_estado_ticket"]
    assert resultado["intermediate_steps"][0][1] == "en revision por el equipo tecnico"
    assert resultado["output"] == "Tu ticket TK1001 esta en revision."

def test_agente_no_usa_herramienta_para_pregunta_general():
    modelo = crear_modelo_falso(AIMessage(content="Puedes escribirnos a soporte desde la app."))
    resultado = construir_agente(modelo).invoke({"entrada": "¿Como puedo contactar a soporte"})
    assert resultado["intermediate_steps"] == []
