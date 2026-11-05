import re
import time

from src.cadena_tres_pasos import construir_modelo
from src.indexar_corpus import CARPETA_VECTORSTORE, cargar_vectorstore

PAUSA_SEGUNDOS = 2

PROMPT_TEMPLATE = """Reponde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""

PREGUNTAS_DE_PRUEBA = [
    "Que pasa si mi conexion tarda demasiado?",
    "Como decide el agente que herramienta usar?",
    "Cuanto cuesta el plan premium de la aplicacion?",
]

def formatear_contexto(chunks_recuperados):
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente
    contexto = "\n\n".join(lineas)
    return contexto, citas

def construir_prompt(pregunta, persist_directory, k=3):
    vectorstore = cargar_vectorstore(persist_directory)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    chunks_recuperados = retriever.invoke(pregunta)
    contexto, citas = formatear_contexto(chunks_recuperados)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
    return prompt, citas

def extraer_citas(respuesta, citas):
    indices = [int(num) for num in re.findall(r"\[(\d+)\]", respuesta)]
    return {idx: citas.get(idx, "Cita invalida / no encontrada") for idx in indices}

def responder(prompt):
    return construir_modelo().invoke(prompt).text

if __name__ == "__main__":
    try:
        for numero, pregunta in enumerate(PREGUNTAS_DE_PRUEBA):
            if numero > 0:
                time.sleep(PAUSA_SEGUNDOS)
                print("-" * 60)
            prompt, citas = construir_prompt(pregunta, persist_directory=CARPETA_VECTORSTORE)
            print(prompt)
            print("citas:", citas)
            respuesta = responder(prompt)
            print("\nRespuesta del modelo:", respuesta)
            print("Citas de la respuesta:", extraer_citas(respuesta, citas))
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