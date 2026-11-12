# def recomendar_estrategia(respuestas): ## esto fue para testear
#     puntos = {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0}

#     if respuestas["informacion_cambia_seguido"]:
#         puntos["RAG"] += 3
#     if respuestas["problema_de_formato_o_tono"]:
#         puntos["PEFT"] += 2
#         puntos["Fine-tuning completo"] += 1
#     if respuestas["dataset_grande_y_de_calidad"]:
#         puntos["Fine-tuning completo"] += 2
#         puntos["PEFT"] += 1
#     if respuestas["presupuesto_limitado_o_iterar_rapido"]:
#         puntos["RAG"] += 2
#         puntos["PEFT"] += 1
#     if respuestas["necesita_multiples_variantes"]:
#         puntos["PEFT"] += 2

#     maximo = max(puntos.values())

#     ganadoras = [tecnica for tecnica, p in puntos.items() if p == maximo]
#     return puntos, ganadoras
import os 

RUTA_DOCUMENTO = os.path.join("docs", "decision_personalizacion.md")

RESPUESTAS_MI_CASO = {#Default es None, para pruebas True/False 
    "informacion_cambia_seguido": False,  #5 intenciones fijas, banco.py sin cambios
    "problema_de_formato_o_tono": True, #clasificar_mensaje: 1 de 3 respuestas invalidas (33 %), muestra de 3
    "dataset_grande_y_de_calidad": False,# 12 ejemplos etiquetados, menos de 200
    "presupuesto_limitado_o_iterar_rapido": True, # la clave de AI Studio no puede entrenar: 0 intentos posibles
    "necesita_multiples_variantes": False, # un solo clasificador, un idioma
}
#"El clasificador de errores del cliente no responde con un formato consistente."
PROBLEMA = "El clasificador de tickets de soporte no siempre devuelve la intencion y la prioridad en el formato JSON esperado."
def recomendar_estrategia(respuestas):
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

    maximo = max(puntos.values())

    ganadoras = [tecnica for tecnica, p in puntos.items() if p == maximo]
    return puntos, ganadoras

def generar_esqueleto_decision(problema, puntos, ganadoras):
    empate = len(ganadoras) > 1
    lineas = []
    lineas.append("# Decision de personalizacion")
    lineas.append("")
    lineas.append("## 1. El problema")
    lineas.append(problema)
    lineas.append("")
    lineas.append("## 2. Resultado del metodo de decision")
    for tecnica, p in sorted(puntos.items(), key=lambda x: -x[1]):
        lineas.append(f"- {tecnica}: {p} puntos")
    if empate:
        lineas.append("")
        lineas.append(f"**Empate entre: {', '.join(ganadoras)}**")
    lineas.append("")
    lineas.append("## 3. Tecnica elegida y por que")
    if empate:
        lineas.append(
            "[COMPLETAR: el puntaje no resolvio el empate solo -- "
            "justifica aqui con criterio propio]"
        )
    else:
        lineas.append(f"[COMPLETAR: por que {ganadoras[0]} responde mejor a este caso]")
    lineas.append("")
    lineas.append("## 4. Que necesitarias para ejecutarla")
    lineas.append(
        "[COMPLETAR: corpus faltante, o cantidad de ejemplos etiquetados que faltan]"
    )
    return "\n".join(lineas)


def main():
    if any(valor is None for valor in RESPUESTAS_MI_CASO.values()):
        raise SystemExit("Completa las cinco respuestas con True o False antes de continuar.")

    puntos, ganadoras = recomendar_estrategia(RESPUESTAS_MI_CASO)
    print(puntos)
    print("candidatas:", ganadoras)
    print()

    esqueleto = generar_esqueleto_decision(PROBLEMA, puntos, ganadoras)
    print(esqueleto)
    print()

    
    if os.path.exists(RUTA_DOCUMENTO): # Para que no se sobrescriba el documento si ya existe.
        print(f"{RUTA_DOCUMENTO} ya existe: no se sobrescribe para no perder lo que completaste.")
        print("Si quieres regenerarlo, borralo y vuelve a ejecutar.")
        return

    os.makedirs("docs", exist_ok=True)
    with open(RUTA_DOCUMENTO, "w", encoding="utf-8") as f:
        f.write(esqueleto + "\n")
    print("Esqueleto guardado en", RUTA_DOCUMENTO)


if __name__ == "__main__":
    main()