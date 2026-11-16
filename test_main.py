
import pytest

from main import calcular_promedio, obtener_resultado


def test_calcular_promedio():
    resultado = calcular_promedio(15, 16, 18)
    assert resultado == pytest.approx(16.33, abs=0.01)


def test_estudiante_aprobado():
    assert obtener_resultado(15) == "APROBADO"


def test_estudiante_desaprobado():
    assert obtener_resultado(9) == "DESAPROBADO"


def test_nota_fuera_de_rango():
    with pytest.raises(ValueError):
        calcular_promedio(25, 15, 18)
