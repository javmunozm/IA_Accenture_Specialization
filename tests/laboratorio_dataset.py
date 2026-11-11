from google.genai import types

from src.dataset_tuning import chequear_balance, construir_examples, validar_dataset

CLAVES_ESPERADAS = ("categoria", "accion_sugerida")


ejemplos_raw = [   # ->  Errores reales de los Bloques 24 y 25 -> JSON con categoria y accion_sugerida.
    ("TimeoutError: la conexion tardo mas de 10 segundos en responder.",
     {"categoria": "red", "accion_sugerida": "reintentar con backoff exponencial"}),
    ("ValueError: la clave de API no tiene el formato esperado.",
     {"categoria": "autenticacion", "accion_sugerida": "revisar GEMINI_API_KEY, no reintentar"}),
    ("429 RESOURCE_EXHAUSTED: se supero el limite de peticiones por minuto.",
     {"categoria": "cuota", "accion_sugerida": "esperar y reintentar, con backoff"}),
    ("API key not valid. Please pass a valid API key.",
     {"categoria": "autenticacion", "accion_sugerida": "revisar GEMINI_API_KEY, no reintentar"}),
    ("RuntimeError: Your system has an unsupported version of sqlite3.",
     {"categoria": "entorno", "accion_sugerida": "instalar pysqlite3-binary"}),
    ("ModuleNotFoundError: No module named langchain_chroma.",
     {"categoria": "entorno", "accion_sugerida": "instalar dependencia faltante"}),
    ("PermissionError al crear la carpeta del vector store.",
     {"categoria": "entorno", "accion_sugerida": "revisar permisos de escritura"}),
    ("InvalidArgumentError: Collection expecting embedding with dimension of 768, got 1536.",
     {"categoria": "consistencia_indice", "accion_sugerida": "reindexar con el mismo modelo de embeddings"}),
]


def titulo(texto):
    print("=" * 60)
    print(texto)
    print("=" * 60)


titulo("PASO 1: construir y validar el dataset")
examples = construir_examples(ejemplos_raw)
print(len(examples), "ejemplos construidos")
problemas = validar_dataset(examples, CLAVES_ESPERADAS)
print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
for p in problemas:
    print(" -", p)
print()

titulo("PASO 2: balance entre categorias")
balance = chequear_balance(ejemplos_raw, "categoria")
for categoria, cuenta in balance.most_common():
    print(f"{categoria}: {cuenta}")
maximo = max(balance.values())
minimo = min(balance.values())
print(f"razon max/min: {maximo / minimo:.1f}x")
print()

titulo("PASO 3: probar el validador con un dataset roto a proposito")
examples_rotos = examples + [
    types.TuningExample(text_input="", output='{"categoria": "red"}'),
    types.TuningExample(text_input=ejemplos_raw[0][0], output="no es json"),
]
problemas2 = validar_dataset(examples_rotos, CLAVES_ESPERADAS)
print(f"{len(examples_rotos)} ejemplos, {len(problemas2)} problemas encontrados")
for p in problemas2:
    print(" -", p)
print()

titulo("PASO 4: estados de un trabajo de tuning + config PEFT (sin enviar)")
for estado in types.JobState:
    print(" ", estado)
config = types.CreateTuningJobConfig(
    tuning_mode=types.TuningMode.TUNING_MODE_PEFT_ADAPTER,
    adapter_size=types.AdapterSize.ADAPTER_SIZE_FOUR,
    epoch_count=5,
    tuned_model_display_name="clasificador-errores-cliente",
)
print("tuning_mode:", config.tuning_mode)
print("adapter_size:", config.adapter_size)
print("epoch_count:", config.epoch_count)
print("(configuracion armada; no se envio ningun trabajo)")