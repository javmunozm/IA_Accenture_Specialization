from src.decision import generar_esqueleto_decision, recomendar_estrategia

# bloque 29
CASO_EMPATE = {
    "informacion_cambia_seguido": False,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": True,
    "presupuesto_limitado_o_iterar_rapido": False,
    "necesita_multiples_variantes": False,
}

# bloque 29 nuevamente...bot vs cliente
CASO_RAG = {
    "informacion_cambia_seguido": True,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": False,
    "presupuesto_limitado_o_iterar_rapido": True,
    "necesita_multiples_variantes": False,
}

SECCIONES = [
    "## 1. El problema",
    "## 2. Resultado del metodo de decision",
    "## 3. Tecnica elegida y por que",
    "## 4. Que necesitarias para ejecutarla",
]


def test_empate_reporta_las_dos_tecnicas():
    puntos, ganadoras = recomendar_estrategia(CASO_EMPATE)
    assert puntos == {"RAG": 0, "Fine-tuning completo": 3, "PEFT": 3}
    assert ganadoras == ["Fine-tuning completo", "PEFT"]


def test_ganador_claro():
    puntos, ganadoras = recomendar_estrategia(CASO_RAG)
    assert puntos == {"RAG": 5, "Fine-tuning completo": 1, "PEFT": 3}
    assert ganadoras == ["RAG"]


def test_todo_false_es_empate_a_tres():
    _, ganadoras = recomendar_estrategia({clave: False for clave in CASO_RAG})
    assert ganadoras == ["RAG", "Fine-tuning completo", "PEFT"]


def test_cada_respuesta_cambia_el_empate():
    for clave in CASO_EMPATE:
        variante = dict(CASO_EMPATE)
        variante[clave] = not variante[clave]
        _, ganadoras = recomendar_estrategia(variante)
        assert set(ganadoras) != {"Fine-tuning completo", "PEFT"}, clave


def test_esqueleto_tiene_las_cuatro_secciones_en_orden():
    puntos, ganadoras = recomendar_estrategia(CASO_EMPATE)
    texto = generar_esqueleto_decision("Problema de prueba.", puntos, ganadoras)
    posiciones = [texto.index(seccion) for seccion in SECCIONES]
    assert posiciones == sorted(posiciones)


def test_esqueleto_declara_el_empate():
    puntos, ganadoras = recomendar_estrategia(CASO_EMPATE)
    texto = generar_esqueleto_decision("Problema de prueba.", puntos, ganadoras)
    assert "**Empate entre: Fine-tuning completo, PEFT**" in texto
    assert "el puntaje no resolvio el empate solo" in texto


def test_esqueleto_sin_empate_nombra_la_ganadora():
    puntos, ganadoras = recomendar_estrategia(CASO_RAG)
    texto = generar_esqueleto_decision("Problema de prueba.", puntos, ganadoras)
    assert "Empate" not in texto
    assert "[COMPLETAR: por que RAG responde mejor a este caso]" in texto


def test_esqueleto_ordena_por_puntaje():
    puntos, ganadoras = recomendar_estrategia(CASO_RAG)
    texto = generar_esqueleto_decision("Problema de prueba.", puntos, ganadoras)
    rag = texto.index("- RAG: 5 puntos")
    peft = texto.index("- PEFT: 3 puntos")
    completo = texto.index("- Fine-tuning completo: 1 puntos")
    assert rag < peft < completo