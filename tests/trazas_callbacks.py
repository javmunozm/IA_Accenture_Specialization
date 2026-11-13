import json
import logging
import sys
from typing import List

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.documents import Document
from langchain_core.language_models.fake import FakeListLLM
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableLambda

logger = logging.getLogger("trazas_pipeline")
logger.setLevel(logging.INFO)
h = logging.StreamHandler(sys.stdout)
h.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [h]
logger.propagate = False

def corto(identificador):
    return str(identificador)[-6:] if identificador else None


class HandlerDeTrazas(BaseCallbackHandler):
    def on_retriever_start(self, serialized, query, *, run_id,
                           parent_run_id=None, tags=None, metadata=None,
                           **kwargs):
        logger.info(json.dumps({"evento": "retriever_start", "query_len": len(query),
                                "run_id": corto(run_id), "parent_run_id": corto(parent_run_id)}))

    def on_retriever_end(self, documents, *, run_id, parent_run_id=None, **kwargs):
        logger.info(json.dumps({"evento": "retriever_end", "n_documentos": len(documents),
                                "run_id": corto(run_id), "parent_run_id": corto(parent_run_id)}))

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id=None,
                     tags=None, metadata=None, **kwargs):
        logger.info(json.dumps({"evento": "llm_start", "n_prompts": len(prompts),
                                "run_id": corto(run_id), "parent_run_id": corto(parent_run_id)}))

    def on_llm_end(self, response, *, run_id, parent_run_id=None, tags=None,
                   **kwargs):
        texto = response.generations[0][0].text
        logger.info(json.dumps({"evento": "llm_end", "chars_respuesta": len(texto),
                                "run_id": corto(run_id), "parent_run_id": corto(parent_run_id)}))

class RetrieverFijo(BaseRetriever):
    documentos: List[Document] = []

    def _get_relevant_documents(self, query, *, run_manager=None):
        return self.documentos

def armor_prompt(documentos):
    return f"Contexto: {documentos[0].page_content}"

def titulo(texto):
    print("=" * 66)
    print(texto)
    print("=" * 66)

docs = [Document(page_content="Politica de devoluciones: 30 dias.",
                 metadata={"fuente": "manual.pdf"})]
retriever = RetrieverFijo(documentos=docs)
prompt = RunnableLambda(armor_prompt)
llm = FakeListLLM(responses=["Esta es una respuesta simulada, sin llamar a ninguna API real."])
cadena = retriever | prompt | llm

titulo("PASO 1: UNA sola cadena (retriever | prompt | llm), UN solo handler")
respuesta = cadena.invoke("¿Cuál es la política de devoluciones?",
                          config={"callbacks": [HandlerDeTrazas()]})

print()
titulo("PASO 2: resultado")
print("respuesta:", respuesta)
print("(el parent_run_id de cada paso apunta a la cadena que los contiene)")