import os
import shutil
import time

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

CARPETA_VECTORSTORE = os.path.abspath("vectorstore")
COLECCION = "corpus_miniapp"
MODELO_EMBEDDINGS = "models/gemini-embedding-001"
CHUNK_SIZE = 250
CHUNK_OVERLAP = 40

CORPUS = {
    "peticiones": (
        "Toda llamada a Gemini pasa por src/consumir_gemini.py en tres pasos.\n"
        "armar_peticion arma la url, los headers y el body; enviar_peticion hace "
        "el POST con un timeout de 30 segundos; extraer_texto lee el texto generado.\n"
        "La API key se lee del archivo .env y viaja en el header x-goog-api-key, "
        "nunca en la URL."
    ),
    "reintentos": (
        "El cliente de src/cliente.py reintenta hasta 3 veces ante un TimeoutError, "
        "con espera creciente entre intento e intento.\n"
        "Espera 2 segundos tras el primer fallo y 4 tras el segundo, con un tope "
        "de 30 segundos y un pequeño margen aleatorio.\n"
        "Si el tercer intento tambien falla, consultar_modelo lanza un RuntimeError "
        "y pide probar mas tarde."
    ),
    "errores": (
        "Los errores se separan en dos tipos.\n"
        "ValueError significa que la entrada o la respuesta del modelo no sirve: "
        "una pregunta vacia, falta la API key o el JSON viene incompleto.\n"
        "RuntimeError significa que fallo el servicio: timeout, sin conexion o "
        "un HTTP 4xx o 5xx.\n"
        "Los scripts capturan ambos y el usuario nunca ve un traceback."
    ),
    "costos": (
        "El costo de cada llamada se calcula con usageMetadata: los tokens de "
        "entrada por su precio mas los tokens de salida por el suyo.\n"
        "El modelo por defecto, gemini-3.5-flash-lite, cobra 0,30 USD por millon "
        "de tokens de entrada y 2,50 USD por millon de tokens de salida.\n"
        "Los modelos que razonan cobran esos tokens de razonamiento como salida."
    ),
    "agente": (
        "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, "
        "segun la descripcion de cada una.\n"
        "consultar_estado_ticket responde el estado de un ticket y "
        "buscar_solucion_frecuente resuelve problemas comunes.\n"
        "generar_reembolso es de riesgo alto: antes de ejecutarla, una persona "
        "debe aprobarla dentro de 300 segundos.\n"
        "Cada interaccion queda registrada en docs/trazas_agente.jsonl."
    ),
    "pruebas": (
        "Las pruebas unitarias se ejecutan con py -m pytest desde la raiz.\n"
        "Simulan el modelo con MagicMock, asi que no llaman a la API, no gastan "
        "cuota y la suite completa corre en pocos segundos.\n"
        "Las metricas de precision, cobertura y F1 comparan los tokens de una "
        "respuesta con los de una respuesta de referencia."
    ),
}


def crear_embeddings():
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError('Falta GEMINI_API_KEY. Definela en tu archivo ".env".')
    return GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)

def con_reintentos(operacion, max_intentos=4, espera_inicial=5):
    espera = espera_inicial
    for intento in range(1, max_intentos + 1):
        try:
            return operacion()
        except Exception as error:
            mensaje = str(error)
            es_limite = "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje
            if not es_limite or intento == max_intentos:
                raise
            print(f"Limite de peticiones alcanzado. Reintento {intento} de {max_intentos - 1} en {espera} s ...")
            time.sleep(espera)
            espera *= 2

def partir_corpus(corpus, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.create_documents(
        list(corpus.values()),
        metadatas=[{"fuente":fuente} for fuente in corpus],
    )
def generar_ids(chunks):
    contador = {}
    ids = []
    for chunk in chunks:
        fuente = chunk.metadata["fuente"]
        numero = contador.get(fuente, 0)
        ids.append(f"{fuente}_{numero}")
        contador[fuente] = numero + 1
    return ids

def indexar_corpus(corpus, persist_directory, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    chunks = partir_corpus(corpus, chunk_size, chunk_overlap)
    ids = generar_ids(chunks)
    embeddings = crear_embeddings()
    shutil.rmtree(persist_directory, ignore_errors=True)
    # vectorstore = Chroma.from_documents(
    #     documents=chunks,
    #     embedding=embeddings,
    #     persist_directory=persist_directory
    # )
    vectorstore = con_reintentos(
        lambda: Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            ids=ids,
            collection_name=COLECCION,
            persist_directory=persist_directory,
        )
    )
    print(f"Indexados {len(chunks)} chunks en {persist_directory}")
    return vectorstore

def cargar_vectorstore(persis_directory=CARPETA_VECTORSTORE):
    return Chroma(
        collection_name=COLECCION,
        embedding_function=crear_embeddings(),
        persist_directory=persis_directory,
    )

def titulo(texto):
    print("=" * 60)
    print(texto)
    print("=" * 60)

if __name__ == "__main__":
    try:
        titulo("PASO 1: chunking + embeddings + indexacion")
        print("Ruta del indice:", CARPETA_VECTORSTORE)
        print("Coleccion:", COLECCION)
        chunks = partir_corpus(CORPUS)
        print(f"Corpus original: {len(CORPUS)} documentos")
        print(f"Despues de chunking: {len(chunks)} chunks")
        print()
        for i, chunk in enumerate(chunks, start=1):
            print(f"  chunk {i} [{chunk.metadata['fuente']}] ({len(chunk.page_content)} caracteres)")
        print()
        print("Ids:", generar_ids(chunks))
        print()
        print("Calculando embeddings e indexando en Chroma (esto llama a la API)...")
        indexar_corpus(CORPUS, CARPETA_VECTORSTORE)
        print()

        titulo("PASO 2: confirmando que quedo en disco, no solo en memoria")
        contenido = os.listdir(CARPETA_VECTORSTORE)
        print(f"Contenido real de la carpeta {CARPETA_VECTORSTORE} ({len(contenido)} elementos):")
        for nombre in contenido:
            print(f"  {nombre}")
    except Exception as error:
        mensaje = str(error)
        if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
            print("Limite de peticiones alcanzado. Espera un minuto y vuelve a ejecutar.")
        elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
            print('La API rechazo tu clave. Revisa el valor de GEMINI_API_KEY en tu ".env".')
        else:
            print("No se pudo indexar el corpus:", type(error).__name__)
        print("Detalle tecnico:", mensaje)
        raise SystemExit(1)