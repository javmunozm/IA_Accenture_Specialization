import json 
import time
from contextlib import contextmanager
from datetime import datetime, timezone

from src.cadena_tres_pasos import construir_modelo
from src.evaluacion_recuperacion import casos_evaluacion
from src.indexar_corpus import CARPETA_VECTORSTORE, cargar_vectorstore
from src.recuperacion import PROMPT_TEMPLATE, formatear_contexto

ARCHIVO_REGISTROS = "docs/registros_latencia_costo.jsonl"
PAUSA_SEGUNDOS = 2

PRECIO_ENTRADA_POR_MILLON = 0.30
PRECIO_SALIDA_POR_MILLON = 2.50

@contextmanager
def medir(tiempos, etapa):
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio

def calcular_costo_usd(tokens):
    if not tokens:
        return None
    costo_entrada = tokens["input_tokens"] / 1_000_000 * PRECIO_ENTRADA_POR_MILLON
    costo_salida = tokens["output_tokens"] / 1_000_000 * PRECIO_SALIDA_POR_MILLON
    return round(costo_entrada + costo_salida, 8)

def registrar_consulta(pregunta, persist_directory, k=3):
    tiempos = {}

    vectorstore = cargar_vectorstore(persist_directory)
    chat_model = construir_modelo()

    with medir(tiempos, "embed_query"):
        vector = vectorstore.embeddings.embed_query(pregunta)

    with medir(tiempos, "busqueda_vectorial"):
        chunks = vectorstore.similarity_search_by_vector(vector, k=k)

    contexto, _ = formatear_contexto(chunks)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    with medir(tiempos, "generacion"):
        respuesta = chat_model.invoke(prompt)

    tokens = dict(respuesta.usage_metadata) if respuesta.usage_metadata else None
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": tokens,
        "costo_usd": calcular_costo_usd(tokens),
    }
    return registro

def guardar_registro(registro, ruta=ARCHIVO_REGISTROS):
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def titulo(texto):
    print("=" * 60)
    print(texto)
    print("=" * 60)

if __name__ == "__main__":
    try:
        titulo("PASO 1: registrando 3 consultas distintas (Como se prueba, chequeo 1)")
        preguntas = [casos_evaluacion[0]["pregunta"], casos_evaluacion[6]["pregunta"], casos_evaluacion[7]["pregunta"]]
        for numero, pregunta in enumerate(preguntas):
            if numero > 0:
                time.sleep(PAUSA_SEGUNDOS)
            registro = registrar_consulta(pregunta, persist_directory=CARPETA_VECTORSTORE)
            print(json.dumps(registro, indent=2, ensure_ascii=False))
            guardar_registro(registro)
        print()
        titulo("PASO 2: misma pregunta con k=3 y k=6 ")
        pregunta = casos_evaluacion[4]["pregunta"]
        for k in (3, 6):
            time.sleep(PAUSA_SEGUNDOS)
            registro = registrar_consulta(pregunta, persist_directory=CARPETA_VECTORSTORE, k=k)
            guardar_registro(registro)
            entrada = registro["tokens"]["input_tokens"] if registro["tokens"] else None
            print(f"k={k} -> input_tokens: {entrada} costo_usd: {registro['costo_usd']}")

        print(0)
        titulo("PASO 3: confirmando el archivo de registros")
        with open(ARCHIVO_REGISTROS, encoding="utf-8") as f:
            lineas = f.readlines()
        print(f"{ARCHIVO_REGISTROS} tiene {len(lineas)} lineas (una por corrida)")
    except Exception as error:
        mensaje = str(error)
        if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
            print("Limite de peticiones alcanzado. Espera un minuto y vuelve a ejecutar.")
        elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
            print('La API rechazo tu clave. Revisa el valor de GEMINI_API_KEY en tu ".env".')
        else:
            print("No se pudo registrar la consulta:", type(error).__name__)
        print("Detalle tecnico:", mensaje)
        raise SystemExit(1)