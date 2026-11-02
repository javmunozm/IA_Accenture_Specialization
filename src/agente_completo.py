import time

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from  langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.agente_con_herramientas import buscar_solucion_frecuente, construir_agente, texto_salida
from src.cadena_tres_pasos import construir_modelo

PAUSA_SEGUNDOS = 2

TICKETS_DETALLE = {
    "TK1001": {
        "actual": "en revision por el equipo tecnico",
        "historial": ["recibido", "asignado a soporte tecnico", "en revision"],
    },
    "TK1002": {
        "actual": "resuelto",
        "historial": ["recibido", "resuelto"],
    },
}


class ArgumentosConsultaTicket(BaseModel):
    numero_ticket: str = Field(
        description="Numero del ticket de soporte, por ejemplo 'TK1001'."
    )
    incluir_historial: bool = Field(
        default=False,
        description="Si es True, incluye el historial completo de estados, no solo el actual.",
    )

@tool("consultar_ticket_con_historial", args_schema=ArgumentosConsultaTicket)
def consultar_ticket_detallado(numero_ticket: str, incluir_historial: bool = False) -> str:
    """Consulta el estado de un ticket de soporte, con la opcion de incluir el historial. Usar cuando el usuario pregunte estado de su ticket"""
    ticket = TICKETS_DETALLE.get(numero_ticket.strip().upper())
    if ticket is None:
        return f"No se encontro un ticket con el numero {numero_ticket}."
    if not  incluir_historial:
        return ticket["actual"]
    historial = ", ".join(ticket["historial"])
    return f"{ticket['actual']} (historial: {historial})"


#executor and agent
HERRAMIENTAS = [consultar_ticket_detallado, buscar_solucion_frecuente]

PROMPT_AGENTE_CON_HISTORIAL = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente de  soporte que responde preguntas "
        "usando las herramientas disponibles cuando "
        "las necesites.",
    ),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])


historiales = {}

def obtener_historial(session_id: str):
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]

def cerrar_sesion(session_id: str):
    historiales.pop(session_id, None)


def construir_agente_con_memoria(modelo, herramientas=HERRAMIENTAS):
    ejecutor_agente = construir_agente(modelo, herramientas, PROMPT_AGENTE_CON_HISTORIAL)
    return RunnableWithMessageHistory(
        ejecutor_agente,
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
    )

if __name__ == "__main__":
    try:
        agente_con_memoria = construir_agente_con_memoria(construir_modelo())

        config = {"configurable": {"session_id": "cliente_456"}}
        for entrada in [
            "¿Cual es el estado del ticket TK1001, con su historial?",
            "¿Y ese mismo ticket ya fue resuelto",
        ]:
            resultado = agente_con_memoria.invoke({"entrada": entrada}, config)
            print(f"> {entrada}\n{texto_salida(resultado['output'])}\n")
            time.sleep(PAUSA_SEGUNDOS)

        #Dos sesiones diferentes no comparten historial
        config_cliente_1 = {"configurable": {"session_id": "cliente_1"}}
        config_cliente_2 = {"configurable": {"session_id": "cliente_2"}}
        agente_con_memoria.invoke({"entrada": "Estoy preguntando por el ticket TK1001."}, config_cliente_1)
        time.sleep(PAUSA_SEGUNDOS)
        resultado = agente_con_memoria.invoke({"entrada": "¿De que ticket te pregunte?"}, config_cliente_2)
        print(f"> cliente_2: ¿De que ticket te pregunte?\n{texto_salida(resultado['output'])}\n")
        for sesion in ["cliente_456", "cliente_1", "cliente_2"]:
            print(sesion, "->", len(obtener_historial(sesion).messages), "mensajes")
    except Exception as error:
        print("no se pudo completar la operacion:", error)
