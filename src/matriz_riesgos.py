def puntaje_riesgo(probabilidad, impacto):
    return probabilidad * impacto

def categoria_riesgo(puntaje):
    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"
    return "BAJO"

def esta_en_el_limite(probabilidad, impacto):
    categoria_actual = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    vecinos = [
        (probabilidad + 1, impacto), (probabilidad -1, impacto),
        (probabilidad, impacto + 1), (probabilidad, impacto -1),
    ]
    for p2, i2 in vecinos:
        if not (1 <= p2 <= 5 and 1 <= i2 <= 5):
            continue
        if categoria_riesgo(puntaje_riesgo(p2, i2)) != categoria_actual:
            return True
    return False

def completar_matriz(riesgos):
    for r in riesgos:
        r["puntaje"] = puntaje_riesgo(r["probabilidad"], r["impacto"])
        r["categoria"] = categoria_riesgo(r["puntaje"])
        r["al_limite"] = esta_en_el_limite(r["probabilidad"], r["impacto"])
    return sorted(riesgos, key=lambda x: -x["puntaje"])

FILA_MODELO = [
    {"riesgo": "Inyeccion de prompt via comentario de usuario indexado",
     "probabilidad": 4,   # 1 a 5: probable, con la informacion que se tiene
     "impacto": 4,        # 1 a 5: expone instrucciones internas y datos de clientes
     "mitigacion": "Filtro de patrones + delimitacion de contexto (Bloque 31)"},
]

mis_riesgos = [
    {"riesgo": "Registro de consultas sube la pregunta completa a GitHub (docs/registros_latencia_costo.jsonl)",
     "probabilidad": 4,   # ya pasa: registro_rag.py guarda "pregunta" y el archivo esta versionado
     "impacto": 3,        # hoy son preguntas de prueba
     "mitigacion": "Registrar longitud y huella en vez de la pregunta (Bloque 31, logging_rag.py)"},
    {"riesgo": "Agente ejecuta generar_reembolso sin aprobacion humana",
     "probabilidad": 2,   # solo si alguien quita la aprobacion o la salta
     "impacto": 5,        # accion con dinero e irreversible
     "mitigacion": "esperar_aprobacion con tiempo limite y registro_aprobaciones (Bloque 23, agente_supervision.py)"},
    {"riesgo": "Respuesta RAG con una cita inventada o fuera del contexto recuperado",
     "probabilidad": 3,
     "impacto": 3,
     "mitigacion": "extraer_citas marca 'Cita invalida / no encontrada' (Bloque 26) y precision/recall de la recuperacion (Bloque 27)"},
    {"riesgo": "Version nueva de PROMPT_TEMPLATE activada sin revisar el cambio",
     "probabilidad": 3,
     "impacto": 3,
     "mitigacion": "RegistroDePrompts y diff_prompts (Bloque 32, registro_prompts.py)"},
    {"riesgo": "Inyeccion de prompt via chunk recuperado: PROMPT_TEMPLATE mezcla instrucciones y contexto",
     "probabilidad": 2,   # el corpus son 6 documentos propios (CORPUS en indexar_corpus.py)
     "impacto": 4,
     "mitigacion": "Filtro de patrones, delimitacion de contexto y roles separados (Bloque 31, logging_rag.py)"},
    {"riesgo": "Error 429 de la capa gratuita corta la indexacion o la respuesta",
     "probabilidad": 4,   # ya paso al indexar el corpus
     "impacto": 2,
     "mitigacion": "con_reintentos con espera creciente en indexar_corpus.py (Bloque 25) y PAUSA_SEGUNDOS"},
    {"riesgo": "API key filtrada en el repositorio o en la URL de la peticion",
     "probabilidad": 1,
     "impacto": 5,
     "mitigacion": ".env con python-dotenv y header x-goog-api-key (Bloques 5-7)"},
]

PUNTOS_DE_SUPERVISION = {
    "Registro de consultas sube la pregunta completa a GitHub (docs/registros_latencia_costo.jsonl)":
        "Revisar git diff --staged de docs/*.jsonl antes de cada git push",
    "Agente ejecuta generar_reembolso sin aprobacion humana":
        "Aprobacion s/n en consola antes de generar_reembolso (agente_supervision.py, ya existe)",
    "Respuesta RAG con una cita inventada o fuera del contexto recuperado":
        "Una persona revisa la respuesta antes de usarla cuando extraer_citas marca una cita invalida",
    "Version nueva de PROMPT_TEMPLATE activada sin revisar el cambio":
        "interrupt de grafo_supervision.py antes de activar la huella nueva (Bloque 32)",
}

def imprimir_titulo(texto):
    print("=" * 62)
    print(texto)
    print("=" * 62)

def main():
    imprimir_titulo("EJEMPLO DE REFERENCIA (fila modelo)")
    for r in completar_matriz(FILA_MODELO):
        print(f"{r['categoria']:8} ({r['puntaje']:2} - {r['riesgo']})")
        if r["al_limite"]:
            print("revisar con otra persona:", r["riesgo"])

    imprimir_titulo("PASO 3: mi matriz de riesgos (ordenada por puntaje)")
    matriz = completar_matriz(mis_riesgos)
    for r in matriz:
        marca = "[AL LIMITE]" if r["al_limite"] else ""
        print(f"{r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']} {marca}")

    print()
    print("Puntos de supervision (riesgos ALTO o CRITICO):")
    for r in matriz:
        if r["categoria"] in ("ALTO", "CRITICO"):
            print(f"- {r['riesgo']}: {PUNTOS_DE_SUPERVISION.get(r['riesgo'], 'FALTA DEFINIRLO')}")


if __name__ == "__main__":
    main()