from src.decision import recomendar_estrategia

def recomendar_estrategia_primera_version(respuestas):
    puntos = {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0}

    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3
    if respuestas["problema_de_formato_o_tono"]:
        puntos["PEFT"] += 2
        puntos["Fine-tuning completo"] += 1
    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1
    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1
    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2

    ganador = max(puntos, key=puntos.get)
    return puntos, ganador


respuestas_caso2 = {
    "informacion_cambia_seguido": False,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": True,
    "presupuesto_limitado_o_iterar_rapido": False,
    "necesita_multiples_variantes": False,
}

respuestas_caso1 = {
    "informacion_cambia_seguido": True,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": False,
    "presupuesto_limitado_o_iterar_rapido": True,
    "necesita_multiples_variantes": False,
}

def titulo(texto):
    print("=" * 68)
    print(texto)
    print("=" * 68)

def main():
    titulo("PASO 1: la primera version esconde el empate")
    puntos2, ganador2 = recomendar_estrategia_primera_version(respuestas_caso2)
    print("caso 2:", puntos2, "-> recomendacion:", ganador2)
    print()

    titulo("PASO 2: la version corregida lo reporta")
    puntos2, ganadoras2 = recomendar_estrategia(respuestas_caso2)
    print("caso 2:", puntos2)
    print("candidatas empatadas:", ganadoras2)
    print()

    titulo("DETALLE: las dos lineas clave de la funcion corregida")
    print(list(puntos2.items()))
    maximo2 = max(puntos2.values())
    print("maximo:", maximo2)
    print([tecnica for tecnica, p in puntos2.items() if p == maximo2])
    print()

    titulo("PASO 3: analisis de sensibilidad del empate")
    for clave in respuestas_caso2:
        variante = dict(respuestas_caso2)
        variante[clave] = not variante[clave]
        puntos_v, ganadoras_v = recomendar_estrategia(variante)
        cambio = "CAMBIA" if set(ganadoras_v) != set(ganadoras2) else "igual"
        print(f"{clave} -> {not respuestas_caso2[clave]}: {ganadoras_v}  [{cambio}]")
    print()

    titulo("PASO 4: un caso sin empate")
    puntos1, ganadoras1 = recomendar_estrategia(respuestas_caso1)
    print("caso 1:", puntos1)
    print("candidatas empatadas:", ganadoras1)

if __name__ == "__main__":
    main()