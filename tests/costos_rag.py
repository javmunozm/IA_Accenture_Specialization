import time
from contextlib import contextmanager

tiempos = {}

@contextmanager
def medir(etapa):
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio

from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_chroma import Chroma

corpus = [
    "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
    "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un ValueError.",
    "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por cada 1000 tokens.",
]

pregunta = "Que hace el cliente si hay un TimeoutError?"

embeddings_fake = DeterministicFakeEmbedding(size=16)
vectorstore = Chroma.from_texts(
    corpus, embedding=embeddings_fake, collection_name="demo_costos"
)

tiempos.clear()

with medir("embed_query"):
    vector = embeddings_fake.embed_query(pregunta)

with medir("busqueda_vectorial"):
    chunks = vectorstore.similarity_search(pregunta, k=3)

for etapa, segundos in tiempos.items():
    print(f"{etapa}: {segundos * 1000:.2f} ms")
print(f"total medido: {sum(tiempos.values()) * 1000:.2f} ms")

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""

contexto = "\n\n".join([
    "[1] El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente. Los errores",
    "[2] errores de autenticacion nunca se reintentan: fallan de inmediato con un ValueError.",
    "[3] El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por",
])

prompt_con_rag = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)


def aprox_tokens(texto):
    """Aproximacion habitual para espanol/ingles: ~4 caracteres por token."""
    return len(texto) // 4


print("pregunta sola:")
print("  caracteres:", len(pregunta))
print("  tokens aprox:", aprox_tokens(pregunta))
print()
print("prompt RAG completo (con contexto de 3 chunks):")
print("  caracteres:", len(prompt_con_rag))
print("  tokens aprox:", aprox_tokens(prompt_con_rag))
print()
print("factor de crecimiento:", round(len(prompt_con_rag) / len(pregunta), 1), "x")


def calcular_costo(tokens_entrada, tokens_salida, tarifa_entrada_x1000, tarifa_salida_x1000):
    costo_entrada = (tokens_entrada / 1000) * tarifa_entrada_x1000
    costo_salida = (tokens_salida / 1000) * tarifa_salida_x1000
    return costo_entrada + costo_salida


# valores de ejemplo, NO tarifas reales vigentes: consulta la documentacion oficial
TARIFA_ENTRADA_X1000 = 0.0001
TARIFA_SALIDA_X1000 = 0.0004

tokens_salida_estimados = 60  # el largo de la respuesta no cambia por usar RAG o no

tokens_sin_rag = aprox_tokens(pregunta)
tokens_con_rag = aprox_tokens(prompt_con_rag)

costo_sin_rag = calcular_costo(tokens_sin_rag, tokens_salida_estimados, TARIFA_ENTRADA_X1000, TARIFA_SALIDA_X1000)
costo_con_rag = calcular_costo(tokens_con_rag, tokens_salida_estimados, TARIFA_ENTRADA_X1000, TARIFA_SALIDA_X1000)

print(f"costo sin RAG: ${costo_sin_rag:.6f}")
print(f"costo con RAG: ${costo_con_rag:.6f}")
print(f"aumento: {costo_con_rag / costo_sin_rag:.2f}x")