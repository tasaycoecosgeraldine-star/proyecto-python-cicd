
import pytest

from app import app


@pytest.fixture
def cliente():
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        yield cliente


# PRUEBA 1: Página principal
def test_pagina_principal(cliente):
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert b"AcademicLab" in respuesta.data


# PRUEBA 2: Promedio aprobado
def test_promedio_aprobado(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": 15,
        "nota2": 16,
        "nota3": 18
    })

    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert datos["promedio"] == 16.33
    assert datos["resultado"] == "APROBADO"


# PRUEBA 3: Promedio desaprobado
def test_promedio_desaprobado(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": 8,
        "nota2": 9,
        "nota3": 10
    })

    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert datos["promedio"] == 9.00
    assert datos["resultado"] == "DESAPROBADO"


# PRUEBA 4: Notas máximas
def test_notas_maximas(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": 20,
        "nota2": 20,
        "nota3": 20
    })

    assert respuesta.status_code == 200
    assert respuesta.get_json()["promedio"] == 20


# PRUEBA 5: Notas mínimas
def test_notas_minimas(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": 0,
        "nota2": 0,
        "nota3": 0
    })

    assert respuesta.status_code == 200
    assert respuesta.get_json()["promedio"] == 0


# PRUEBA 6: Primera nota negativa
def test_nota_negativa(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": -1,
        "nota2": 15,
        "nota3": 18
    })

    assert respuesta.status_code == 400


# PRUEBA 7: Nota mayor que 20
def test_nota_superior_a_20(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": 21,
        "nota2": 15,
        "nota3": 18
    })

    assert respuesta.status_code == 400


# PRUEBA 8: Campo faltante
def test_campo_faltante(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": 15,
        "nota3": 18
    })

    assert respuesta.status_code == 400


# PRUEBA 9: Texto no numérico
def test_nota_no_numerica(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": "abc",
        "nota2": 15,
        "nota3": 18
    })

    assert respuesta.status_code == 400


# PRUEBA 10: JSON vacío
def test_json_vacio(cliente):
    respuesta = cliente.post("/api/calcular", json={})

    assert respuesta.status_code == 400


# PRUEBA 11: Nota decimal
def test_notas_decimales(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": 14.5,
        "nota2": 15.5,
        "nota3": 16
    })

    assert respuesta.status_code == 200
    assert respuesta.get_json()["promedio"] == 15.33


# PRUEBA 12: Nota aprobatoria exacta
def test_limite_aprobatorio(cliente):
    respuesta = cliente.post("/api/calcular", json={
        "nota1": 11,
        "nota2": 11,
        "nota3": 11
    })

    assert respuesta.status_code == 200
    assert respuesta.get_json()["promedio"] == 11
    assert respuesta.get_json()["resultado"] == "APROBADO"


# PRUEBA 13: Solicitud con formato JSON incorrecto
def test_formato_json_incorrecto(cliente):
    respuesta = cliente.post(
        "/api/calcular",
        data="esto no es un JSON",
        content_type="text/plain"
    )

    datos = respuesta.get_json()

    assert respuesta.status_code == 400
    assert datos["error"] == (
        "Debes enviar las notas en formato JSON."
    )

# PRUEBA 14: Manejo de errores de cálculo
def test_error_interno_de_calculo(cliente, monkeypatch):

    def simular_error(*notas):
        raise ValueError("Error simulado en el cálculo")

    monkeypatch.setattr(
        "app.calcular_promedio",
        simular_error
    )

    respuesta = cliente.post(
        "/api/calcular",
        json={
            "nota1": 15,
            "nota2": 16,
            "nota3": 18
        }
    )

    datos = respuesta.get_json()

    assert respuesta.status_code == 400

    assert datos["error"] == (
        "Error simulado en el cálculo"
    )
