import time
from datetime import date

from src.indexar_corpus import (
    CARPETA_VECTORSTORE,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    cargar_vectorstore,
)

K = 3 # chunks que el retriever recuperara y cuantos se evaluaran
K_COMPARACION = 5
PAUSA_SEGUNDOS = 2
ARCHIVO_RESULTADOS = "docs/resultados_evaluacion.txt"

casos_evaluacion = [
    {"pregunta": "que hace el cliente si una llamada tarda demasiado",
     "ids_relevantes": {"reintentos_0", "reintentos_1"}},
    {"pregunta": "cuanto espera el cliente entre un intento y el siguiente",
     "ids_relevantes": {"reintentos_0"}},
    {"pregunta": "donde se guarda la clave de la api y como se envia",
     "ids_relevantes": {"peticiones_1"}},
    {"pregunta": "que funciones intervienen al mandar una pregunta a gemini",
     "ids_relevantes": {"peticiones_0"}},
    {"pregunta": "que diferencia hay entre un ValueError y un RuntimeError",
     "ids_relevantes": {"errores_0", "errores_1"}},
    {"pregunta": "cuanto cobra el modelo por defecto por millon de tokens",
     "ids_relevantes": {"costos_1"}},
    {"pregunta": "como se calcula el costo de una llamada",
     "ids_relevantes": {"costos_0"}},
    {"pregunta": "como elige el agente la herramienta que va a usar",
     "ids_relevantes": {"agente_0"}},
    {"pregunta": "que tiene que pasar antes de generar un reembolso",
     "ids_relevantes": {"agente_1"}},
    {"pregunta": "como se corren las pruebas sin gastar cuota",
     "ids_relevantes": {"pruebas_0"}},
    {"pregunta": "que comparan las metricas de precision cobertura y F1",
     "ids_relevantes": {"pruebas_1"}},
    # Sin respuesta en el corpus: recall n/a, se excluye del promedio de recall
    {"pregunta": "cual es el horario de atencion de la mesa de ayuda",
     "ids_relevantes": set()},
]


def precision_at_k(ids_recuperados, ids_relevantes):
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)

def recall_at_k(ids_recuperados, ids_relevantes):
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)

def promediar(valores):
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0

def evaluar_recuperacion(retriever, casos, k=3):
    resultados = []
    for caso in casos:
        chunks = retriever.invoke(caso["pregunta"])
        ids_recuperados = [c.id for c in chunks][:k]
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({"pregunta": caso["pregunta"], "precision":p, "recall": r})

    precision_promedio = promediar(x["precision"] for x in resultados)
    recall_promedio = promediar(x["recall"] for x in resultados)
    return resultados, precision_promedio, recall_promedio

def correr_evaluacion(k):
    vectorstore = cargar_vectorstore(CARPETA_VECTORSTORE)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return evaluar_recuperacion(retriever, casos_evaluacion, k=k)

def imprimir_resultados(resultados, precision_promedio, recall_promedio):
    for r in resultados:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        print(f"{r['precision']:.2f} {recall_txt} {r['pregunta']}")
    print(f"\npromedio -> precision: {precision_promedio:.3f} recall: {recall_promedio:.3f}")

def guardar_resultados(resultados, precision_promedio, recall_promedio, k, ruta=ARCHIVO_RESULTADOS):
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(f"Fecha: {date.today()}\n")
        archivo.write(f"Configuracion: k={k}, chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP}\n\n")
        for r in resultados:
            recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
            archivo.write(f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}\n")
        archivo.write(
            f"\npromedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}\n"
        )
        print(f"Resultados guardados en {ruta}")

def titulo(texto):
    print("=" * 60)
    print(texto)
    print("=" * 60)

if __name__ == "__main__":
    try:
        titulo(f"PASO 1: tu conjunto de evaluacion ({len(casos_evaluacion)} preguntas etiquetadas)")
        for caso in casos_evaluacion:
            print(f" {caso['pregunta']!r} -> relevantes: {sorted(caso['ids_relevantes'])}")

        print()
        titulo(f"PASO 2: primera corrida, k={K}")
        primera = correr_evaluacion(K)
        imprimir_resultados(*primera)

        time.sleep(PAUSA_SEGUNDOS)
        print()
        titulo(f"PASO 3: segunda corrida, k={K} otra vez -- debe dar identico")
        segunda = correr_evaluacion(K)
        imprimir_resultados(*segunda)
        print("\nIdentico a la primera corrida:", primera == segunda)

        time.sleep(PAUSA_SEGUNDOS)
        print()
        titulo(f"PASO 4: tercera corrida, k={K_COMPARACION}")
        tercera = correr_evaluacion(K_COMPARACION)
        imprimir_resultados(*tercera)
        print(f"\nrecall subio o se mantuvo (k={K} -> k={K_COMPARACION}):", tercera[2] >= primera[2])
        print(f"precision bajo o se mantuvo (k={K} -> k={K_COMPARACION}):", tercera[1] <= primera[1])

        print()
        guardar_resultados(*primera, K)
    except Exception as error:
        mensaje = str(error)
        if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
            print("Limite de peticiones alcanzado. Espera un minuto y vuelve a ejecutar.")
        elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
            print('La API rechazo tu clave. Revisa el valor de GEMINI_API_KEY en tu ".env".')
        else:
            print("No se pudo completar la evaluacion:", type(error).__name__)
        print("Detalle tecnico:", mensaje)
        raise SystemExit(1)