import time
from src.cliente import consultar_modelo
from src.pipeline_texto import procesar_texto

SYSTEM_INSTRUCTION = "Responde en una sola frase corta, en español y sin formato markdown."
PAUSA_SEGUNDOS = 2
CASOS = [
    ("¿Que es python?", "python es un lenguaje de programación interpretado."),
    ("¿Cuando se creo la culebra python?", "python fue creado en 1991."),
    ("¿Que es una lista en python?", "Una lista es una coleccion ordenada y modificable."),
]

def coincidencia(tokens_referencia: list[str], tokens_respuesta: list[str]) -> float:
    if not tokens_referencia:
        return 0.0
    comunes = set(tokens_referencia) & set(tokens_respuesta)
    return len(comunes) / len(set(tokens_referencia))

if __name__ == "__main__":
    try:
        for i, (consulta, referencia) in enumerate(CASOS, start=1):
            respuesta = consultar_modelo(consulta, system_instruction=SYSTEM_INSTRUCTION)
            pct_raw = coincidencia(referencia.split(), respuesta.split())
            pct_proc = coincidencia(procesar_texto(referencia), procesar_texto(respuesta))
            print(f"[Caso {i}] {consulta} -> {respuesta}")
            print(f"[Caso {i}] Coincidencia texto raw: {pct_raw:.1%}")
            print(f"[Caso {i}] coincidencia texto procesado: {pct_proc:.1%}\n")
            if i < len(CASOS):
                time.sleep(PAUSA_SEGUNDOS)
    except (ValueError, RuntimeError, FileNotFoundError) as error:
        print("No se pudo completar la operacion:", error)