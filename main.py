
def calcular_promedio(nota1, nota2, nota3):
    notas = [nota1, nota2, nota3]

    if not all(0 <= nota <= 20 for nota in notas):
        raise ValueError("Las notas deben estar entre 0 y 20")

    return sum(notas) / len(notas)


def obtener_resultado(promedio):
    if promedio >= 11:
        return "APROBADO"

    return "DESAPROBADO"


if __name__ == "__main__":
    nota1 = float(input("Ingrese nota 1: "))
    nota2 = float(input("Ingrese nota 2: "))
    nota3 = float(input("Ingrese nota 3: "))

    promedio = calcular_promedio(nota1, nota2, nota3)
    resultado = obtener_resultado(promedio)

    print(f"Promedio: {promedio:.2f}")
    print(f"Resultado: {resultado}")
