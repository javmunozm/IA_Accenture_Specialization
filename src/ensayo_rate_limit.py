from src import cliente

PETICIONES = 100

for i in range(PETICIONES):
    try:
        respuesta = cliente.consultar_modelo(f"Pregunta de prueba numero {i}")
        print(f"Respuesta {i}: {respuesta[:40]}...")
    except (ValueError, RuntimeError, FileNotFoundError) as error:
        print(f"Respuesta {i} fallo : {error}")

print(f"Costo total del ensayo : {cliente.costo_total_sesion:5f} USD")