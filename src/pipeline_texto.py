import re
from collections import Counter

def limpiar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def tokenizar(texto_limpio: str) -> list[str]:
    return texto_limpio.split()

def vectorizar(tokens: list[str]) -> Counter:
    return Counter(tokens)

def procesar_texto(texto: str) -> list[str]:
    return tokenizar(limpiar_texto(texto))

if __name__ == "__main__":
    texto = "El gato, el gato y el gaton corren corriendo como el viento."
    texto_limpio = limpiar_texto(texto)
    tokens = tokenizar(texto_limpio)
    print("Texto limpio:", texto_limpio)
    print("Tokens:", tokens)
    print("conteo:", vectorizar(tokens))