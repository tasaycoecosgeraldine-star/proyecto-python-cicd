
from pathlib import Path
from datetime import datetime, timezone
import json
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
REPORTES = BASE / "reportes"
RESULTADOS = REPORTES / "resultados.xml"
COBERTURA = REPORTES / "coverage.xml"
DESTINO = REPORTES / "dashboard" / "index.html"

# Descripción académica de las 20 pruebas
DESCRIPCIONES = {
    "test_pagina_principal":
        "Comprueba que AcademicLab responda HTTP 200.",

    "test_promedio_aprobado":
        "Calcula 15, 16 y 18; espera 16.33 y APROBADO.",

    "test_promedio_desaprobado":
        "Calcula 8, 9 y 10; espera 9.00 y DESAPROBADO.",

    "test_notas_maximas":
        "Verifica el promedio máximo de 20.",

    "test_notas_minimas":
        "Verifica el promedio mínimo de 0.",

    "test_nota_negativa":
        "Rechaza notas inferiores a cero (HTTP 400).",

    "test_nota_superior_a_20":
        "Rechaza notas superiores a 20 (HTTP 400).",

    "test_campo_faltante":
        "Rechaza solicitudes con una nota ausente.",

    "test_nota_no_numerica":
        "Rechaza texto no numérico en una nota.",

    "test_json_vacio":
        "Rechaza un objeto JSON sin notas.",

    "test_notas_decimales":
        "Comprueba el cálculo con notas decimales.",

    "test_limite_aprobatorio":
        "Verifica la nota aprobatoria exacta de 11.",

    "test_formato_json_incorrecto":
        "Rechaza solicitudes sin un objeto JSON.",

    "test_error_interno_de_calculo":
        "Comprueba el manejo de ValueError simulado.",

    "test_consola_estudiante_aprobado":
        "Ejecuta main.py por consola con resultado aprobado.",

    "test_consola_estudiante_desaprobado":
        "Ejecuta main.py por consola con resultado desaprobado.",

    "test_calcular_promedio":
        "Verifica el cálculo unitario del promedio.",

    "test_estudiante_aprobado":
        "Verifica la clasificación APROBADO.",

    "test_estudiante_desaprobado":
        "Verifica la clasificación DESAPROBADO.",

    "test_nota_fuera_de_rango":
        "Verifica el rechazo de notas fuera del rango 0 a 20."
}


# ======================================
# 1. LEER RESULTADOS REALES DE PYTEST
# ======================================

def leer_pruebas():
    raiz = ET.parse(RESULTADOS).getroot()
    filas = []

    for caso in raiz.iter("testcase"):
        estado = "aprobada"
        detalle = ""

        for etiqueta, nuevo_estado in (
            ("failure", "fallida"),
            ("error", "error"),
            ("skipped", "omitida")
        ):
            elemento = caso.find(etiqueta)

            if elemento is not None:
                estado = nuevo_estado
                detalle = (
                    elemento.get("message")
                    or elemento.text
                    or ""
                ).strip()[:300]
                break

        nombre = caso.get("name", "Sin nombre")
        modulo = caso.get("classname", "")

        if "consola" in modulo or "consola" in nombre:
            grupo = "Pruebas de consola"
        elif "test_app" in modulo:
            grupo = "Integración Flask"
        else:
            grupo = "Pruebas unitarias"

        filas.append({
            "nombre": nombre,
            "grupo": grupo,
            "estado": estado,
            "duracion": round(
                float(caso.get("time", "0")), 4
            ),
            "descripcion": DESCRIPCIONES.get(
                nombre,
                "Verificación automatizada de AcademicLab."
            ),
            "detalle": detalle
        })

    return filas


# ======================================
# 2. LEER COBERTURA REAL
# ======================================

def leer_cobertura():
    raiz = ET.parse(COBERTURA).getroot()
    archivos = []

    for clase in raiz.iter("class"):
        nombre = clase.get(
            "filename",
            clase.get("name", "archivo")
        )

        porcentaje = round(
            float(clase.get("line-rate", 0)) * 100, 1
        )

        archivos.append({
            "nombre": nombre,
            "porcentaje": porcentaje
        })

    return {
        "total": round(
            float(raiz.get("line-rate", 0)) * 100, 1
        ),
        "archivos": archivos
    }


# ======================================
# 3. GENERAR DASHBOARD
# ======================================

def main():
    if not RESULTADOS.is_file() or not COBERTURA.is_file():
        raise SystemExit(
            "Faltan resultados.xml o coverage.xml. "
            "Ejecuta las pruebas primero."
        )

    pruebas = leer_pruebas()
    cobertura = leer_cobertura()

    resumen = {
        "total": len(pruebas),
        "aprobadas": sum(
            p["estado"] == "aprobada" for p in pruebas
        ),
        "fallidas": sum(
            p["estado"] == "fallida" for p in pruebas
        ),
        "errores": sum(
            p["estado"] == "error" for p in pruebas
        ),
        "omitidas": sum(
            p["estado"] == "omitida" for p in pruebas
        ),
        "duracion": round(
            sum(p["duracion"] for p in pruebas), 3
        )
    }

    datos = {
        "resumen": resumen,
        "pruebas": pruebas,
        "cobertura": cobertura,
        "generado": datetime.now(
            timezone.utc
        ).strftime("%d/%m/%Y %H:%M UTC")
    }

    payload = json.dumps(
        datos, ensure_ascii=False
    ).replace("<", "\\u003c")

    html = r'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>AcademicLab | Quality Dashboard</title>

<style>
:root {
    --dark: #152012;
    --tea: #E2EACB;
    --red: #B20000;
    --white: #FFFFFF;
    --bg: #F6F8F0;
    --muted: #6D7866;
    --border: #D9E2CC;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: var(--bg);
    color: var(--dark);
    font: 15px "Segoe UI", Arial, sans-serif;
}

/* ENCABEZADO */

header {
    background: var(--dark);
    color: white;
    padding: 24px max(20px, calc((100vw - 1160px)/2));
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}

.logo {
    font-size: 24px;
    font-weight: 900;
    letter-spacing: -1px;
}

.logo span {
    color: var(--tea);
}

.logo b {
    color: #EF8D86;
}

header small {
    color: #C3D4B8;
}

/* CONTENIDO */

main {
    max-width: 1160px;
    margin: 42px auto;
    padding: 0 20px;
}

.eyebrow {
    color: var(--red);
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 900;
}

h1 {
    font-size: clamp(30px, 5vw, 48px);
    margin: 12px 0;
    letter-spacing: -1.5px;
}

h2 {
    font-size: 20px;
    margin: 0 0 18px;
}

.sub {
    color: var(--muted);
    line-height: 1.7;
}

/* INDICADORES */

.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 28px 0;
}

.metric, .panel {
    border: 1px solid var(--border);
    border-radius: 20px;
    background: white;
    padding: 23px;
}

.metric strong {
    display: block;
    font-size: 38px;
    letter-spacing: -2px;
}

.metric span {
    color: var(--muted);
    font-size: 12px;
}

.metric.featured {
    background: var(--dark);
    color: var(--tea);
    border-color: var(--dark);
}

.metric.featured span {
    color: #C3D4B8;
}

/* GRÁFICOS */

.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    margin-bottom: 22px;
}

.panel {
    min-width: 0;
}

.bar {
    height: 14px;
    border-radius: 30px;
    background: #E7E9E2;
    overflow: hidden;
    margin: 14px 0;
}

.fill {
    height: 100%;
    background: #54884C;
    border-radius: 30px;
}

.coverrow {
    margin: 18px 0;
}

.coverrow > div:first-child {
    display: flex;
    justify-content: space-between;
    gap: 10px;
}

.tiny {
    color: var(--muted);
    font-size: 12px;
}

.red {
    color: var(--red);
}

/* BUSCADOR Y FILTROS */

.controls {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 18px 0;
}

.controls input,
.controls select {
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px;
    background: white;
    color: var(--dark);
    font: inherit;
}

.controls input {
    flex: 1;
    min-width: 180px;
}

/* DETALLE DE PRUEBAS */

.test {
    border: 1px solid var(--border);
    background: white;
    border-radius: 15px;
    padding: 18px 20px;
    margin: 10px 0;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 15px;
}

.test h3 {
    margin: 0 0 7px;
    font-size: 15px;
    overflow-wrap: anywhere;
}

.test p {
    margin: 0 0 6px;
    color: var(--muted);
    line-height: 1.5;
    font-size: 13px;
}

.status {
    font-size: 11px;
    font-weight: 850;
    border-radius: 20px;
    padding: 7px 11px;
    white-space: nowrap;
    background: var(--tea);
}

.status.fallida,
.status.error {
    background: #F9D4D4;
    color: var(--red);
}

.status.omitida {
    background: #EEE9CE;
}

/* BOTONES */

.button {
    display: inline-block;
    text-decoration: none;
    background: var(--red);
    color: white;
    border-radius: 11px;
    padding: 12px 16px;
    font-weight: 750;
    font-size: 13px;
}

/* PIE DE PÁGINA */

footer {
    max-width: 1160px;
    margin: 30px auto 60px;
    padding: 0 20px;
    color: var(--muted);
    font-size: 12px;
}

@media (max-width: 750px) {
    .cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .grid {
        grid-template-columns: 1fr;
    }

    .test {
        flex-direction: column;
    }
}
</style>
</head>

<body>

<header>
    <div class="logo">
        ACADEMIC<span>LAB</span> <b>/ QA</b>
    </div>

    <small>
        Python · Flask · Pytest · GitHub Actions
    </small>
</header>

<main>

    <div class="eyebrow">
        CONTROL DE CALIDAD DEL SOFTWARE
    </div>

    <h1>Quality Dashboard</h1>

    <p class="sub">
        Resultados obtenidos automáticamente de
        Pytest y Coverage.py.
        <br>
        Generado: <span id="fecha"></span>
    </p>

    <!-- INDICADORES -->

    <section class="cards">

        <article class="metric featured">
            <strong id="total">0</strong>
            <span>Pruebas ejecutadas</span>
        </article>

        <article class="metric">
            <strong id="aprobadas">0</strong>
            <span>Aprobadas</span>
        </article>

        <article class="metric">
            <strong id="fallidas">0</strong>
            <span>Fallidas y errores</span>
        </article>

        <article class="metric">
            <strong id="cobertura">0%</strong>
            <span>Cobertura de sentencias</span>
        </article>

    </section>

    <!-- RESULTADOS Y COBERTURA -->

    <section class="grid">

        <article class="panel">
            <h2>Resultados de las pruebas</h2>

            <div class="bar">
                <div class="fill" id="barra-pruebas"></div>
            </div>

            <p id="resumen-pruebas" class="sub"></p>

            <p id="duracion" class="tiny"></p>
        </article>

        <article class="panel">
            <h2>Cobertura por archivo</h2>

            <div id="archivos"></div>

            <a class="button"
               href="../cobertura/index.html">
                Ver cobertura detallada ↗
            </a>
        </article>

    </section>

    <!-- LISTA DE PRUEBAS -->

    <section class="panel">

        <h2>Detalle de pruebas automatizadas</h2>

        <p class="sub">
            Objetivo, estado y duración
            de cada caso ejecutado.
        </p>

        <div class="controls">

            <input
                id="buscar"
                placeholder="Buscar una prueba..."
                aria-label="Buscar prueba"
            >

            <select id="filtrar">
                <option value="todos">
                    Todos los estados
                </option>
                <option value="aprobada">
                    Aprobadas
                </option>
                <option value="fallida">
                    Fallidas
                </option>
                <option value="error">
                    Errores
                </option>
                <option value="omitida">
                    Omitidas
                </option>
            </select>

        </div>

        <p id="contador" class="tiny"></p>

        <div id="pruebas"></div>

    </section>

</main>

<footer>
    AcademicLab · Informe técnico automatizado.
    La cobertura no garantiza ausencia de defectos.
</footer>

<script>
const DATA = __DATA__;

const $ = id => document.getElementById(id);

function escapar(texto) {
    return String(texto).replace(
        /[&<>"']/g,
        caracter => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[caracter])
    );
}

const resumen = DATA.resumen;

$("total").textContent = resumen.total;
$("aprobadas").textContent = resumen.aprobadas;

$("fallidas").textContent =
    resumen.fallidas + resumen.errores;

$("cobertura").textContent =
    DATA.cobertura.total + "%";

$("fecha").textContent = DATA.generado;

// Gráfico de aprobación
$("barra-pruebas").style.width = (
    resumen.total
        ? resumen.aprobadas / resumen.total * 100
        : 0
) + "%";

$("resumen-pruebas").textContent =
    resumen.aprobadas + " aprobadas · " +
    resumen.fallidas + " fallidas · " +
    resumen.errores + " errores · " +
    resumen.omitidas + " omitidas";

$("duracion").textContent =
    "Duración acumulada: " +
    resumen.duracion.toFixed(3) + " segundos";

// Cobertura por archivo
$("archivos").innerHTML =
    DATA.cobertura.archivos.map(archivo => `
        <div class="coverrow">
            <div>
                <b>${escapar(archivo.nombre)}</b>
                <b>${archivo.porcentaje}%</b>
            </div>

            <div class="bar">
                <div class="fill"
                     style="width:${archivo.porcentaje}%">
                </div>
            </div>
        </div>
    `).join("");

// ======================================
// BUSCADOR Y FILTROS
// ======================================

function renderizarPruebas() {
    const busqueda =
        $("buscar").value.toLowerCase();

    const estado = $("filtrar").value;

    const filtradas = DATA.pruebas.filter(prueba => {
        const coincideEstado =
            estado === "todos" ||
            prueba.estado === estado;

        const texto = (
            prueba.nombre + " " +
            prueba.descripcion + " " +
            prueba.grupo
        ).toLowerCase();

        return coincideEstado &&
            texto.includes(busqueda);
    });

    $("contador").textContent =
        "Mostrando " + filtradas.length +
        " de " + DATA.pruebas.length + " pruebas";

    $("pruebas").innerHTML = filtradas.map(prueba => `
        <article class="test">

            <div>
                <h3>${escapar(prueba.nombre)}</h3>

                <p>${escapar(prueba.descripcion)}</p>

                <p class="tiny">
                    ${escapar(prueba.grupo)}
                    · ${prueba.duracion.toFixed(4)} s
                </p>

                ${prueba.detalle ? `
                    <p class="red">
                        ${escapar(prueba.detalle)}
                    </p>
                ` : ""}
            </div>

            <span class="status ${prueba.estado}">
                ${prueba.estado.toUpperCase()}
            </span>

        </article>
    `).join("") ||
        "<p>No hay pruebas con ese filtro.</p>";
}

$("buscar").addEventListener(
    "input", renderizarPruebas
);

$("filtrar").addEventListener(
    "change", renderizarPruebas
);

renderizarPruebas();
</script>

</body>
</html>'''

    DESTINO.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    DESTINO.write_text(
        html.replace("__DATA__", payload),
        encoding="utf-8"
    )

    print("Dashboard generado correctamente.")
    print("Archivo:", DESTINO)
    print("Pruebas:", resumen["total"])
    print("Cobertura:", cobertura["total"], "%")


if __name__ == "__main__":
    main()
