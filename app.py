
from flask import Flask, jsonify, render_template, request
from math import isfinite

from main import calcular_promedio, obtener_resultado

app = Flask(__name__)


# Página principal de AcademicLab
@app.get("/")
def inicio():
    return render_template("index.html")


# Servicio para calcular las notas
@app.post("/api/calcular")
def calcular():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar las notas en formato JSON."
        }), 400

    notas = []

    for i in range(1, 4):
        valor = datos.get(f"nota{i}")

        if (
            valor is None
            or isinstance(valor, (bool, list, dict))
            or str(valor).strip() == ""
        ):
            return jsonify({
                "error": f"Ingresa correctamente la nota {i}."
            }), 400

        try:
            nota = float(valor)
        except (ValueError, TypeError, OverflowError):
            return jsonify({
                "error": f"La nota {i} debe ser numérica."
            }), 400

        if not isfinite(nota) or nota < 0 or nota > 20:
            return jsonify({
                "error": f"La nota {i} debe estar entre 0 y 20."
            }), 400

        notas.append(nota)

    try:
        promedio = calcular_promedio(*notas)
        resultado = obtener_resultado(promedio)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({
        "notas": notas,
        "promedio": round(promedio, 2),
        "resultado": resultado,
        "aprobado": resultado == "APROBADO"
    })


if __name__ == "__main__":
    app.run(debug=True)  # pragma: no cover