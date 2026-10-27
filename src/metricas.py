from collections import Counter

from src.pipeline_texto import procesar_texto

def contar_coincidencias( tokens_referencia: list[str], tokens_respuesta: list[str]) -> int:
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())

def calcular_precision_cobertura_f1(tokens_referencia: list[str], tokens_respuesta: list[str]) -> dict[str, float]:
    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)
    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {"precision": precision, "cobertura": cobertura, "f1": f1}


def calcular_metricas(texto_referencia: str, texto_respuesta: str) -> dict[str, float]:
    return calcular_precision_cobertura_f1(
        procesar_texto(texto_referencia), procesar_texto(texto_respuesta)
    )

def resumir_metricas(resultados: list[dict]) -> dict[str, float]:
    if not resultados:
        return {"precision_promedio": 0, "cobertura_promedio": 0, "f1_promedio": 0}

    n = len(resultados)
    return {
        "precision_promedio": sum(r["precision"] for r in resultados) / n,
        "cobertura_promedio": sum(r["cobertura"] for r in resultados) / n,
        "f1_promedio": sum(r["f1"] for r in resultados) /n,
    }

if __name__ == "__main__":
    EJEMPLOS = [
        ("Ejemplo ajam","El gato duerme en el sillon", "el gato duerme en la silla todo el dia"),
        ("Sinonimos perfecto", "El auto es rapido", "el vehiculo es veloz"),
        ("Dato equivocado", "Python fue creado en 1991", "Python fue creado en 1989"),
        ("Palabra que falta", "Python no es un lenguaje compilado", "Python es un lenguaje compilado"),
    ]
    for nombre, referencia, respuesta in EJEMPLOS:
        m = calcular_metricas(referencia, respuesta)
        print(f"{nombre:18} precision={m['precision']:.2f} cobertura={m['cobertura']:.2f}")