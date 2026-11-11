import json
import time
from collections import Counter

from dotenv import load_dotenv

from src.consumir_gemini import MODELO_POR_DEFECTO

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise SystemExit("No se pudo importar google.genai. Ejecuta pip install google-genai")


# Con una API key de Google AI Studio el envio no es posible (ver el manual): debe quedar en false.
ENVIAR_TRABAJO = False
MODELO_BASE = f"models/{MODELO_POR_DEFECTO}"
CLAVES_ESPERADAS = ("intencion", "prioridad")
CLAVE_BALANCE = "intencion"
INTERVALO_SEGUNDOS = 30

# EJEMPLOS_RAW = [
#     ("No puedo iniciar sesion desde ayer: dice que mi contraseña es incorrecta aunque ya la cambie dos veces.",
#      {"intencion": "acceso", "prioridad": "alta"}),
#     ("Me cobraron dos veces la suscripcion de este mes, necesito el reembolso de uno de los cargos.",
#      {"intencion": "facturacion", "prioridad": "alta"}),
#     ("Quisiera saber si el plan Pro incluye mas de un usuario, no es urgente.",
#      {"intencion": "consulta_plan", "prioridad": "baja"}),
#     ("La aplicacion se cierra sola cada vez que intento subir una foto.",
#      {"intencion": "falla_tecnica", "prioridad": "media"}),
#     ("Quiero dar de baja mi cuenta al terminar el mes, gracias.",
#      {"intencion": "cancelacion", "prioridad": "media"}),
#     ("No me llega el correo para restablecer la contrasena.",
#      {"intencion": "acceso", "prioridad": "media"}),
#     ("Hay un cargo en mi tarjeta que no reconozco y quiero que lo revisen hoy.",
#      {"intencion": "facturacion", "prioridad": "alta"}),
# ]


EJEMPLOS_RAW = [# # Parte de los 7 del ejemplo resuelto y llega a 12, son tickets de soporte basados en el proecto
    ("No puedo iniciar sesion desde ayer: dice que mi contrasena es incorrecta aunque ya la cambie dos veces.",
     {"intencion": "acceso", "prioridad": "alta"}),
    ("Me cobraron dos veces la suscripcion de este mes, necesito el reembolso de uno de los cargos.",
     {"intencion": "facturacion", "prioridad": "alta"}),
    ("Quisiera saber si el plan Pro incluye mas de un usuario, no es urgente.",
     {"intencion": "consulta_plan", "prioridad": "baja"}),
    ("La aplicacion se cierra sola cada vez que intento subir una foto.",
     {"intencion": "falla_tecnica", "prioridad": "media"}),
    ("Quiero dar de baja mi cuenta al terminar el mes, gracias.",
     {"intencion": "cancelacion", "prioridad": "media"}),
    ("No me llega el correo para restablecer la contrasena.",
     {"intencion": "acceso", "prioridad": "media"}),
    ("Hay un cargo en mi tarjeta que no reconozco y quiero que lo revisen hoy.",
     {"intencion": "facturacion", "prioridad": "alta"}),
    ("Necesito la factura del mes pasado a nombre de mi empresa.",
     {"intencion": "facturacion", "prioridad": "baja"}),
    ("Tienen descuento si pago el plan anual en vez del mensual?",
     {"intencion": "consulta_plan", "prioridad": "baja"}),
    ("La pagina tarda mucho en cargar desde hace dos dias.",
     {"intencion": "falla_tecnica", "prioridad": "media"}),
    ("No me llegan las notificaciones al celular, pero la app funciona bien.",
     {"intencion": "falla_tecnica", "prioridad": "baja"}),
    ("Quiero cancelar mi suscripcion hoy mismo para que no me vuelvan a cobrar.",
     {"intencion": "cancelacion", "prioridad": "alta"}),
]

def construir_examples(ejemplos_raw: list[tuple[str, dict]]) -> list[types.TuningExample]:
    return [
        types.TuningExample(text_input=texto, output=json.dumps(salida, ensure_ascii=False))
        for texto, salida in ejemplos_raw
    ]


def chequear_balance(ejemplos_raw: list[tuple[str, dict]], clave: str) -> Counter:
    categorias = Counter(salida[clave] for _, salida in ejemplos_raw)
    return categorias


def validar_dataset(
    examples: list[types.TuningExample], claves_esperadas: tuple[str, ...]
) -> list[str]:
    problemas = []
    vistos = set()
    for i, ej in enumerate(examples):
        if not ej.text_input or not ej.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ej.output or not ej.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        if ej.text_input in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(ej.text_input)
        try:
            salida = json.loads(ej.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')
    return problemas


def esperar_a_que_termine(
    client: genai.Client, nombre_trabajo: str, intervalo_segundos: int = 30
) -> types.TuningJob:
    estados_finales = {
        types.JobState.JOB_STATE_SUCCEEDED,
        types.JobState.JOB_STATE_FAILED,
        types.JobState.JOB_STATE_CANCELLED,
        types.JobState.JOB_STATE_PARTIALLY_SUCCEEDED,
    }
    while True:
        trabajo = client.tunings.get(name=nombre_trabajo)
        print(f"estado actual: {trabajo.state}")
        if trabajo.state in estados_finales:
            return trabajo
        time.sleep(intervalo_segundos)


def enviar_trabajo(examples: list[types.TuningExample]) -> None:
    load_dotenv()
    client = genai.Client()
    dataset = types.TuningDataset(examples=examples)
    config = types.CreateTuningJobConfig(
        tuning_mode=types.TuningMode.TUNING_MODE_PEFT_ADAPTER,
        adapter_size=types.AdapterSize.ADAPTER_SIZE_FOUR,
        epoch_count=5,
        tuned_model_display_name="clasificador-tickets-soporte",
    )
    try:
        trabajo = client.tunings.tune(
            base_model=MODELO_BASE,
            training_dataset=dataset,
            config=config,
        )
        print(trabajo)
    except Exception as error:
        print("No se pudo crear el trabajo de tuning:", error)
        return

    print("nombre del trabajo:", trabajo.name)
    try:
        esperar_a_que_termine(client, trabajo.name, INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("Interrumpido. El trabajo sigue en la nube; para cancelarlo usa")
        print(f'client.tunings.cancel(name="{trabajo.name}")')


def titulo(texto: str) -> None:
    print("=" * 60)
    print(texto)
    print("=" * 60)


def main() -> None:
    examples = construir_examples(EJEMPLOS_RAW)

    titulo("PASO 1: balance de MI dataset")
    balance = chequear_balance(EJEMPLOS_RAW, CLAVE_BALANCE)
    for categoria, cuenta in balance.most_common():
        print(f"{categoria}: {cuenta}")
    print()

    titulo("PASO 2: validacion de MI dataset")
    problemas = validar_dataset(examples, CLAVES_ESPERADAS)
    print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
    for p in problemas:
        print(" -", p)
    print()

    titulo("PASO 3: rompo un ejemplo a proposito")
    # str() de un diccionario usa comillas simples: Python lo acepta, json.loads no
    examples_rotos = list(examples)
    examples_rotos[3] = types.TuningExample(
        text_input=examples[3].text_input,
        output=str(EJEMPLOS_RAW[3][1]),
    )
    problemas_rotos = validar_dataset(examples_rotos, CLAVES_ESPERADAS)
    print(f"{len(examples_rotos)} ejemplos, {len(problemas_rotos)} problemas encontrados")
    for p in problemas_rotos:
        print(" -", p)
    print()

    titulo("PASO 4: trabajo de tuning")
    if problemas:
        print("No se envia nada: corrige primero los problemas del PASO 2.")
    elif ENVIAR_TRABAJO:
        enviar_trabajo(examples)
    else:
        print("(ENVIAR_TRABAJO = False; no se envio ningun trabajo)")


if __name__ == "__main__":
    main()