# Límites de autonomía: agente de soporte de la mesa de ayuda

Agente definido en `src/agente_completo.py` (Bloques 21-23). Trazas reales en `docs/trazas_agente.jsonl`.

## Herramientas y nivel de riesgo

- consultar_ticket_con_historial: bajo (solo lee el estado de un ticket, no modifica nada)
- buscar_solucion_frecuente: bajo (solo devuelve soluciones conocidas, no ejecuta ninguna acción externa)
- generar_reembolso: alto (en producción movería dinero de forma irreversible; en esta versión es simulado y solo
  devuelve un texto). Requiere aprobación humana.

En esta versión no hay herramientas de riesgo medio (escritura reversible).

## Herramientas que requieren aprobación humana

- generar_reembolso: un reembolso no se puede deshacer y tiene un costo directo. Antes de ejecutarlo, `esperar_aprobacion` pide confirmación (s/n) con un límite de 300 segundos; si nadie responde a tiempo, el resultado es "no aprobado". Cada decisión, aprobada o no, queda en `registro_aprobaciones` con la herramienta, los argumentos y el momento.
- Las herramientas de riesgo bajo no piden aprobación: se revisan después en la traza, para no diluir la atención de quien aprueba.
- Limitaciones conocidas: la aprobación se pide por consola (no hay panel de aprobaciones) y `registro_aprobaciones` vive en memoria, así que se pierde al cerrar el programa. La traza no guarda la decisión: solo se deduce por la observación ("generado" o "no aprobado"). Tampoco hay tope de monto ni se valida que el pedido exista.

## Revisión de trazas

- Frecuencia: una muestra de 10 trazas cada semana, más todas las trazas donde aparezca `generar_reembolso`.
- Qué se busca:
  - La misma herramienta invocada varias veces seguidas (`marcar_repeticiones_sospechosas` marca las candidatas).
  - Un `generar_reembolso` cuya observación diga "generado" sin que alguien recuerde haberlo aprobado.
  - Una respuesta final que afirma algo que ninguna observación devolvió (por ejemplo, un estado de ticket inventado).
  - Una herramienta usada en preguntas que no la necesitan (descripción demasiado amplia).

## Lo que mostró la traza

  Corrida de `py -m src.agente_completo` con 3 interacciones registradas en `docs/trazas_agente.jsonl`:

  - cliente_123, "¿Como va mi ticket TK1001": usó `consultar_ticket_con_historial` una vez, con `incluir_historial:true`. Correcto.
  - cliente_123, "¿Como cambio mi contraseña?": usó `buscar_solucion_frecuente` una vez. Correcto.
  - cliente_456, "Reembolso el pedido P1 por $100": usó `generar_reembolso` (P1, 100), se aprobó por consola y la observación fue "Reembolso de $100.0 generado para el pedido P1."
  - `marcar_repeticiones_sospechosas` no marcó ninguna sesión: ninguna herramienta se repitió.
  - Hallazgo: en el reembolso, la respuesta final dice "generado exitosamente (pendiente de aprobación final)", pero la aprobación ya se había dado. El agente agregó un estado que ninguna observación devolvió. Es el caso del punto 4 del plan de abajo (ajustar el prompt del sistema).

## Qué hacer ante un comportamiento inesperado

1. Si `generar_reembolso` actuó sin aprobación o con argumentos equivocados: quitarla de `HERRAMIENTAS` en `src/agente_completo.py` hasta corregirla.
2. Guardar la línea de la traza (session_id y entrada) que muestra el problema.
3. Si eligió mal la herramienta o la usó sin necesidad: reescribir el docstring de esa herramienta según la pregunta que debería dispararla.
4. Si inventó datos: ajustar el prompt del sistema para que responda solo con lo que devuelven las herramientas.
5. Agregar una prueba con el modelo simulado que reproduzca el caso y correr `py -m pytest src/` antes de volver a habilitar la herramienta.