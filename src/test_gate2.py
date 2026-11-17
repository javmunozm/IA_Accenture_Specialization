import logging

# Dato  de prueba shouldnt appear in any place or log
CORREO = "ana.perez@example.com"
PREGUNTA = "Que pasa si mi conexion tarda demasiado? Mi correo es " + CORREO

# esta parte esta adaptada a este curso
# from langchain_chroma import Chroma
# from langchain_core.embeddings import DeterministicFakeEmbedding

# from src.grafo_supervision import MI_HUELLA, app_despliegue
# from src.indexar_corpus import CORPUS, generar_ids, partir_corpus
# from src.logging_rag import Documento, procesar_consulta
# from src.recuperacion import extraer_citas, formatear_contexto

# RESPUESTA_SIMULADA = "Segun el contexto recuperado, esta es la respuesta [1]."

# def ejecutar_servicio(pregunta):

#     chunks = partir_corpus(CORPUS)
#     vectorstore = Chroma(collection_name="test_gate2",
#                          embedding_function=DeterministicFakeEmbedding(size=768))
#     if not vectorstore.get()["ids"]:
#         vectorstore.add_documents(chunks, ids=generar_ids(chunks))
#     recuperados = vectorstore.as_retriever(search_kwargs={"k": 3}).invoke(pregunta)
#     documentos = [Documento(d.page_content, d.metadata["fuente"]) for d in recuperados]
#     limpios = {d.contenido for d in procesar_consulta(pregunta, documentos)}
#     _, citas = formatear_contexto([d for d in recuperados if d.page_content in limpios])
#     usadas = extraer_citas(RESPUESTA_SIMULADA, citas)
#     fuentes = sorted(set(usadas.values()))
#     respuesta = RESPUESTA_SIMULADA + "\n\nFuentes: " + ", ".join(
#         f"[{n}] {f}" for n, f in sorted(usadas.items()))    
#     return respuesta, fuentes

# def crear_supervision():
#     """Tu grafo del Bloque 32 (src/grafo_supervision.py) y su estado inicial."""
#     return app_despliegue, {"huella_nueva": MI_HUELLA, "aprobado": False}

from langchain_chroma import Chroma
from langchain_core.embeddings import DeterministicFakeEmbedding

from src.grafo_supervision import MI_HUELLA, app_despliegue
from src.servicio_rag import ModeloSimulado, actualizar_indice, responder

def ejecutar_servicio(pregunta):
    vectorstore = Chroma(collection_name="test_gate2",
                         embedding_function=DeterministicFakeEmbedding(size=768))
    estado_indice, _ = actualizar_indice(vectorstore)
    llm = ModeloSimulado("Segun el contexto recuperado, esta es la respuesta [1].")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    resultado = responder(pregunta, retriever, llm, estado_indice)
    return resultado["respuesta"], resultado["fuentes"]

def crear_supervision():
    return app_despliegue, {"huella_nueva": MI_HUELLA, "aprobado": False}

# hasta aca llega lo adaptado

def test_1_pipeline_sin_excepciones():
    respuesta, _ = ejecutar_servicio(PREGUNTA)
    assert respuesta.strip(), "el servicio devolvio una respuesta vacia"


def test_2_respuesta_cita_fuente():
    respuesta, fuentes = ejecutar_servicio(PREGUNTA)
    assert fuentes, "el servicio no devolvio ninguna fuente"
    assert any(f in respuesta for f in fuentes), "la respuesta no menciona su fuente"


def test_3_logs_sin_contenido_crudo(caplog):
    with caplog.at_level(logging.DEBUG):
        ejecutar_servicio(PREGUNTA)
    texto_logs = " ".join(r.getMessage() + " " + str(r.__dict__) for r in caplog.records)
    assert CORREO not in texto_logs, "un dato sensible aparece en los logs"
    assert PREGUNTA not in texto_logs, "la consulta completa aparece en los logs"


def test_4_supervision_pausa_y_reanuda():
    from langgraph.types import Command
    app, entrada = crear_supervision()
    config = {"configurable": {"thread_id": "test-gate2"}}
    pausado = app.invoke(entrada, config=config)
    assert "__interrupt__" in pausado, "el grafo no se detuvo en el punto de supervision"
    final = app.invoke(Command(resume=True), config=config)
    assert "__interrupt__" not in final, "el grafo sigue pausado despues de reanudar"
    assert final["aprobado"] is True, "la decision no quedo registrada"