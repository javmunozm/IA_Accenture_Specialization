import pytest
from langgraph.types import Command

from src.grafo_supervision import MI_HUELLA, app_despliegue, nuevo_thread_id, resolver
from src.registro_prompts import NOMBRE_PROMPT, registro

def iniciar():
    config = {"configurable": {"thread_id": nuevo_thread_id("prueba")}}
    resultado = app_despliegue.invoke({"huella_nueva": MI_HUELLA, "aprobado": False}, config=config)
    return config, resultado

def test_mi_huella_es_la_ultima_del_registro():
    assert MI_HUELLA == registro.ultima(NOMBRE_PROMPT)["huella"]

def test_sin_reanudar_queda_interrumpido():
    config, resultado = iniciar()
    assert "__interrupt__" in resultado
    snapshot = app_despliegue.get_state(config)
    assert snapshot.next == ("supervisar",)
    assert snapshot.interrupts[0].value == {
        "motivo": "aprobar nueva version de prompt en produccion",
        "huella_propuesta": MI_HUELLA,
    }

def test_aprobar_activa_la_version(capsys):
    config, _ = iniciar()
    resultado = app_despliegue.invoke(Command(resume=True), config=config)
    assert resultado == {"huella_nueva": MI_HUELLA, "aprobado": True}
    assert f"version {MI_HUELLA} activada" in capsys.readouterr().out

def test_rechazar_mantiene_la_anterior(capsys):
    config, _ = iniciar()
    resultado = app_despliegue.invoke(Command(resume=False), config=config)
    assert resultado == {"huella_nueva": MI_HUELLA, "aprobado": False}
    assert "rechazada, se mantiene la anterior" in capsys.readouterr().out

def test_segunda_aprobacion_lanza_value_error():
    config, _ = iniciar()
    resolver(app_despliegue, config, True)
    with pytest.raises(ValueError, match="ninguna aprobacion pendiente"):
        resolver(app_despliegue, config, True)