def precision_at_k(ids_recuperados, ids_relevantes):
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)

def recall_at_k(ids_recuperados, ids_relevantes):
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)

def f1(precision, recall):
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)

corpus = {
    "doc0": "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
    "doc1": "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un ValueError.",
    "doc2": "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por cada 1000 tokens.",
    "doc3": "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, segun la descripcion de cada una.",
    "doc4": "Las pruebas unitarias del cliente usan mocks, de forma que la suite completa corre en menos de un segundo.",
}

pregunta = "que hace el cliente si una llamada tarda demasiado?"
ids_relevantes = {"doc0"} # solo este responde la pregunta
ids_recuperados = ["doc2", "doc0", "doc4"] # lo que devolvio k con k=3
ranked = ["doc2", "doc4", "doc0", "doc1", "doc3"] # va de - a +

print("precision@3:", precision_at_k(ids_recuperados, ids_relevantes))
print("recall@3:", recall_at_k(ids_recuperados, ids_relevantes))

print()
for k in range(1, 6):
    sub = ranked[:k]
    p = precision_at_k(sub, ids_relevantes)
    r = recall_at_k(sub, ids_relevantes)
    print(f"k={k}: precision ={p:.3f} recall={r:.3f} recuperados={sub}")

print()
for k in range(1, 6):
    sub =ranked[:k]
    p = precision_at_k(sub, ids_relevantes)
    r = recall_at_k(sub, ids_relevantes)
    print(f"k={k}: F1={f1(p, r):.3f}")
