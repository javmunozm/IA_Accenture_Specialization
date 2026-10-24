'''
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def obtener_dato_de_prueba(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-3.5-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
    body = {
        "contents" : [
            {"parts": [{"text": pregunta}]}
        ]
    }
    respuesta = requests.post(url, json=body)
    datos = respuesta.json()
    return datos["candidates"][0]["content"]["parts"][0]["text"]

print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexion funciona"))
'''
##version mejorada de lo anterior
##version anterior era molesta, por que habia que escribir key siempre referenciando el api key expuesta
##y como soy medio torpe escribi varias veces Key, lo otro, por norma no se expone nunca esa info en la url
'''
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def obtener_dato_de_prueba(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No se encontro Api en .env")

    modelo = "gemini-3.5-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    headers = {"x-goog-api-key": api_key}
    body = {
            "contents" : [
                {"parts": [{"text": pregunta}]}
            ]
        }
    
    respuesta = requests.post(url, headers=headers, json=body)
    
    datos = respuesta.json()

    
    if not respuesta.ok:
        raise RuntimeError(f"Error {respuesta.status_code}: {respuesta.text}")
 
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"La respuesta no trae texto generado: {datos}")


print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexion funciona"))
'''
##refactorizar
'''
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No se encontró GEMINI_API_KEY en el .env")

    modelo = "gemini-3.5-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    headers = {"x-goog-api-key": api_key}
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, headers, body


def enviar_peticion(url, headers, body):
    respuesta = requests.post(url, headers=headers, json=body, timeout=30)
    if not respuesta.ok:
        raise RuntimeError(f"Error {respuesta.status_code}: {respuesta.text}")
    return respuesta.json()


def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"La respuesta no trae texto generado: {datos}")


def obtener_dato_de_prueba(pregunta):
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona"))
'''
##validaciones, exception, etc.
import os
import json
import re

import requests
from dotenv import load_dotenv

load_dotenv()


MODELO_POR_DEFECTO ="gemini-3.5-flash-lite"

def armar_peticion(pregunta, modelo=MODELO_POR_DEFECTO, system_instruction=None, response_schema=None):
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No se encontró GEMINI_API_KEY en el .env")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    headers = {"x-goog-api-key": api_key}
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return url, headers, body


def enviar_peticion(url, headers, body):
    try:
        respuesta = requests.post(url, headers=headers, json=body, timeout=30)
    ##except requests.exceptions.Timeout:
    ##    raise RuntimeError("El servicio tardo demasiado en responder. Intenta de nuevo.")
    ##except requests.exceptions.ConnectionError:
    ##    raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo conectar al proveedor. Puede ser momentaneo.")

    codigo = respuesta.status_code
    if codigo in (401, 403):
        raise ValueError("Credencial invalida o sin permiso. Revisa tu GEMINI_API_KEY.")
    if codigo == 400: #Este es el verdadero error que se genera con una api mal ingresada...
        raise ValueError("Peticion rechazada (Bad Request). Error de API")
    if codigo == 404:
        raise FileNotFoundError("modelo no existe o mal escrito")
    if codigo == 429:
        raise TimeoutError("Demasiados intentos, espere unos minutos para reintentar.")
    if codigo >= 500:
        raise TimeoutError("El proveedor no pudo procesar la peticion")
   

    if not respuesta.ok:
        raise RuntimeError(f"El servicio responde con error {respuesta.status_code}: {respuesta.text}")

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llego en el formato esperado.")


def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def obtener_dato_de_prueba(pregunta):
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


def calcular_costo(datos: dict, precio_entrada: float, precio_salida: float) -> float:
    """Calcula el costo en USD de una peticion usando usageMetadata"""
    uso = datos["usageMetadata"]
    tokens_entrada = uso["promptTokenCount"]
    token_salida = uso["candidatesTokenCount"]
    return (tokens_entrada * precio_entrada) + (token_salida * precio_salida)


def parsear_respuesta_json(texto, claves_requeridas=("categoria", "confianza")):
    """limpia, valida y interpreta el json devuelto"""
    texto_limpio = texto.strip() #quita espacios
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio) ##borra los ```
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)## borra '''

    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no JSON valido")

    if not isinstance(datos, dict):
        raise ValueError("la respuesta del modelo no es un objeto JSON")

    faltantes = [clave for clave in claves_requeridas if clave not in datos]
    if faltantes:
        raise ValueError(f"la respuesta no tiene la estructura espada. Faltan: {faltantes}")

    return datos


if __name__ == "__main__":
    pruebas = {
        "Entrada vacia": "",
        "Entrada valida": "Confirma en una frase corta que esta conexión funciona",
    }

    for nombre, pregunta in pruebas.items():
        print(f"--- {nombre} ---")
        try:
            print(obtener_dato_de_prueba(pregunta))
        except (ValueError, RuntimeError, TimeoutError, FileNotFoundError) as error:
            print("No se pudo completar la operacion:", error)