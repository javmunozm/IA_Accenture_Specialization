# Decision de personalizacion

## 1. El problema
El clasificador de tickets de soporte no siempre devuelve la intencion y la prioridad en el formato JSON esperado.

## 2. Resultado del metodo de decision
- PEFT: 3 puntos
- RAG: 2 puntos
- Fine-tuning completo: 1 puntos

## 3. Tecnica elegida y por que
Elijo PEFT porque el problema es de formato (la intencion y la prioridad no siempre salen en el Json) y no de informacion que cambie.
PEFT corrige el formato entrenando pocos parametros, es mas barato que fine-tuning. Ademas que depende de la sola respuesta de problema_de_formato_o_tono que se apoya en solo 3 respuestas de clasificar_mensaje, para este caso si con 20 respuesta bajara del 15%, entonces se recomendaria RAG

## 4. Que necesitarias para ejecutarla
Tengo 12 ejemplos etiquetados en 5 intenciones (2 a 3 por intencion) y necesito  doscientas, asi que faltan 200-n, para este caso n =12,  asi que 188, multiplaco por el tiempo que son 5 minutos por ejemplo son 15.67 hora, aprox $391.67 a $25 la hora. Ademas se necesita una cuenta con tuning que no se encuentra en la API gratuita y no me permite entrenar, asi que no necesitaria un corpus para indexar por que no usa rag..