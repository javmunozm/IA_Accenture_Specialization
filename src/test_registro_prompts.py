from src.recuperacion import PROMPT_TEMPLATE
from src.registro_prompts import (
    NOMBRE_PROMPT,
    PROMPT_ACTUAL,
    diff_prompts,
    registro,
    registro_ejemplo,
)

def test_huellas_del_ejemplo_coinciden_con_la_captura():
    huellas = [v["huella"] for v in registro_ejemplo.versiones]
    assert huellas == ["e9567a5cd1bc", "ba2bcb4f4f13"]


def test_mis_versiones_tienen_huellas_distintas():
    v1, v2 = registro.versiones
    assert v1["huella"] != v2["huella"]
    assert len(v2["huella"]) == 12


def test_ultima_devuelve_la_version_mas_reciente():
    assert registro.ultima(NOMBRE_PROMPT) is registro.versiones[-1]
    assert registro.ultima("prompt_que_no_existe") is None


def test_version_actual_es_el_prompt_template_real():
    assert PROMPT_ACTUAL == PROMPT_TEMPLATE


def test_diff_muestra_solo_el_cambio():
    v1, v2 = registro.versiones
    lineas = diff_prompts(v1["texto"], v2["texto"])
    cambios = [l for l in lineas[2:] if l.startswith(("+", "-"))]
    assert cambios == ["-Reponde", "+Responde"]