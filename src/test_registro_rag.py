import json
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from src.preflight import preflight_check
from src.registro_rag import calcular_costo_usd, guardar_registro, medir, registrar_consulta


def test_medir_guarda_la_duracion_de_la_etapa():
    tiempos = {}
    with medir(tiempos, "etapa"):
        pass
    assert list(tiempos) == ["etapa"]
    assert tiempos["etapa"] >= 0


def test_calcular_costo_usd_con_tokens_reales():
    tokens = {"input_tokens": 1_000_000, "output_tokens": 1_000_000, "total_tokens": 2_000_000}
    assert calcular_costo_usd(tokens) == 2.80
    assert calcular_costo_usd(None) is None


def test_registrar_consulta_tiene_las_claves_y_tres_etapas():
    vectorstore = MagicMock()
    vectorstore.embeddings.embed_query.return_value = [0.1, 0.2]
    vectorstore.similarity_search_by_vector.return_value = [
        Document(page_content="El cliente reintenta.", metadata={"fuente": "reintentos"})
    ]
    modelo = MagicMock()
    modelo.invoke.return_value = AIMessage(
        content="Reintenta [1].",
        usage_metadata={"input_tokens": 150, "output_tokens": 38, "total_tokens": 188},
    )
    with patch("src.registro_rag.cargar_vectorstore", return_value=vectorstore), \
         patch("src.registro_rag.construir_modelo", return_value=modelo):
        registro = registrar_consulta("que hace el cliente?", "vectorstore", k=2)

    assert list(registro) == [
        "timestamp", "pregunta", "k", "tiempos_ms", "tiempo_total_ms", "tokens", "costo_usd"
    ]
    assert list(registro["tiempos_ms"]) == ["embed_query", "busqueda_vectorial", "generacion"]
    assert registro["k"] == 2
    assert registro["tokens"]["input_tokens"] == 150
    vectorstore.similarity_search_by_vector.assert_called_once_with([0.1, 0.2], k=2)


def test_guardar_registro_agrega_una_linea_json_por_corrida(tmp_path):
    ruta = tmp_path / "registros.jsonl"
    guardar_registro({"k": 3}, ruta)
    guardar_registro({"k": 6}, ruta)
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    assert [json.loads(linea)["k"] for linea in lineas] == [3, 6]


def test_preflight_detecta_carpeta_faltante_y_gitignore(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text(".env\n", encoding="utf-8")
    problemas = preflight_check(str(tmp_path / "no_existe") + "/", str(gitignore))
    assert len(problemas) == 2