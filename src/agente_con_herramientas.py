from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import tool
import time

from src.cadena_tres_pasos import construir_modelo

PAUSA_SEGUNDOS = 2

TICKETS = {
    "TK1001": "en revision por el equipo tecnico",
    "TK1002": "resuelto",
}

SOLUCIONES = {
    "contraseña": "Para cambiar tu contraseña, entra a Perfil > Seguridad > Cambiar contraseña.",
    "imagen": "Si la app se cierra al subir una imagen, actualizala y prueba con un archivo de menos de 10MB.",
    "factura": "Las facturas se descargan desde el Perfil > Pagos > Historial.",
}

PROMPT_AGENTE = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente de soporte que responde preguntas "
        "usando las herramientas disponibles cuando "
        "las necesites.",
    ),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

@tool
def consultar_estado_ticket(numero_ticket: str) -> str:
    """Consulta el estado de un ticket de soporte a partir de su numero (por ejemplo TK1001). Usar cuando el usuario pregunta cómo va su ticket o su reclamo."""
    try:
        return TICKETS[numero_ticket.strip().upper()]
    except KeyError:
        return f"No se encontro un ticket con el numero {numero_ticket}."

@tool
def buscar_solucion_frecuente(problema: str) -> str:
    """Busca la solucion a un problema frecuente de la app (contraseña, imagenes, facturas). Usar cuando el usuario pregunta como resolver un problema o como hacer algo dentro de la app."""
    for clave, solucion in SOLUCIONES.items():
        if clave in problema.lower():
            return solucion
    return "No hay una solucion registrada para ese problema."

HERRAMIENTAS = [consultar_estado_ticket, buscar_solucion_frecuente]


def texto_salida(salida):
    if isinstance(salida, str):
        return salida
    return "".join(
        bloque.get("text","") if isinstance(bloque, dict) else str(bloque)
        for bloque in salida
    )

def salida_como_texto(resultado):
    return {**resultado, "output": texto_salida(resultado["output"])}

def construir_agente(modelo, herraminetas=HERRAMIENTAS, prompt=PROMPT_AGENTE):
    agente =create_tool_calling_agent(modelo, herraminetas, prompt)
    ejecutor_agente = AgentExecutor(
        agent=agente,
        tools=herraminetas,
        verbose=True,
        return_intermediate_steps=True,
    )
    return ejecutor_agente | RunnableLambda(salida_como_texto)

def herramientas_usadas(resultado):
    return [accion.tool for accion, _ in resultado["intermediate_steps"]]



if __name__ == "__main__":
    CASOS = [
        ("¿Como va mi ticket TK1001?", ["consultar_estado_ticket"]),
        ("¿Como cambio mi contraseña?", ["buscar_solucion_frecuente"]),
        ("¿Como puedo contactar a soporte?", []),
    ]
    try:
        ejecutor_agente = construir_agente(construir_modelo())
        for entrada, esperadas in CASOS:
            resultado = ejecutor_agente.invoke({"entrada": entrada})
            usadas = herramientas_usadas(resultado)
            estado = "OK" if usadas == esperadas else "REVISAR"
            print(f"[{estado}] {entrada} -> herramientas: {usadas}")
            print(resultado["output"], "\n")
            time.sleep(PAUSA_SEGUNDOS)
    except Exception as error:
        print("No se pudo completar la operacion:", error)
