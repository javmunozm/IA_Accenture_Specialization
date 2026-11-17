# Miniaplicación de consumo de Gemini — Especialización en Desarrollo con IA Generativa (Accenture)

Proyecto en Python que consume la API de Google Gemini. En el Módulo 1 arma y envía peticiones REST con `requests`, maneja errores, mide latencia y costo por modelo, separa el prompt de sistema de la pregunta del usuario y obtiene salidas JSON validadas. En el Módulo 2 agrega un servicio RAG que indexa un corpus, responde citando sus fuentes, registra cada consulta con un `trace_id` y pide aprobación humana antes de activar una versión nueva del prompt.

Corresponde a las entregas del **Gate 1 — Habilitación técnica** (Módulo 1) y del **Gate 2 — Integración y orquestación** (Módulo 2).

## Verificación rápida (punto de entrada)

Después de la [instalación](#instalación), estos son los comandos principales para verificar cada entrega, desde la raíz del proyecto:

**Gate 2 (Módulo 2): servicio RAG**

```powershell
py -m src.verificar_entorno                 # debe terminar con "Entorno listo para la corrida final"
py -m src.servicio_rag                      # consulta de punta a punta (2 llamadas a la API)
py -m pytest src/test_gate2.py -v           # los 4 criterios no compensables, sin API
```

Si el índice no existe todavía, antes ejecuta `py -m src.indexar_corpus` (ver [Módulo 2](#módulo-2-servicio-rag-gate-2)).

**Gate 1 (Módulo 1): consumo de Gemini**

```powershell
py -m src.consumir_gemini                   # módulo principal: entrada vacía (error controlado) y una válida
py -m src.prueba_salida_json                # salida JSON forzada y validada
```

El resto de los scripts está en [Scripts principales](#scripts-principales-módulo-1).

## Requisitos

- Python 3.10 o superior (desarrollado con Python 3.14).
- Git.
- Una API key de Gemini, que se obtiene en [Google AI Studio](https://aistudio.google.com/apikey).

## Instalación

Todos los comandos se ejecutan desde la raíz del proyecto.

**Windows (PowerShell)**

```powershell
git clone <url-de-este-repositorio> accenture
cd accenture
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

**macOS / Linux**

```bash
git clone <url-de-este-repositorio> accenture
cd accenture
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Después abre el archivo `.env` y reemplaza `tu_api_key_aqui` por tu API key real:

```
GEMINI_API_KEY=tu_api_key_aqui
```

El archivo `.env` está excluido en `.gitignore` y nunca se sube al repositorio.

## Cómo ejecutar

Los scripts importan módulos con la forma `from src.consumir_gemini import ...`, por eso **se ejecutan desde la raíz y con `-m`**, usando puntos en vez de barras y sin `.py`. (En macOS/Linux, cambia `py` por `python3`.)

```powershell
py -m src.prueba_salida_json
```

Si se ejecuta el archivo directamente (con el botón ▶ de VS Code o con `py src/prueba_salida_json.py`), aparece `ModuleNotFoundError: No module named 'src'`.

### Scripts principales (Módulo 1)

- `py -m src.consumir_gemini` (bloques 5–7): prueba la conexión con una entrada vacía (error controlado) y una válida.
- `py -m src.prueba_costo` (bloque 8): hace una petición real y calcula su costo en USD a partir de `usageMetadata`.
- `py -m src.comparar_modelos` (bloque 9): compara latencia y costo de dos modelos, y guarda sus respuestas en `docs/respuestas_<modelo>.txt`.
- `py -m src.prueba_system_prompt` (bloque 10): prueba el prompt de sistema separado (respuesta en máximo 3 oraciones).
- `py -m src.prueba_salida_json` (bloque 10): obtiene una clasificación en JSON forzado con `responseSchema` y la valida.
- `py -m prompts.test_consistencia` (bloque 10): corre cada prompt del banco 3 veces y guarda el resultado en `prompts/registro_resultados.json`.

## Módulo principal: `consumir_gemini.py`

Ubicado en `src/`. Todas las piezas del Módulo 1 lo importan.

- `armar_peticion(pregunta, modelo, system_instruction, response_schema)`: valida la entrada, lee la API key del `.env` y arma URL, headers y body. Los dos últimos parámetros son opcionales.
- `enviar_peticion(url, headers, body)`: envía la petición con timeout y convierte errores de red y de HTTP en mensajes claros.
- `extraer_texto(datos)`: saca el texto generado de la respuesta de la API.
- `parsear_respuesta_json(texto, claves_requeridas)`: limpia bloques de markdown, interpreta el JSON y valida que tenga las claves esperadas.
- `calcular_costo(datos, precio_entrada, precio_salida)`: calcula el costo en USD de una petición según los tokens usados.

Los errores se lanzan como `ValueError` (entrada o respuesta inválida) o `RuntimeError` (problemas con el servicio), y cada script los captura para no terminar con un traceback.

## Banco de prompts

La carpeta `prompts/` contiene:

- `banco.py`: tres prompts para una mesa de ayuda (clasificar el mensaje, extraer datos y hacer un resumen corto), cada uno con su prompt de sistema, un ejemplo de entrada, las claves esperadas y su `response_schema`.
- `test_consistencia.py`: ejecuta cada prompt 3 veces contra la API real y cuenta cuántas respuestas fueron JSON válido con la estructura correcta.
- `registro_resultados.json`: resultado de la última ejecución, generado automáticamente por el script.

## Módulo 2: servicio RAG (Gate 2)

Servicio que indexa el corpus del proyecto, recupera los fragmentos relevantes, descarta los que traen inyección de prompt, responde citando la fuente, registra cada etapa con un `trace_id` (sin el texto de la pregunta), mide costo y latencia, y pide aprobación humana antes de activar una versión nueva del prompt.

### 1. Instalar

Igual que la sección [Instalación](#instalación): entorno virtual, `pip install -r requirements.txt` y `GEMINI_API_KEY` en `.env`.

### 2. Indexar el corpus (una vez, 1 llamada de embeddings)

```powershell
py -m src.indexar_corpus
```

Crea el índice persistido en `vectorstore/` (colección `corpus_miniapp`, ignorado por git). El servicio lo reutiliza y solo agrega los fragmentos nuevos.

### 3. Verificar el entorno

```powershell
py -m src.verificar_entorno
```

Debe terminar con `Entorno listo para la corrida final`.

### 4. Consulta de punta a punta

```powershell
py -m src.servicio_rag                      # real: 2 llamadas a la API
py -m src.servicio_rag "tu pregunta"        # otra pregunta
py -m src.servicio_rag --simulado           # sin API ni costo (embeddings y modelo falsos)
```

Al final pide aprobar (`s`/`n`) la versión nueva del prompt: es el punto de supervisión humana.

### 5. Pruebas (sin API)

```powershell
py -m pytest src -q
py -m pytest src/test_gate2.py -v           # los 4 criterios no compensables del Gate 2
```

### Piezas del Módulo 2

- `src/indexar_corpus.py` (bloques 24–25): chunking, embeddings e índice Chroma persistido.
- `src/recuperacion.py` (bloque 26): prompt con contexto y citas `[n]`.
- `src/evaluacion_recuperacion.py` (bloque 27): precisión y exhaustividad de la recuperación.
- `src/registro_rag.py` (bloque 28): latencia por etapa y costo por consulta.
- `src/decision.py` (bloques 29–30): decisión RAG / fine-tuning / PEFT.
- `src/logging_rag.py` (bloque 31): logging JSON con `trace_id`, consumo y filtro de inyección.
- `src/registro_prompts.py`, `src/grafo_supervision.py` y `src/matriz_riesgos.py` (bloque 32): versionado de prompts, supervisión con `interrupt` y matriz de riesgos.
- `src/servicio_rag.py` (Gate 2): el servicio integrado.

## Estructura del proyecto

```
.
├── docs/                    Documentación, decisiones y evidencias
├── prompts/                 Banco de prompts y su prueba de consistencia
├── src/                     Código de la miniaplicación (estructura plana)
│   ├── consumir_gemini.py   Módulo principal del Módulo 1 (bloques 5–7)
│   ├── servicio_rag.py      Servicio RAG integrado (Gate 2)
│   ├── test_*.py            Pruebas unitarias (pytest, sin API)
│   └── ...                  Resto de las piezas (ver las listas de arriba)
├── tests/                   Pruebas exploratorias y ensayo del Gate 2
├── vectorstore/             Índice Chroma persistido (se genera, ignorado por git)
├── .env.example             Plantilla de variables de entorno (sin valores reales)
├── .gitignore
├── requirements.txt
└── README.md
```

## Documentación (`docs/`)

- `diagrama_arquitectura.png`: diagrama de arquitectura de la miniaplicación.
- `desicion_arquitectura.md`: decisión de arquitectura.
- `comparacion_modelos.md`: comparación entre `gemini-3.5-flash-lite` y `gemini-3.7-flash` (latencia, costo y calidad) y modelo elegido.
- `mediciones.txt`: mediciones de latencia y costo.
- `respuestas_<modelo>.txt`: respuestas de cada modelo a las preguntas de calidad.
- `decision_personalizacion.md`: decisión fundamentada entre RAG, fine-tuning y PEFT.
- `registro_ensayo_gate2.md`: qué se encontró y corrigió en el ensayo funcional del Gate 2.
- `evidencia_*.png` y `prueba_bloque_*.png`: capturas de ejecución de cada bloque.

## Pruebas exploratorias (fuera del programa)

Pruebas propias, hechas durante el desarrollo, que se mantienen como evidencia:

- `tests/test_gemini.py`: verifica que `GEMINI_API_KEY` se carga desde el `.env`. Imprime `True` o `False`, nunca la clave.
- `tests/prueba_bloque8.py`: petición de prueba que imprime el texto generado y el uso de tokens.

```powershell
py -m tests.test_gemini
py -m tests.prueba_bloque8
```

## Seguridad

- Ninguna credencial está escrita en el código: la API key se lee desde `.env` con `python-dotenv`.
- `.env` está excluido en `.gitignore`; solo se versiona `.env.example`, sin valores reales.
- La API key se envía en el header `x-goog-api-key`, no en la URL.

## Registro del ensayo de instalación limpia

Fechas en formato DD-MM-AAAA.

### 19-10-2026

- **Encontrado:** `requirements.txt` generado con `pip freeze` incluía paquetes que el proyecto no usa: restos de una librería no oficial desinstalada (`python-gemini-api`) y paquetes solo para Windows (`pywin32`, `WMI`), que harían fallar la instalación en macOS/Linux.
- **Corregido:** `requirements.txt` reducido a `python-dotenv` y `requests`; `.venv` recreado desde cero.
- **Resultado:** los scripts principales corren con el entorno nuevo.

### 19-10-2026

- **Encontrado:** no existía `.env.example`.
- **Corregido:** se creó con la variable `GEMINI_API_KEY` sin valor real.
- **Resultado:** quien clone el repositorio sabe qué variable configurar.

### Pendiente

- Ensayo completo: clonar en una carpeta nueva y seguir solo este README.

## Reglas del programa

- Ningún secreto (contraseña, llave de API, token) va escrito en el código ni en ningún archivo que se suba al repositorio.
- Cada proyecto tiene su propio entorno virtual.
- Todo el trabajo entregado vive en un repositorio de GitHub.
