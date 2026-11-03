import json
import os
from datetime import datetime, timezone

ARCHIVO_TRAZAS = "docs/trazas_agente.jsonl"

def registrar_traza(session_id: str, entrada: str, resultado: dict, archivo: str = ARCHIVO_TRAZAS) -> None:
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": resultado["output"],
    }
    os.makedirs(os.path.dirname(archivo) or ".", exist_ok=True)
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

def marcar_repeticiones_sospechosas(archivo: str = ARCHIVO_TRAZAS) -> None:
    try:
        with open(archivo, encoding="utf-8") as f:
            registros =[json.loads(linea) for linea in f]
    except FileNotFoundError:
        print(
            f"No se encontro '{archivo}'. Corre "
            "registrar_taza al menos una vez antes "
            "de revisar repeticiones."
        )
        return

    for registro in registros:
        herramientas = [a["herramienta"] for a in registro.get("acciones", [])]
        for i in range(1, len(herramientas)):
            if herramientas[i] == herramientas[i - 1]:
                print(
                    f"Revisar: {registro['session_id']} uso "
                    f"'{herramientas[i]}' dos veces seguidas"
                )
                break

if __name__ == "__main__":
    marcar_repeticiones_sospechosas()