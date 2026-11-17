def promedio_ponderado(puntajes, pesos):
    return sum(puntajes[d] * pesos[d] for d in pesos)

pesos = {
    "pipeline_funcional": 0.25,
    "recuperacion_citacion": 0.15,
    "costo_latencia": 0.10,
    "personalizacion": 0.15,
    "observabilidad": 0.15,
    "seguridad_gobernanza": 0.20,
}
print("suma de pesos:", sum(pesos.values()))

def evaluar_gate(puntajes, no_compensables_ok, umbral=80):
    promedio = promedio_ponderado(puntajes, pesos)
    aprueba = promedio >= umbral and no_compensables_ok
    return promedio, aprueba

puntajes = {
    "pipeline_funcional": 95, "recuperacion_citacion": 90, "costo_latencia": 85,
    "personalizacion": 88, "observabilidad": 92, "seguridad_gobernanza": 80,
}

promedio_1, aprueba_1 = evaluar_gate(puntajes, no_compensables_ok=False)
print(f"caso 1: promedio {promedio_1:.1f}, no compensables OK? False -> aprueba? {aprueba_1}")

promedio_2, aprueba_2 = evaluar_gate(puntajes, no_compensables_ok=True)
print(f"caso 2: promedio {promedio_2:.1f}, no compensables OK? True -> aprueba? {aprueba_2}")

puntajes_bajos = {k: v - 15 for k, v in puntajes.items()}
promedio_3, aprueba_3 = evaluar_gate(puntajes_bajos, no_compensables_ok=True)
print(f"caso 3: promedio {promedio_3:.1f}, no compensables OK? True -> aprueba? {aprueba_3}")