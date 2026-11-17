# Registro del ensayo funcional del Gate 2

## 16-11-2026

### Encontrado
`filtrar_documentos_sospechosos` de `src/logging_rag.py` (Bloque 31) lee
`d.contenido` y `d.fuente` (namedtuple `Documento`); el retriever real
devuelve `Document` de LangChain con `page_content` y `metadata`.

Conectados directo:
> `AttributeError: 'Document' object has no attribute 'contenido'`

### Corregido
- En `logging_rag.py`, el puente es `recuperar_documentos` (convierte cada
  `Document` en `Documento`).
- `tests/ensayo_gate2.py` filtra sobre `d.page_content`.

### Resultado
`py -m tests.ensayo_gate2` termina con:
> Ensayo completo: todas las verificaciones pasaron

## 16-11-2026 (servicio integrado)

### Encontrado
Las piezas corrian por separado: no habia un servicio que indexara,
recuperara, filtrara, citara, generara, registrara y supervisara junto.

### Corregido
`src/servicio_rag.py`, con el filtro sobre `d.page_content`.

### Resultado
`"s" | py -m src.servicio_rag --simulado | Select-String "Fuentes:"` imprime:
> Fuentes: [1] agente

Corrida real (`py -m src.servicio_rag`):
- Respuesta con `Fuentes: [1] reintentos, [2] reintentos, [3] errores`.
- Los 4 eventos con un solo `trace_id` (`trace-86d29049`), solo con `pregunta_len`, conteos, tokens, costo y tiempos.
- Consumo: 197 tokens de entrada, 138 de salida, 0.0004041 USD; recuperacion 1297.9 ms, generacion 10306.8 ms.
- Pausa de supervision (`pausado, pendiente: ...`) antes de la decision; con `s`: `version 849809fdf663 activada` y estado final `'aprobado': True`.
- Captura: `docs/prueba_bloque_S1_servicio.png`.
- `Proceso terminado sin errores.`, sin traceback; `$LASTEXITCODE`: 0.

## 16-11-2026 (trace_id en el servicio)

### Encontrado
`py -m src.servicio_rag --simulado` terminaba con:
> `TypeError: '_contextvars.ContextVar' object is not callable`

`evento()` llamaba `trace_id_var()` en vez de `trace_id_var.get()`.
`py -m pytest src/test_gate2.py` daba 4 passed porque la version del
paso 2 prueba las piezas sueltas y no importa `servicio_rag.py`.

### Corregido
`trace_id_var.get()` en `evento()`.

### Resultado
`py -m src.servicio_rag --simulado` termina con:
> Proceso terminado sin errores.

Todos los eventos de la consulta llevan el mismo `trace_id`.

## 16-11-2026 (indice incremental)

### Encontrado
`indexar_corpus` borra la carpeta (`shutil.rmtree`) y re-indexa todo en
cada corrida (sin actualizacion incremental).

### Corregido
`actualizar_indice` en `servicio_rag.py` agrega solo los ids que faltan.

### Resultado
- `--simulado`, con un indice vacio: `Indice: indice_creado (12 chunks nuevos)`
- Corrida real, con `vectorstore/` ya indexado: `Indice: indice_reutilizado (0 chunks nuevos)`, sin llamadas de embeddings para indexar.

## 16-11-2026 (pregunta en los registros)

### Encontrado
`registro_rag.py` guarda la pregunta completa en
`docs/registros_latencia_costo.jsonl` (5 registros con el campo `"pregunta"`).

### Corregido
`servicio_rag.py` registra solo `pregunta_len`; el riesgo ya estaba en
`matriz_riesgos.py` con su punto de supervision.

### Resultado
- `test_3_logs_sin_contenido_crudo` pasa.
- `"n" | py -m src.servicio_rag --simulado "Que pasa si mi conexion tarda? Mi correo es ana.perez@example.com" | Select-String "ana.perez"`: no imprime nada.
- `Select-String -Path docs\*.jsonl -Pattern "ana.perez"`: no imprime nada.

## 16-11-2026 (corrida final)

### Resultado
- `py -m pytest src -q`: 103 passed
- `py -m src.verificar_entorno`: Entorno listo para la corrida final
- `git check-ignore .env vectorstore`: imprime `.env` y `vectorstore`