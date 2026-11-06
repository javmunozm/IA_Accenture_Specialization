from unittest.mock import MagicMock

from langchain_core.documents import Document

from src.evaluacion_recuperacion import (
    casos_evaluacion,
    evaluar_recuperacion,
    precision_at_k,
    promediar,
    recall_at_k,
)
from src.indexar_corpus import CORPUS, generar_ids, partir_corpus


def test_metricas_del_ejemplo_de_la_leccion():
    ids_relevantes = {"doc0"}
    ids_recuperados = ["doc2", "doc0", "doc4"]
    assert precision_at_k(ids_recuperados, ids_relevantes) == 1 / 3
    assert recall_at_k(ids_recuperados, ids_relevantes) == 1.0


def test_casos_borde_no_lanzan_zero_division():
    assert precision_at_k([], {"doc0"}) == 0.0
    assert recall_at_k(["doc0"], set()) is None
    assert promediar([None, None]) == 0.0
    assert promediar([1.0, None, 0.0]) == 0.5


def test_evaluar_recuperacion_con_resultados_fijos_de_la_leccion():
    casos = [
        {"pregunta": "que hace el cliente si una llamada tarda demasiado", "ids_relevantes": {"doc0"}},
        {"pregunta": "que pasa si la clave de api es invalida", "ids_relevantes": {"doc1"}},
        {"pregunta": "como se calcula el costo de una llamada", "ids_relevantes": {"doc2"}},
        {"pregunta": "como decide el agente que herramienta usar", "ids_relevantes": {"doc3"}},
    ]
    recuperados = {
        casos[0]["pregunta"]: ["doc0", "doc4", "doc2"],
        casos[1]["pregunta"]: ["doc2", "doc4", "doc3"],
        casos[2]["pregunta"]: ["doc2", "doc0", "doc4"],
        casos[3]["pregunta"]: ["doc4", "doc3", "doc1"],
    }
    retriever = MagicMock()
    retriever.invoke.side_effect = lambda pregunta: [
        Document(page_content="x", id=i) for i in recuperados[pregunta]
    ]
    resultados, p_prom, r_prom = evaluar_recuperacion(retriever, casos, k=3)
    assert [r["recall"] for r in resultados] == [1.0, 0.0, 1.0, 1.0]
    assert round(p_prom, 3) == 0.25
    assert r_prom == 0.75


def test_etiquetas_usan_ids_que_existen_en_el_indice():
    ids_del_indice = set(generar_ids(partir_corpus(CORPUS)))
    assert 8 <= len(casos_evaluacion) <= 15
    for caso in casos_evaluacion:
        assert caso["ids_relevantes"] <= ids_del_indice, caso["pregunta"]