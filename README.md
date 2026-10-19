# Miniaplicación de consumo de Gemini — Especialización en Desarrollo con IA Generativa (Accenture)

Módulo en Python que consume la API REST de Google Gemini con `requests`. Arma y envía peticiones con manejo de errores, mide latencia y costo por modelo, separa el prompt de sistema de la pregunta del usuario y obtiene salidas JSON validadas. Incluye un banco de prompts con su prueba de consistencia.

Corresponde a la entrega del **Gate 1 — Habilitación técnica** (Módulo 1).

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

Los scripts importan módulos con la forma `from src.Modulo_1...`, por eso **se ejecutan desde la raíz y con `-m`**, usando puntos en vez de barras y sin `.py`. (En macOS/Linux, cambia `py` por `python3`.)

```powershell
py -m src.Modulo_1.Bloque_10.prueba_salida_json
```

Si se ejecuta el archivo directamente (con el botón ▶ de VS Code o con `py src/Modulo_1/...py`), aparece `ModuleNotFoundError: No module named 'src'`.

### Scripts principales

| Comando | Qué hace | Bloque |
| --- | --- | --- |
| `py -m src.Modulo_1.Bloque_5_6_7.consumir_gemini` | Prueba la conexión: una entrada vacía (error controlado) y una válida | 5–7 |
| `py -m src.Modulo_1.Bloque_8_9.prueba_costo` | Hace una petición real y calcula su costo en USD a partir de `usageMetadata` | 8 |
| `py -m src.Modulo_1.Bloque_8_9.comparar_modelos` | Compara latencia y costo de dos modelos, y guarda sus respuestas en `docs/respuestas_<modelo>.txt` | 9 |
| `py -m src.Modulo_1.Bloque_10.prueba_system_prompt` | Prueba el prompt de sistema separado (respuesta en máximo 3 oraciones) | 10 |
| `py -m src.Modulo_1.Bloque_10.prueba_salida_json` | Obtiene una clasificación en JSON forzado con `responseSchema` y la valida | 10 |
| `py -m prompts.test_consistencia` | Corre cada prompt del banco 3 veces y guarda el resultado en `prompts/registro_resultados.json` | 10 |

## Módulo principal: `consumir_gemini.py`

Ubicado en `src/Modulo_1/Bloque_5_6_7/`. Todas las demás piezas lo importan.

| Función | Responsabilidad |
| --- | --- |
| `armar_peticion(pregunta, modelo, system_instruction, response_schema)` | Valida la entrada, lee la API key del `.env` y arma URL, headers y body. Los dos últimos parámetros son opcionales. |
| `enviar_peticion(url, headers, body)` | Envía la petición con timeout y convierte errores de red y de HTTP en mensajes claros. |
| `extraer_texto(datos)` | Saca el texto generado de la respuesta de la API. |
| `parsear_respuesta_json(texto, claves_requeridas)` | Limpia bloques de markdown, interpreta el JSON y valida que tenga las claves esperadas. |
| `calcular_costo(datos, precio_entrada, precio_salida)` | Calcula el costo en USD de una petición según los tokens usados. |

Los errores se lanzan como `ValueError` (entrada o respuesta inválida) o `RuntimeError` (problemas con el servicio), y cada script los captura para no terminar con un traceback.

## Banco de prompts

La carpeta `prompts/` contiene:

- `banco.py`: tres prompts para una mesa de ayuda (clasificar el mensaje, extraer datos y hacer un resumen corto), cada uno con su prompt de sistema, un ejemplo de entrada, las claves esperadas y su `response_schema`.
- `test_consistencia.py`: ejecuta cada prompt 3 veces contra la API real y cuenta cuántas respuestas fueron JSON válido con la estructura correcta.
- `registro_resultados.json`: resultado de la última ejecución, generado automáticamente por el script.

## Estructura del proyecto

```
.
├── docs/                    Documentación, decisiones y evidencias
├── prompts/                 Banco de prompts y su prueba de consistencia
├── src/
│   └── Modulo_1/
│       ├── Bloque_5_6_7/    consumir_gemini.py (módulo principal)
│       ├── Bloque_8_9/      Costo y comparación de modelos
│       └── Bloque_10/       Prompt de sistema y salida JSON
├── tests/                   Pruebas exploratorias
├── .env.example             Plantilla de variables de entorno (sin valores reales)
├── .gitignore
├── requirements.txt
└── README.md
```

## Documentación (`docs/`)

- `diagrama_arquitectura.png`: diagrama de arquitectura de la miniaplicación.
- `decision_arquitectura.md`: decisión de arquitectura.
- `comparacion_modelos.md`: comparación entre `gemini-3.5-flash-lite` y `gemini-3.7-flash` (latencia, costo y calidad) y modelo elegido.
- `mediciones.txt`: mediciones de latencia y costo.
- `respuestas_<modelo>.txt`: respuestas de cada modelo a las preguntas de calidad.
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

| Fecha | Encontrado | Corregido | Resultado |
| --- | --- | --- | --- |
| 2026-10-19 | `requirements.txt` generado con `pip freeze` incluía paquetes que el proyecto no usa: restos de una librería no oficial desinstalada (`python-gemini-api`) y paquetes solo para Windows (`pywin32`, `WMI`), que harían fallar la instalación en macOS/Linux. | `requirements.txt` reducido a `python-dotenv` y `requests`; `.venv` recreado desde cero. | Los scripts principales corren con el entorno nuevo. |
| 2026-10-19 | No existía `.env.example`. | Se creó con la variable `GEMINI_API_KEY` sin valor real. | Quien clone el repositorio sabe qué variable configurar. |
| _pendiente_ | Ensayo completo: clonar en una carpeta nueva y seguir solo este README. | | |

## Reglas del programa

- Ningún secreto (contraseña, llave de API, token) va escrito en el código ni en ningún archivo que se suba al repositorio.
- Cada proyecto tiene su propio entorno virtual.
- Todo el trabajo entregado vive en un repositorio de GitHub.