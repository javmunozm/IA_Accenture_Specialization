EJEMPLOS_ACTUALES = 12      # los de EJEMPLOS_RAW bloque 29
EJEMPLOS_OBJETIVO = 200 
MINUTOS_POR_EJEMPLO = 5
COSTO_POR_HORA = 25

def estimar_costo_de_etiquetar(num_ejemplos, minutos_por_ejemplo, costo_por_hora):
    horas = (num_ejemplos * minutos_por_ejemplo) / 60
    costo = horas * costo_por_hora
    return horas, costo

def main():
    # del dataset del bloque anterior, 5 minutos por ejemplo
    horas, costo = estimar_costo_de_etiquetar(8,5, 25)
    print(f"{horas:.2f} horas, aprox ${costo:.2f}")

    #el mismo calculo pero para un dataset mas op
    horas2, costo2 = estimar_costo_de_etiquetar(200,5, 25)
    print(f"{horas2:.2f} horas, aprox ${costo2:.2f}")
    print(f"factor de crecimiento en horas: {horas2 / horas:.1f}x, para 25x mas ejemplos")
    print()

    #Mini ejer + una revision
    horas_base, costo_base = estimar_costo_de_etiquetar(500, 4, 20)
    horas_rev, costo_rev = estimar_costo_de_etiquetar(500 * 0.20, 2, 20)

    total_horas = horas_base + horas_rev
    total_costo = costo_base + costo_rev
    jornadas = total_horas / 8

    print(f"etiquetado base: {horas_base:.2f} horas, aprox ${costo_base:.2f}")
    print(f"segunda revision: {horas_rev:.2f} horas, aprox ${costo_rev:.2f}")
    print(f"total: {total_horas:.2f} horas, aprox ${total_costo:.2f}")
    print(f"jornadas de 8 horas: {jornadas:.1f} jornadas")
    print()

    faltan = max(EJEMPLOS_OBJETIVO - EJEMPLOS_ACTUALES, 0) # lo que falta para el objetivo
    horas_mias, costo_mio = estimar_costo_de_etiquetar(faltan, MINUTOS_POR_EJEMPLO, COSTO_POR_HORA)
    print(f"tu caso: tienes {EJEMPLOS_ACTUALES} ejemplos, faltan {faltan} ejemplos para {EJEMPLOS_OBJETIVO}")
    print(f"tu caso: {horas_mias:.2f} horas, aprox ${costo_mio:.2f}")

if __name__ == "__main__":
    main()