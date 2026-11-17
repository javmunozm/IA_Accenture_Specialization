def promedio_ponderado(puntajes, pesos):
    return sum(puntajes[d] * pesos[d] for d in pesos)

pesos = {
    "pipeline_funcional": 0.25, "recuperacion_citacion": 0.15,
    "costo_latencia": 0.10, "personalizacion": 0.15,
    "observabilidad": 0.15, "seguridad_gobernanza": 0.20,
}

# escala 0-100
mi_puntaje = {
    "pipeline_funcional": 90, 
    "recuperacion_citacion": 85,
    "costo_latencia": 90, 
    "personalizacion": 85,
    "observabilidad": 85, 
    "seguridad_gobernanza": 80,
}

no_compensables = {                          #default None
    "pipeline_corre_de_punta_a_punta": True,  # True/False
    "respuestas_citan_fuente": True,        # True/False
    "logs_sin_contenido_crudo": True,       # True/False
    "supervision_humana_funciona": True,    # True/False
}

faltan = [clave for clave, valor in {**mi_puntaje, **no_compensables}.items() if valor is None]
if faltan:
    print("Completa antes de calcular:", ", ".join(faltan))
else:
    promedio = promedio_ponderado(mi_puntaje, pesos)
    todos_los_no_compensables_ok = all(no_compensables.values())
    print(f"promedio: {promedio:.1f}, no compensables OK? {todos_los_no_compensables_ok}")
    if promedio >= 80 and todos_los_no_compensables_ok:
        print("Listo para entregar")
    else:
        print("Todavia no: corrige lo que falla antes de entregar")