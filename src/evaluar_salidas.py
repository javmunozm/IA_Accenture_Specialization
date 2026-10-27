import json
import os
import time

from src import cliente
from src.metricas import calcular_metricas, resumir_metricas

SYSTEM_INSTRUCTION = "Responde en una sola oracion corta, en español NEUTRO y sin formato markdown."
ARCHIVO_RESULTADOS = "docs/resultados_metricas.json"
PAUSA_SEGUNDOS = 2  #  si jode mucho subir 1 segundo mas para evitar 429

CASOS = [
    ("que es python?", "es un lenguaje de programacion interpretado"),
    ("cuando salio python?", "en 1991"),
    ("que es una lista en python?", "una coleccion ordenada que podes ir modificando"),
    ("cual es la capital de chile?", "santiago"),
    ("que es una api rest?", "una forma de comunicar sistemas y pasar datos usando peticiones http"),
    ("que significa el error 404?", "que no se encontro lo que buscabas"),
    ("que significa el codigo http 429?", "que mandaste demasiadas peticiones seguidas"),
    ("cuantos dias tiene un año bisiesto?", "366"),
    ("python es compilado?", "no, es interpretado"),
    ("como guarda las cosas un json?", "en texto plano como pares de clave y valor"),
    ("para que sirve git?", "para llevar el control de versiones del codigo"),
    ("que es un entorno virtual en python?", "un espacio aislado para no mezclar las librerias de tus proyectos"),
    ("en que año llego el hombre a la luna?", "en 1969"),
    ("cual es el oceano mas grande?", "el pacifico"),
    ("que es un token en una ia?", "un pedazo de texto o palabra que procesa el modelo"),
    ("cuantos bits son un byte?", "8"),
    ("que hace la funcion len en python?", "te cuenta cuantos elementos tiene algo"),
    ("quien escribio cien años de soledad?", "gabriel garcia marquez"),
    ("a cuantos grados hierve el agua a nivel del mar?", "a 100 grados"),
    ("para que sirve la temperatura en un modelo de lenguaje?", "para regular que tan creativa o aleatoria sale la respuesta"),
]


def generar_resultados(casos: list[tuple[str, str]]) -> list[dict]:
    resultados = []
    for i, (consulta, referencia) in enumerate(casos, start=1):
        try:
            respuesta = cliente.consultar_modelo(consulta, system_instruction=SYSTEM_INSTRUCTION)
        except RuntimeError as error:
            print(f"Caso {i} sin respuesta, se omite: {error}")
            continue
        metricas = calcular_metricas(referencia, respuesta)
        resultados.append({
            "consulta": consulta,
            "referencia": referencia,
            "respuesta": respuesta,
            **{clave: round(valor, 2) for clave,valor in metricas.items()}, #desempacar
        })
        print(f"Caso {i}/ {len(casos)}: f1={metricas['f1']:.2f} {consulta}")
        if i < len(casos):
            time.sleep(PAUSA_SEGUNDOS)
    return resultados

def elegir_muestra(resultados: list[dict], por_extremo: int = 5) -> list[dict]:
    ordenados = sorted(resultados, key=lambda r: r["f1"])
    if len(ordenados) <= 2 * por_extremo:
        return ordenados
    return ordenados[:por_extremo] + ordenados[-por_extremo:]

if __name__ == "__main__":
    try:
        resultados = generar_resultados(CASOS)
    except (ValueError, FileNotFoundError) as error:
        print("No se pudo completar la operacion:", error)
    else:
        os.makedirs("docs", exist_ok=True)
        with open(ARCHIVO_RESULTADOS, "w", encoding="utf-8") as archivo:
            json.dump(resultados, archivo, indent=2, ensure_ascii=False)

        resumen = resumir_metricas(resultados)
        print(f"\n{len(resultados)} resultados guardados en {ARCHIVO_RESULTADOS}")
        print(f"Precision promedio: {resumen['precision_promedio']:.2f}")
        print(f"Cobertura promedio: {resumen['cobertura_promedio']:.2f}")
        print(f"F1 promedio:        {resumen['f1_promedio']:.2f}")
        print(f"Costo de la evaluacion: {cliente.costo_total_sesion:.5f} USD")

        print("\nMuestra para revisar a mano (F1 de menor a mayor):")
        for caso in elegir_muestra(resultados):
            print(f"    {caso['f1']:.2f}    {caso['consulta']}")