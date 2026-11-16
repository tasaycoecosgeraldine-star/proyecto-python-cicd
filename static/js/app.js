
// ======================================
// ACADEMICLAB - FUNCIONES JAVASCRIPT
// ======================================

const $ = (id) => document.getElementById(id);

// ======================================
// 1. ALMACENAMIENTO LOCAL
// ======================================

function leerDatos(clave, defecto) {
    try {
        const contenido = localStorage.getItem(clave);

        if (contenido === null) {
            return defecto;
        }

        return JSON.parse(contenido);
    } catch {
        return defecto;
    }
}

function guardarDatos(clave, valor) {
    localStorage.setItem(
        clave,
        JSON.stringify(valor)
    );
}

let perfil = leerDatos("academiclab_perfil", {
    nombre: "Estudiante",
    carrera: ""
});

let ajustes = leerDatos("academiclab_ajustes", {
    compacto: false,
    guardarHistorial: true
});

let historial = leerDatos(
    "academiclab_historial",
    []
);

// ======================================
// 2. NAVEGACIÓN ENTRE PANTALLAS
// ======================================

function mostrarSeccion(seccion) {
    document.querySelectorAll(".page")
        .forEach((pagina) => {
            pagina.classList.toggle(
                "active",
                pagina.id === seccion
            );
        });

    document.querySelectorAll(".nav-btn")
        .forEach((boton) => {
            boton.classList.toggle(
                "active",
                boton.dataset.section === seccion
            );
        });

    if (seccion === "historial") {
        mostrarHistorial();
    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

document.querySelectorAll("[data-section]")
    .forEach((boton) => {
        boton.addEventListener("click", () => {
            mostrarSeccion(
                boton.dataset.section
            );
        });
    });

document.querySelectorAll("[data-go]")
    .forEach((boton) => {
        boton.addEventListener("click", () => {
            mostrarSeccion(boton.dataset.go);
        });
    });

// ======================================
// 3. CALCULADORA DE NOTAS
// ======================================

const formulario = $("form-notas");

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    $("mensaje-error").textContent = "";

    const nota1 = $("nota1").value;
    const nota2 = $("nota2").value;
    const nota3 = $("nota3").value;

    const entradas = [nota1, nota2, nota3];

    const validas = entradas.every((valor) => {
        return (
            valor.trim() !== "" &&
            Number.isFinite(Number(valor)) &&
            Number(valor) >= 0 &&
            Number(valor) <= 20
        );
    });

    if (!validas) {
        $("mensaje-error").textContent =
            "Ingresa tres notas válidas entre 0 y 20.";
        return;
    }

    const boton = $("btn-calcular");
    boton.disabled = true;
    boton.textContent = "CALCULANDO...";

    try {
        const respuesta = await fetch("/api/calcular", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nota1: Number(nota1),
                nota2: Number(nota2),
                nota3: Number(nota3)
            })
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                datos.error || "No se pudo calcular."
            );
        }

        // Mostrar el promedio obtenido de Python
        $("promedio").textContent =
            Number(datos.promedio).toFixed(2);

        $("resultado").textContent =
            datos.resultado;

        $("resultado").classList.toggle(
            "failed",
            datos.resultado === "DESAPROBADO"
        );

        // Guardar el cálculo, si está habilitado
        if (ajustes.guardarHistorial) {
            const registro = {
                notas: datos.notas,
                promedio: datos.promedio,
                resultado: datos.resultado,
                fecha: new Date().toLocaleString("es-PE")
            };

            historial.unshift(registro);

            historial = historial.slice(0, 40);

            guardarDatos(
                "academiclab_historial",
                historial
            );
        }

    } catch (error) {
        $("mensaje-error").textContent =
            error.message ||
            "No se pudo conectar con Python.";

    } finally {
        boton.disabled = false;
        boton.textContent = "CALCULAR PROMEDIO →";
    }
});

// Limpiar formulario y resultado
formulario.addEventListener("reset", () => {
    $("promedio").textContent = "--";
    $("resultado").textContent = "SIN CALCULAR";

    $("resultado").classList.remove("failed");

    $("mensaje-error").textContent = "";
});

// ======================================
// 4. HISTORIAL DE CALIFICACIONES
// ======================================

function mostrarHistorial() {
    const contenedor = $("historial-lista");

    contenedor.replaceChildren();

    if (historial.length === 0) {
        const mensaje = document.createElement("div");

        mensaje.className = "empty-state";
        mensaje.textContent =
            "Todavía no tienes promedios guardados.";

        contenedor.appendChild(mensaje);
        return;
    }

    historial.forEach((registro) => {
        const tarjeta = document.createElement("div");
        tarjeta.className = "history-item";

        const informacion = document.createElement("div");

        const titulo = document.createElement("strong");
        titulo.textContent =
            Number(registro.promedio).toFixed(2);

        const detalle = document.createElement("p");
        detalle.textContent =
            `Notas: ${registro.notas.join(" / ")} · ${registro.fecha}`;

        informacion.append(titulo, detalle);

        const estado = document.createElement("span");
        estado.className = "result-badge";

        estado.textContent = registro.resultado;

        if (registro.resultado === "DESAPROBADO") {
            estado.classList.add("failed");
        }

        tarjeta.append(informacion, estado);

        contenedor.appendChild(tarjeta);
    });
}

$("borrar-historial").addEventListener("click", () => {
    const confirmar = confirm(
        "¿Deseas eliminar todo el historial?"
    );

    if (!confirmar) {
        return;
    }

    historial = [];

    guardarDatos(
        "academiclab_historial",
        historial
    );

    mostrarHistorial();
});

// ======================================
// 5. PERFIL ACADÉMICO
// ======================================

function mostrarPerfil() {
    $("nombre").value = perfil.nombre || "";
    $("carrera").value = perfil.carrera || "";

    $("perfil-nombre").textContent =
        perfil.nombre || "Estudiante";

    $("perfil-carrera").textContent =
        perfil.carrera || "Sin carrera registrada";

    $("nav-name").textContent =
        perfil.nombre || "Estudiante";

    $("avatar").textContent =
        (perfil.nombre || "E")
            .trim()
            .charAt(0)
            .toUpperCase();
}

$("form-perfil").addEventListener("submit", (evento) => {
    evento.preventDefault();

    perfil = {
        nombre: $("nombre").value.trim() || "Estudiante",
        carrera: $("carrera").value.trim()
    };

    guardarDatos(
        "academiclab_perfil",
        perfil
    );

    mostrarPerfil();

    alert("Perfil guardado correctamente.");
});

// ======================================
// 6. AJUSTES DE LA APLICACIÓN
// ======================================

function aplicarAjustes() {
    document.body.classList.toggle(
        "compact",
        ajustes.compacto
    );

    $("modo-compacto").checked =
        ajustes.compacto;

    $("guardar-historial").checked =
        ajustes.guardarHistorial;
}

$("btn-ajustes").addEventListener("click", () => {
    ajustes = {
        compacto: $("modo-compacto").checked,

        guardarHistorial:
            $("guardar-historial").checked
    };

    guardarDatos(
        "academiclab_ajustes",
        ajustes
    );

    aplicarAjustes();

    alert("Ajustes guardados correctamente.");
});

// ======================================
// 7. INICIALIZACIÓN
// ======================================

mostrarPerfil();
aplicarAjustes();
mostrarHistorial();

console.log("AcademicLab iniciado correctamente.");
