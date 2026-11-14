import uuid
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

HUELLA_EJEMPLO = "ba2bcb4f4f13"  # la huella del ejemplo del Prompt viejo
MI_HUELLA = "849809fdf663"       # la huella del ultimo


class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool

def proponer(estado: EstadoDespliegue):
    return {}

def supervisar(estado: EstadoDespliegue):
    decision = interrupt({
        "motivo": "aprobar nueva version de prompt en produccion",
        "huella_propuesta": estado["huella_nueva"],
    })
    return {"aprobado": decision}

def aplicar(estado: EstadoDespliegue):
    if estado["aprobado"]:
        print("version", estado["huella_nueva"], "activada")
    else:
        print("version", estado["huella_nueva"], "rechazada, se mantiene la anterior")
    return {}

grafo = StateGraph(EstadoDespliegue)
grafo.add_node("proponer", proponer)
grafo.add_node("supervisar", supervisar)
grafo.add_node("aplicar", aplicar)
grafo.add_edge(START, "proponer")
grafo.add_edge("proponer", "supervisar")
grafo.add_edge("supervisar", "aplicar")
grafo.add_edge("aplicar", END)

app_despliegue = grafo.compile(checkpointer=InMemorySaver())


def nuevo_thread_id(prefijo="despliegue"):
    return f"{prefijo}-{uuid.uuid4().hex[:8]}"

def resolver(app, config, aprobar):
    snapshot = app.get_state(config)
    if not snapshot.next:
        raise ValueError("este thread_id no tiene ninguna aprobacion pendiente")
    return app.invoke(Command(resume=aprobar), config=config)


def imprimir_titulo(texto):
    print("=" * 62)
    print(texto)
    print("=" * 62)

def main():
    imprimir_titulo("EJEMPLO DE REFERENCIA (huella del ejemplo del Paso 1)")
    huella = HUELLA_EJEMPLO

    config_ej = {"configurable": {"thread_id": "ejemplo-1"}}
    resultado = app_despliegue.invoke({"huella_nueva": huella, "aprobado": False}, config=config_ej)
    print("1) tras invocar:", resultado)
    print("2) pendiente:", app_despliegue.get_state(config_ej).interrupts[0].value)
    resultado = app_despliegue.invoke(Command(resume=True), config=config_ej)
    print("3) tras aprobar:", resultado)

    config_ej2 = {"configurable": {"thread_id": "ejemplo-2"}}
    app_despliegue.invoke({"huella_nueva": huella, "aprobado": False}, config=config_ej2)
    resultado = app_despliegue.invoke(Command(resume=False), config=config_ej2)
    print("4) tras rechazar:", resultado)

    imprimir_titulo("PASO 2: punto de supervision antes de activar la version nueva")
    config = {"configurable": {"thread_id": "mi-despliegue-1"}}
    resultado = app_despliegue.invoke({"huella_nueva": MI_HUELLA, "aprobado": False}, config=config)
    print("interrupcion detectada:", "__interrupt__" in resultado)
    print("pendiente:", app_despliegue.get_state(config).interrupts[0].value)
    resolver(app_despliegue, config, True)

    config2 = {"configurable": {"thread_id": "mi-despliegue-2"}}
    app_despliegue.invoke({"huella_nueva": MI_HUELLA, "aprobado": False}, config=config2)
    resolver(app_despliegue, config2, False)

    try:
        resolver(app_despliegue, config, True)
    except ValueError as error:
        print("segunda aprobacion bloqueada:", error)


if __name__ == "__main__":
    main()