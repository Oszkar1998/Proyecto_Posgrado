document.addEventListener("DOMContentLoaded", () => {
    const inputCuenta = document.getElementById("numeroDeCuenta");
    const modalFechaHora = document.getElementById("modal-fecha-hora");
    const modalSeleccionPlan = document.getElementById("modalSeleccionPlan");
    const botonesExpediente = document.getElementById("botones-expediente");
    const nombreAlumno = document.getElementById("nombre-alumno");
    const btnModificar = document.getElementById("btn-modificar-datos");

    window.numeroDeCuentaGlobal = "";
    window.seleccionIdGlobal = "";

    let debounceId = null;
    let bloqueoValidacion = false;
    let cuentaValidada = "";

    inicializarUI();
    bindEventos();

    function inicializarUI() {
        ocultarBotonesExpediente();
        cerrarModal("modal-fecha-hora");
        cerrarModal("modalSeleccionPlan");

        if (nombreAlumno) {
            nombreAlumno.textContent = "";
            nombreAlumno.style.display = "none";
        }

        crearStatusSiNoExiste();
        setStatus("Escribe tu número de cuenta.");
    }

    function bindEventos() {
        if (inputCuenta) {
            inputCuenta.addEventListener("input", manejarInputCuenta);
            inputCuenta.addEventListener("blur", manejarBlurCuenta);
            inputCuenta.addEventListener("keydown", manejarEnterCuenta);
        }

        if (btnModificar) {
            btnModificar.addEventListener("click", abrirModoModificar);
        }

        document.addEventListener("keydown", (ev) => {
            if (ev.key === "Escape") {
                cerrarModal("modal-fecha-hora");
                cerrarModal("modalSeleccionPlan");
                setStatus("Modal cerrado.");
            }
        });

        if (modalFechaHora) {
            modalFechaHora.addEventListener("click", (ev) => {
                if (ev.target === modalFechaHora) {
                    cerrarModal("modal-fecha-hora");
                    setStatus("Modal cerrado.");
                }
            });
        }

        if (modalSeleccionPlan) {
            modalSeleccionPlan.addEventListener("click", (ev) => {
                if (ev.target === modalSeleccionPlan) {
                    cerrarModal("modalSeleccionPlan");
                }
            });
        }

        const botones = [
            { id: "btn-documento-2", tipo: "2" },
            { id: "btn-documento-3", tipo: "3" },
            { id: "btn-documento-4", tipo: "4" },
            { id: "btn-documento-5", tipo: "5" },
            { id: "btn-documento-6", tipo: "6" },
            { id: "btn-documento-7", tipo: "7" }
        ];

        botones.forEach(({ id, tipo }) => {
            const btn = document.getElementById(id);
            if (!btn) return;

            btn.addEventListener("click", () => {
                generarDocumento(tipo);
            });
        });
    }

    function crearStatusSiNoExiste() {
        let status = document.getElementById("status-cuenta");

        if (!status) {
            status = document.createElement("div");
            status.id = "status-cuenta";
            status.className = "status-cuenta";

            const form = document.getElementById("login-form");
            if (form) {
                form.appendChild(status);
            }
        }
    }

    function setStatus(msg) {
        const status = document.getElementById("status-cuenta");
        if (status) status.textContent = msg || "";
    }

    function abrirModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;

        modal.classList.add("active");
        modal.style.display = "flex";
    }

    function cerrarModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;

        modal.classList.remove("active");
        modal.style.display = "none";
    }

    function mostrarBotonesExpediente() {
        if (botonesExpediente) botonesExpediente.style.display = "grid";
    }

    function ocultarBotonesExpediente() {
        if (botonesExpediente) botonesExpediente.style.display = "none";
    }

    function mostrarNombreAlumno(nombre) {
        if (!nombreAlumno) return;

        if (nombre) {
            nombreAlumno.textContent = `Alumno: ${nombre}`;
            nombreAlumno.style.display = "block";
        } else {
            nombreAlumno.textContent = "";
            nombreAlumno.style.display = "none";
        }
    }

    function toggleSinodales(show) {
        const campos = ["tutor", "presidente", "vocal1", "vocal2", "vocal3", "secretario"];
        const titulos = ["titulo-tutor", "titulo-sinodales"];

        campos.forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.style.display = show ? "block" : "none";
        });

        titulos.forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.style.display = show ? "block" : "none";
        });
    }

    function limpiarFormularioModal() {
        const ids = [
            "fechaExamen",
            "horaExamen",
            "ingreso",
            "termino",
            "promedio",
            "folio",
            "tutor",
            "presidente",
            "vocal1",
            "vocal2",
            "vocal3",
            "secretario"
        ];

        ids.forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.value = "";
        });

        const selectSede = document.getElementById("modalidadSede");
        if (selectSede) selectSede.value = "";
    }

    function resetAfterError() {
        if (debounceId) clearTimeout(debounceId);

        bloqueoValidacion = true;
        cuentaValidada = "";
        window.numeroDeCuentaGlobal = "";
        window.seleccionIdGlobal = "";

        ocultarBotonesExpediente();
        cerrarModal("modal-fecha-hora");
        cerrarModal("modalSeleccionPlan");
        mostrarNombreAlumno("");

        if (inputCuenta) {
            inputCuenta.value = "";
            setTimeout(() => inputCuenta.focus(), 0);
        }

        setStatus("Ingresa un número de cuenta válido.");
    }

    function manejarInputCuenta() {
        if (!inputCuenta) return;

        if (bloqueoValidacion) bloqueoValidacion = false;

        let valor = (inputCuenta.value || "").replace(/\D/g, "").slice(0, 9);
        inputCuenta.value = valor;

        ocultarBotonesExpediente();
        window.numeroDeCuentaGlobal = "";
        window.seleccionIdGlobal = "";
        cuentaValidada = "";
        mostrarNombreAlumno("");

        if (debounceId) clearTimeout(debounceId);

        if (valor.length < 9) {
            setStatus("Escribe tu número de cuenta.");
            return;
        }

        setStatus("Validando automáticamente...");

        debounceId = setTimeout(() => {
            validarCuenta();
        }, 350);
    }

    function manejarBlurCuenta() {
        if (!inputCuenta || bloqueoValidacion) return;

        const valor = (inputCuenta.value || "").trim();
        if (valor.length === 9 && cuentaValidada !== valor) {
            validarCuenta();
        }
    }

    function manejarEnterCuenta(ev) {
        if (ev.key !== "Enter") return;
        ev.preventDefault();

        if (!bloqueoValidacion) {
            validarCuenta();
        }
    }

    async function validarCuenta() {
        if (!inputCuenta) return;

        const numeroDeCuenta = (inputCuenta.value || "").trim();
        if (!numeroDeCuenta || numeroDeCuenta.length !== 9) return;

        setStatus("Validando cuenta...");

        try {
            const body = new URLSearchParams({
                numeroDeCuenta: numeroDeCuenta
            });

            const response = await fetch("/examen/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: body.toString()
            });

            const data = await response.json();

            if (!data.success) {
                alert(data.error || "No fue posible validar.");
                resetAfterError();
                return;
            }

            if (data.multiples && data.multiples.length > 1) {
                window.numeroDeCuentaGlobal = numeroDeCuenta;
                mostrarModalSeleccion(data.multiples, data.resumen || "");
                setStatus("Selecciona el plan o nivel correspondiente.");
                return;
            }

            window.numeroDeCuentaGlobal = numeroDeCuenta;
            cuentaValidada = numeroDeCuenta;

            mostrarNombreAlumno(data.nombreCompleto || "");

            if (data.tipo_modal === "omit_modal") {
                cerrarModal("modal-fecha-hora");
                mostrarBotonesExpediente();
                setStatus("✅ Cuenta validada. Ya puedes generar documentos.");
                return;
            }

            if (data.tipo_modal === "solo_fecha_hora") {
                limpiarFormularioModal();
                toggleSinodales(false);
                abrirModal("modal-fecha-hora");
                setStatus("⚠️ Faltan datos. Completa fecha, hora y datos de acta.");
                return;
            }

            limpiarFormularioModal();
            toggleSinodales(true);
            abrirModal("modal-fecha-hora");
            setStatus("⚠️ Faltan datos. Completa el formulario para continuar.");
        } catch (error) {
            console.error(error);
            setStatus("Error de red.");
            alert("Ocurrió un error al validar la cuenta.");
        }
    }

    async function abrirModoModificar() {
        const cuenta = (prompt("Ingresa el número de cuenta para modificar:") || "").trim();
        if (!cuenta) return;

        try {
            const response = await fetch(`/examen/datos?numeroDeCuenta=${encodeURIComponent(cuenta)}`);
            const data = await response.json();

            if (!data.success) {
                alert(data.error || "No hay datos guardados para este número.");
                return;
            }

            const campos = data.campos || {};

            window.numeroDeCuentaGlobal = cuenta;
            window.seleccionIdGlobal = "";

            if (inputCuenta) inputCuenta.value = cuenta;

            toggleSinodales(true);

            [
                "fechaExamen",
                "horaExamen",
                "ingreso",
                "termino",
                "promedio",
                "folio",
                "tutor",
                "presidente",
                "vocal1",
                "vocal2",
                "vocal3",
                "secretario"
            ].forEach((id) => {
                const el = document.getElementById(id);
                if (el) el.value = campos[id] || "";
            });

            const sede = document.getElementById("modalidadSede");
            if (sede) sede.value = campos.modalidadSede || "";

            mostrarNombreAlumno("");
            abrirModal("modal-fecha-hora");
            setStatus("Editando datos guardados...");
        } catch (error) {
            console.error(error);
            alert("No se pudo cargar la información para modificar.");
        }
    }

    window.guardarFechaHora = async function () {
        if (!window.numeroDeCuentaGlobal) {
            alert("Falta número de cuenta.");
            return;
        }

        const fecha = document.getElementById("fechaExamen")?.value || "";
        const hora = document.getElementById("horaExamen")?.value || "";
        const ingreso = document.getElementById("ingreso")?.value || "";
        const termino = document.getElementById("termino")?.value || "";
        const promedio = document.getElementById("promedio")?.value || "";
        const folio = document.getElementById("folio")?.value || "";
        const modalidadSede = document.getElementById("modalidadSede")?.value || "";

        const tutor = document.getElementById("tutor")?.value || "";
        const presidente = document.getElementById("presidente")?.value || "";
        const vocal1 = document.getElementById("vocal1")?.value || "";
        const vocal2 = document.getElementById("vocal2")?.value || "";
        const vocal3 = document.getElementById("vocal3")?.value || "";
        const secretario = document.getElementById("secretario")?.value || "";

        if (!fecha || !hora || !ingreso || !termino || !promedio || !folio || !modalidadSede) {
            alert("Por favor, completa fecha, hora, ingreso, término, promedio, folio y sede del examen.");
            return;
        }

        try {
            const body = new URLSearchParams({
                numeroDeCuenta: window.numeroDeCuentaGlobal,
                tipoDocumento: "confirmar_modal",
                fechaExamen: fecha,
                horaExamen: hora,
                ingreso: ingreso,
                termino: termino,
                promedio: promedio,
                folio: folio,
                tutor: tutor,
                presidente: presidente,
                vocal1: vocal1,
                vocal2: vocal2,
                vocal3: vocal3,
                secretario: secretario,
                modalidadSede: modalidadSede
            });

            if (window.seleccionIdGlobal) {
                body.append("seleccion_id", window.seleccionIdGlobal);
            }

            const response = await fetch("/examen/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: body.toString()
            });

            const data = await response.json();

            if (!data.success) {
                alert(data.error || "No se pudo guardar.");
                return;
            }

            cerrarModal("modal-fecha-hora");
            mostrarBotonesExpediente();
            setStatus("✅ Datos guardados. Ya puedes generar documentos.");
        } catch (error) {
            console.error(error);
            alert("Error de red al guardar.");
        }
    };

    window.cerrarModalFechaHora = function () {
        cerrarModal("modal-fecha-hora");
    };

    async function generarDocumento(tipoDocumento) {
        if (!window.numeroDeCuentaGlobal) {
            alert("Primero ingresa el número de cuenta.");
            return;
        }

        try {
            const body = new URLSearchParams({
                numeroDeCuenta: window.numeroDeCuentaGlobal,
                tipoDocumento: tipoDocumento
            });

            if (window.seleccionIdGlobal) {
                body.append("seleccion_id", window.seleccionIdGlobal);
            }

            const response = await fetch("/examen/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: body.toString()
            });

            const data = await response.json();

            if (data.success && data.pdf_url) {
                window.open(data.pdf_url, "_blank");
                return;
            }

            if (data.success && data.documentos) {
                (data.documentos || []).forEach((doc) => {
                    const url = `/static/Documentos/${doc}`;
                    window.open(url, "_blank");
                });
                return;
            }

            alert("❌ Error al generar documento: " + (data.error || "desconocido"));
        } catch (error) {
            console.error(error);
            alert("Error de red al generar documento.");
        }
    }

    function mostrarModalSeleccion(opciones, resumenTexto) {
        const contenedor = document.getElementById("opcionesPlanes");
        const resumen = document.getElementById("resumenProgramas");

        if (!contenedor) return;

        contenedor.innerHTML = "";

        if (resumen) {
            resumen.textContent = resumenTexto || "";
        }

        opciones.forEach((op) => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "btn";
            btn.textContent = `${op.programa} · plan ${op.planEstudios}${op.especializacion ? " · " + op.especializacion : ""}`;

            btn.addEventListener("click", () => {
                seleccionarPlan(op.id);
            });

            contenedor.appendChild(btn);
        });

        abrirModal("modalSeleccionPlan");
    }

    window.cerrarModalSeleccion = function () {
        cerrarModal("modalSeleccionPlan");
    };

    async function seleccionarPlan(seleccionId) {
        if (!window.numeroDeCuentaGlobal) {
            alert("No se encontró el número de cuenta.");
            return;
        }

        try {
            window.seleccionIdGlobal = String(seleccionId);

            const body = new URLSearchParams({
                numeroDeCuenta: window.numeroDeCuentaGlobal,
                seleccion_id: window.seleccionIdGlobal
            });

            const response = await fetch("/examen/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: body.toString()
            });

            const data = await response.json();

            if (!data.success) {
                alert(data.error || "No se pudo seleccionar el plan.");
                return;
            }

            cerrarModal("modalSeleccionPlan");
            mostrarNombreAlumno(data.nombreCompleto || "");

            if (data.tipo_modal === "omit_modal") {
                mostrarBotonesExpediente();
                setStatus("✅ Plan seleccionado. Ya puedes generar documentos.");
                return;
            }

            if (data.tipo_modal === "solo_fecha_hora") {
                limpiarFormularioModal();
                toggleSinodales(false);
                abrirModal("modal-fecha-hora");
                setStatus("Completa fecha, hora y datos de acta.");
                return;
            }

            limpiarFormularioModal();
            toggleSinodales(true);
            abrirModal("modal-fecha-hora");
            setStatus("Completa el formulario para continuar.");
        } catch (error) {
            console.error(error);
            alert("Ocurrió un error al seleccionar el plan.");
        }
    }
});
