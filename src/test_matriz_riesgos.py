from src.matriz_riesgos import (
    FILA_MODELO, PUNTOS_DE_SUPERVISION, categoria_riesgo, completar_matriz,
    esta_en_el_limite, mis_riesgos,
)


def test_fila_modelo_coincide_con_la_actividad():
    fila = completar_matriz(FILA_MODELO)[0]
    assert (fila["puntaje"], fila["categoria"], fila["al_limite"]) == (16, "CRITICO", True)


def test_cortes_de_categoria():
    assert [categoria_riesgo(p) for p in (15, 14, 9, 8, 4, 3)] == [
        "CRITICO", "ALTO", "ALTO", "MEDIO", "MEDIO", "BAJO",
    ]


def test_riesgo_de_contraste_no_esta_al_limite():
    assert esta_en_el_limite(1, 1) is False


def test_al_menos_cinco_riesgos_con_valores_validos():
    assert len(mis_riesgos) >= 5
    for r in mis_riesgos:
        assert {"riesgo", "probabilidad", "impacto", "mitigacion"} <= set(r)
        assert type(r["probabilidad"]) is int and 1 <= r["probabilidad"] <= 5
        assert type(r["impacto"]) is int and 1 <= r["impacto"] <= 5


def test_hay_al_menos_un_alto_o_critico():
    categorias = {r["categoria"] for r in completar_matriz(mis_riesgos)}
    assert categorias & {"ALTO", "CRITICO"}


def test_cada_alto_o_critico_tiene_punto_de_supervision():
    for r in completar_matriz(mis_riesgos):
        if r["categoria"] in ("ALTO", "CRITICO"):
            assert PUNTOS_DE_SUPERVISION.get(r["riesgo"]), r["riesgo"]


def test_al_menos_dos_mitigaciones_apuntan_a_un_bloque():
    assert sum("Bloque" in r["mitigacion"] for r in mis_riesgos) >= 2