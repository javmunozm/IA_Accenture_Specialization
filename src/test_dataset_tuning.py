import json

from google.genai import types

from src.dataset_tuning import (
    CLAVE_BALANCE,
    CLAVES_ESPERADAS,
    EJEMPLOS_RAW,
    chequear_balance,
    construir_examples,
    validar_dataset,
)


def ejemplo(texto, output):
    return types.TuningExample(text_input=texto, output=output)


def test_el_dataset_tiene_al_menos_10_ejemplos_y_mas_de_una_categoria():
    assert len(EJEMPLOS_RAW) >= 10
    assert len(chequear_balance(EJEMPLOS_RAW, CLAVE_BALANCE)) > 1


def test_chequear_balance_cuenta_por_categoria():
    raw = [("a", {"intencion": "x"}), ("b", {"intencion": "x"}), ("c", {"intencion": "y"})]
    assert dict(chequear_balance(raw, "intencion")) == {"x": 2, "y": 1}


def test_construir_examples_genera_outputs_en_json_valido():
    examples = construir_examples([("hola", {"intencion": "acceso", "prioridad": "baja"})])
    assert examples[0].text_input == "hola"
    assert json.loads(examples[0].output) == {"intencion": "acceso", "prioridad": "baja"}


def test_tu_dataset_pasa_la_validacion_sin_problemas():
    examples = construir_examples(EJEMPLOS_RAW)
    assert validar_dataset(examples, CLAVES_ESPERADAS) == []


def test_validar_detecta_text_input_vacio():
    problemas = validar_dataset([ejemplo("  ", '{"intencion": "acceso"}')], ("intencion",))
    assert problemas == ["ejemplo 0: text_input vacio"]


def test_validar_detecta_output_vacio():
    problemas = validar_dataset([ejemplo("hola", "")], ("intencion",))
    assert problemas == ["ejemplo 0: output vacio"]


def test_validar_detecta_text_input_duplicado():
    examples = [ejemplo("hola", '{"intencion": "a"}'), ejemplo("hola", '{"intencion": "b"}')]
    assert validar_dataset(examples, ("intencion",)) == ["ejemplo 1: text_input duplicado"]


def test_validar_detecta_output_con_comillas_simples():
    problemas = validar_dataset([ejemplo("hola", "{'intencion': 'acceso'}")], ("intencion",))
    assert problemas == ["ejemplo 0: output no es JSON valido"]


def test_validar_detecta_clave_faltante():
    problemas = validar_dataset([ejemplo("hola", '{"intencion": "acceso"}')], ("intencion", "prioridad"))
    assert problemas == ['ejemplo 0: output no tiene la clave "prioridad"']


def test_validar_reporta_todos_los_problemas_de_un_ejemplo():
    problemas = validar_dataset([ejemplo("", '{"intencion": "acceso"}')], ("intencion", "prioridad"))
    assert problemas == [
        "ejemplo 0: text_input vacio",
        'ejemplo 0: output no tiene la clave "prioridad"',
    ]