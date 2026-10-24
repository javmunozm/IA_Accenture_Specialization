import random
import time
from typing import Any, Callable

import requests

from src.consumir_gemini import armar_peticion, extraer_texto,enviar_peticion

COSTO_POR_1000_TOKENS = 0.002 # referencial
costo_total_sesion = 0.0


def con_reintento(
        funcion: Callable[[], Any],
        intentos: int = 3,
        espera_base: float = 2,
        espera_maxima: float = 30,
) -> Any:
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            espera = min(espera_base * (2 ** (intento -1)), espera_maxima)
            espera_con_jitter = espera +random.uniform(0, espera * 0.1)
            print(f"Intento {intento} de {intentos} fallo. Reintentando en {espera_con_jitter:.1f}s..")
            time.sleep(espera_con_jitter)


def registrar_costo( respuesta: dict) -> float:
    global costo_total_sesion
    uso = respuesta.get("usageMetadata", {})
    total_tokens = uso.get("totalTokenCount", 0)
    costo_estimado = (total_tokens / 1000) * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo_estimado
    print(f"Operacion: {total_tokens} tokens, costo {costo_estimado:.5f} USD (acumulado {costo_total_sesion:.5f} USD)")
    return costo_estimado


def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    url, headers, body = armar_peticion(pregunta, system_instruction=system_instruction)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(url, headers, body))
    except TimeoutError:
        raise RuntimeError("El servicio no respondio tras varios intentos, prueba mas tarde")
    registrar_costo(respuesta)
    return extraer_texto(respuesta)

if __name__ == "__main__":
    try:
        print(consultar_modelo("¿Porque Chillan es la ciudad mas importante de chile?"))
        print(f"Costo acumulado de la sesion: {costo_total_sesion:.5f} USD")
    except (ValueError, RuntimeError, FileNotFoundError) as error:
        print("No se pudo completar la operacion: ", error)



