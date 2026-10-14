'''import os
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

    
    if respuesta.status_code != 200 or "candidates" not in datos:
        raise RuntimeError(f"Error {respuesta.status_code}: {datos}")
    
    return datos["candidates"][0]["content"]["parts"][0]["text"]

print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexion funciona"))
    
