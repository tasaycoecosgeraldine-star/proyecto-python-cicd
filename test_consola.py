
import subprocess
import sys
from pathlib import Path

# Ruta del programa original
MAIN = Path(__file__).resolve().parent / "main.py"


# PRUEBA 19: Estudiante aprobado por consola
def test_consola_estudiante_aprobado():

    resultado = subprocess.run(
        [sys.executable, str(MAIN)],
        input="15\n16\n18\n",
        text=True,
        capture_output=True,
        timeout=10
    )

    assert resultado.returncode == 0
    assert "Promedio: 16.33" in resultado.stdout
    assert "Resultado: APROBADO" in resultado.stdout


# PRUEBA 20: Estudiante desaprobado por consola
def test_consola_estudiante_desaprobado():

    resultado = subprocess.run(
        [sys.executable, str(MAIN)],
        input="8\n9\n10\n",
        text=True,
        capture_output=True,
        timeout=10
    )

    assert resultado.returncode == 0
    assert "Promedio: 9.00" in resultado.stdout
    assert "Resultado: DESAPROBADO" in resultado.stdout
