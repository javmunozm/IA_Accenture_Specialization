import json

from src.registro_rag import ARCHIVO_REGISTROS

with open(ARCHIVO_REGISTROS, encoding="utf-8") as f:
    for linea in f:
        r = json.loads(linea)
        tokens_entrada = r["tokens"]["input_tokens"] if r["tokens"] else None
        etapas = " ".join(f"{etapa}0{ms}" for etapa, ms in r["tiempos_ms"].items())
        print(f"k={r['k']}  input_tokens={tokens_entrada}  total={r['tiempo_total_ms']} ms  "
              f"costo={r['costo_usd']}  {r['pregunta'][:35]}")
        print(f"    {etapas}")