import os

def preflight_check(persist_directory, gitignore_path=".gitignore"): 
    problemas = []

    if not os.path.isdir(persist_directory):
        problemas.append(f"{persist_directory} no existe: corriste la indexacion?")

    # El indice es generado y guarda el texto del corpus: no debe subirse al repositorio
    if os.path.exists(gitignore_path):
        with open(gitignore_path, encoding="utf-8") as archivo:
            contenido = archivo.read()
        nombre_carpeta = persist_directory.rstrip("/")
        if nombre_carpeta not in contenido:
            problemas.append(f"{persist_directory} no esta en {gitignore_path}")
    else:
            problemas.append(f"no existe {gitignore_path} en este proyecto")

    return problemas


if __name__ == "__main__":
    problemas = preflight_check("vectorstore/")
    if problemas:
        print("Preflight con problemas:")
        for problema in problemas:
            print(" -", problema)
    else:
        print("Preflight OK: la carpeta del indice existe y esta en .gitignore")

    