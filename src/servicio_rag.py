import contextvars
import json
import logging
import sys
import uuid

from langchain_core.messages import AIMessage

from src.grafo_supervision import MI_HUELLA, app_despliegue, nuevo_thread_id, resolver
from src.indexar_corpus import (
    CARPETA_VECTORSTORE, 
    CORPUS, 
    cargar_vectorstore,
    con_reintentos,
    generar_ids,
    partir_corpus,
)

from src.logging_rag import detectar_inyeccion
from src.recuperacion import PROMPT_TEMPLATE, extraer_citas, formatear_contexto
from src.registro_rag import calcular_costo_usd, medir

K = 3
SIN_CONTEXTO = "No tengo informacion suficiente y verificada para responder esto."
PREGUNTA_DEMO = "Que pasa si mi conexion tarda demasiado?"

trace_id_var = contextvars.ContextVar("trace_id", default=None)
logger = logging.getLogger("servicio_rag")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [handler]
logger.propagate = False

def evento(auditoria, nombre, **campos):
    registro = {"evento": nombre, "trace_id": trace_id_var.get(),**campos}
    logger.info(json.dumps(registro, ensure_ascii=False))
    auditoria.append(registro)

#indice con update incremental y persistente, eslint y el complemento de python me creo esto casi automatico :D
def actualizar_indice(vectorstore, corpus=CORPUS):
    chunks = partir_corpus(corpus)
    ids = generar_ids(chunks)
    existentes = set(vectorstore.get()["ids"])
    nuevos = [(chunk, id_) for chunk, id_ in zip(chunks, ids) if id_ not in existentes]
    if not nuevos:
        return "indice_reutilizado", 0
    con_reintentos(lambda: vectorstore.add_documents(
        [chunk for chunk, _ in nuevos], ids=[id_ for _, id_ in nuevos]
    ))
    return ("indice_actualizado" if existentes else "indice_creado"), len(nuevos)

def filtrar_documentos_sospechosos(documentos):
    limpios, descartados = [], []
    for d in documentos:
        (descartados if detectar_inyeccion(d.page_content) else limpios).append(d)
    return limpios, descartados

class ModeloSimulado:

    def __init__(self,texto):
        self.texto = texto

    def invoke(self, prompt):
        return AIMessage(content=self.texto, usage_metadata={
            "input_tokens": 180, "output_tokens": 22, "total_tokens": 202
        })

def respuesta_sin_fuentes(auditoria, motivo):
    evento(auditoria, motivo)
    return {"trace_id": trace_id_var.get(), "respuesta": SIN_CONTEXTO, "fuentes":[], "auditoria": auditoria}

def responder(pregunta, retriever, llm, estado_indice="indice_reutilizado"):
    token = trace_id_var.set("trace-" + uuid.uuid4().hex[:8])
    auditoria, tiempos = [], {}
    try:
        evento(auditoria, "consulta_recibida", pregunta_len=len(pregunta))
        evento(auditoria, estado_indice)
        with medir(tiempos, "recuperacion"):
            documentos = retriever.invoke(pregunta)
        evento(auditoria, "documentos_recuperados", n=len(documentos))
        limpios, descartados = filtrar_documentos_sospechosos(documentos)
        if descartados:
            evento(auditoria, "documentos_descartados", n=len(descartados),
                   fuentes=sorted({d.metadata.get("fuente", "desconocida") for d in descartados}))
        if not limpios:
            return respuesta_sin_fuentes(auditoria, "sin_contexto_confiable")

        contexto, citas = formatear_contexto(limpios)
        with medir(tiempos, "generacion"):
            mensaje = llm.invoke(PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta))
        tokens = dict(mensaje.usage_metadata) if mensaje.usage_metadata else None
        evento(auditoria, "consumo_llm",
               input_tokens=tokens["input_tokens"] if tokens else None,
               output_tokens=tokens["output_tokens"] if tokens else None,
               costo_usd=calcular_costo_usd(tokens),
               tiempos_ms={etapa: round(s * 1000, 2) for etapa, s in tiempos.items()})

        usadas = {n: f for n, f in extraer_citas(mensaje.text, citas).items() if n in citas}
        if not usadas:
            return respuesta_sin_fuentes(auditoria, "respuesta_sin_cita")
        fuentes = sorted(set(usadas.values()))
        respuesta = mensaje.text.strip() + "\n\nFuentes: " + ", ".join(
            f"[{n}] {f}" for n, f in sorted(usadas.items()))
        return {"trace_id": trace_id_var.get(), "respuesta": respuesta,
                "fuentes": fuentes, "auditoria": auditoria}
    finally:
        trace_id_var.reset(token)


def preguntar_a_la_persona(pendiente):
    return input("Aprobar la version nueva del prompt? (s/n): ").strip().lower() == "s"

def supervisar_despliegue(huella, decidir=preguntar_a_la_persona):
    config = {"configurable": {"thread_id": nuevo_thread_id("gate2")}}
    pausado = app_despliegue.invoke({"huella_nueva": huella, "aprobado": False}, config=config)
    if "__interrupt__" not in pausado:
        raise RuntimeError("el grafo no se detuvo en el punto de supervision")
    pendiente = pausado["__interrupt__"][0].value
    print("pausado, pendiente:", pendiente)
    return resolver(app_despliegue, config, decidir(pendiente))

def construir_dependencias(simulado):
    if simulado:
        from langchain_chroma import Chroma
        from langchain_core.embeddings import DeterministicFakeEmbedding
        vectorstore = Chroma(collection_name="gate2_simulado",
                             embedding_function=DeterministicFakeEmbedding(size=768))
        llm = ModeloSimulado("Segun el contexto recuperado, esta es la respuesta [1].")
    else:
        from src.cadena_tres_pasos import construir_modelo
        vectorstore = cargar_vectorstore(CARPETA_VECTORSTORE)
        llm = construir_modelo()
    estado_indice, n_nuevos = actualizar_indice(vectorstore)
    print(f"Indice: {estado_indice} ({n_nuevos} chunks nuevos)")
    return vectorstore.as_retriever(search_kwargs={"k": K}), llm, estado_indice

def main():
    simulado = "--simulado" in sys.argv
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    pregunta = argumentos[0] if argumentos else PREGUNTA_DEMO
    print("MODO:", "SIMULADO (embeddings y modelo falsos, sin API)" if simulado
          else "REAL (llama a la API de Gemini)")
    retriever, llm, estado_indice = construir_dependencias(simulado)
    resultado = responder(pregunta, retriever, llm, estado_indice)
    print("--- respuesta completa del servicio ---")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

    print("--- punto de supervision humana ---")
    final = supervisar_despliegue(MI_HUELLA)
    print("estado final:", final)
    print("Proceso terminado sin errores.")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        mensaje = str(error)
        if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
            print("Limite de peticiones alcanzado. Espera un minuto y vuelve a ejecutar.")
        elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
            print('La API rechazo tu clave. Revisa el valor de GEMINI_API_KEY en tu ".env".')
        else:
            print("No se pudo completar la consulta:", type(error).__name__)
        print("Detalle tecnico:", mensaje)
        raise SystemExit(1)