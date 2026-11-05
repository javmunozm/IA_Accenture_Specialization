from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from src.recuperacion import construir_prompt, extraer_citas, formatear_contexto

CHUNKS_EJEMPLO = [
    Document(
        page_content="El cliente reintenta hasta 3 veces ante un TimeoutError.",
        metadata={"fuente": "doc0.md"},
    ),
    Document(
        page_content="El costo de cada llamada se calcula a partir de totalTokenCount.",
        metadata={"fuente": "doc2.md"},
    ),
]


def test_formatear_contexto_numera_desde_1_y_mapea_fuentes():
    contexto, citas = formatear_contexto(CHUNKS_EJEMPLO)
    assert citas == {1: "doc0.md", 2: "doc2.md"}
    assert contexto.startswith("[1] El cliente reintenta")
    assert "\n\n[2] El costo" in contexto


def test_formatear_contexto_sin_fuente_usa_desconocida():
    _, citas = formatear_contexto([Document(page_content="texto suelto")])
    assert citas == {1: "desconocida"}


def test_extraer_citas_marca_las_inventadas():
    citas = {1: "doc0.md", 2: "doc2.md"}
    respuesta = "Reintenta 3 veces [1]. El costo usa tokens [2] y [99]."
    assert extraer_citas(respuesta, citas) == {
        1: "doc0.md",
        2: "doc2.md",
        99: "Cita invalida / no encontrada",
    }


def test_construir_prompt_usa_la_pregunta_exacta_y_k_citas():
    vectorstore = MagicMock()
    vectorstore.as_retriever.return_value.invoke.return_value = CHUNKS_EJEMPLO
    with patch("src.recuperacion.cargar_vectorstore", return_value=vectorstore):
        prompt, citas = construir_prompt("Que hace el cliente?", "vectorstore", k=2)
    vectorstore.as_retriever.assert_called_once_with(search_kwargs={"k": 2})
    assert "Pregunta: Que hace el cliente?" in prompt
    assert list(citas) == [1, 2]