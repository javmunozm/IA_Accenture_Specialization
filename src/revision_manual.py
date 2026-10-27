import json
import os

ARCHIVO_REVISION = "docs/revision_manual.json"
VALORES_PERMITIDOS = {
    "correccion_factual": {"si", "no", "parcial"}, #¿Todo dato verificable (fechas, nombres, cifras) coincide con la referencia?
    "completitud": {"si", "no", "parcial"},#¿La respuesta cubre lo que cubre la referencia, o falta algo importante?
    "contradiccion": {"si", "no"},#¿Afirma lo contrario de algo de la referencia, aunque sea con una palabra (como una negacion)?
}


REVISION_MANUAL = [
   
    {
        "consulta": "que es python?",
        "f1": 0.37,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta y completa; F1 bajo porque agrega detalles que no estan en la referencia y 'programacion' sin tilde no coincide con la palabra con tilde",
    },
    {
        "consulta": "cuantos bits son un byte?",
        "f1": 0.0,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta y completa, F1 bajo porque la referencia es 1 sola palabra, 8 frente a ocho",
    },
    {
        "consulta": "que hace la funcion len en python?",
        "f1": 0.07,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta y completa, F1 bajo porque la referencia es coloquial y corta",
    },
    {
        "consulta": "cuando salio python?",
        "f1": 0.12,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta y completa, F1 bajo porque la respuesta agrega dia y el autor",
    },
    {
        "consulta": "quien escribio cien años de soledad?",
        "f1": 0.13,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta y completa, F1 bajo es por los tildes",
    },
    {
        "consulta": "para que sirve la temperatura en un modelo de lenguaje?",
        "f1": 0.14,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta, aunque difiere del a referencia en el uso de 'o' vs 'y' en respuesta , F1 bajo es por la diferencia entre palabras ej creativa vs creatividad",
    },
    {
        "consulta": "cual es el oceano mas grande?",
        "f1": 0.33,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta y completa, F1 bajo porque la respuesta es mas larga",
    },
    {
        "consulta": "a cuantos grados hierve el agua a nivel del mar?",
        "f1": 0.35,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta y completa, F1 bajo porque la respuesta abarca toda la referencia y mas",
    },
    {
        "consulta": "que es un token en una ia?",
        "f1": 0.44,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "correcta y completa, F1 de rango medio, dado que la respuesta es mas larga y completa",
    },
    {
        "consulta": "como guarda las cosas un json?",
        "f1": 0.47,
        "correccion_factual": "si",
        "completitud": "parcial",
        "contradiccion": "no",
        "nota": "correcta pero incompleta, no menciona que se guarda en texto plano, F1 de rango medio porque la respuesta es mas larga",
    },
]



def validar_revision(revision: list[dict]) -> None:
    """Comprueba que cada caso use los valores de la rúbrica y tenga una nota."""
    for i, caso in enumerate(revision, start=1):
        for campo, permitidos in VALORES_PERMITIDOS.items():
            if caso.get(campo) not in permitidos:
                raise ValueError(f"caso {i}: '{campo}' debe ser uno de {sorted(permitidos)}")
        if not caso.get("nota", "").strip():
            raise ValueError(f"caso {i}: falta la nota que explica la calificación")


if __name__ == "__main__":
    try:
        validar_revision(REVISION_MANUAL)
    except ValueError as error:
        print("No se pudo guardar la revision:", error)
    else:
        os.makedirs("docs", exist_ok=True)
        with open(ARCHIVO_REVISION, "w", encoding="utf-8") as archivo:
            json.dump(REVISION_MANUAL, archivo, indent=2, ensure_ascii=False)
        print(f"{len(REVISION_MANUAL)} casos guardados en {ARCHIVO_REVISION}")
        if len(REVISION_MANUAL) < 10:
            print("Aviso: la actividad pide al menos 10 casos revisados.")