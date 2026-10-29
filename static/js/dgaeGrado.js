document.addEventListener("DOMContentLoaded", () => {
    const inputCuenta = document.getElementById("numeroDeCuenta");
    const msgEstado = document.getElementById("estado-validacion");

    const contBotones = document.getElementById("botones-expediente");
    const btnPresencial = document.getElementById("btn-documento-1");
    const btnVirtual = document.getElementById("btn-documento-2");

    const contOpcionesVirtual = document.getElementById("botones-opciones-virtual");
    const btnVirtualTodasX = document.getElementById("btn-virtual-todas-x");
    const btnVirtualMencion = document.getElementById("btn-virtual-mencion");
    const btnVirtualMedalla = document.getElementById("btn-virtual-medalla");
    const btnVirtualNinguna = document.getElementById("btn-virtual-ninguna");

    const contOpcionesPresencial = document.getElementById("botones-opciones-presencial");
    const btnPresencialTodasX = document.getElementById("btn-presencial-todas-x");
    const btnPresencialMencion = document.getElementById("btn-presencial-mencion");
    const btnPresencialMedalla = document.getElementById("btn-presencial-medalla");
    const btnPresencialNinguna = document.getElementById("btn-presencial-ninguna");

    let cuentaValidada = "";
    let seleccionIdGlobal = "";
    let debounceId = null;

    inicializarUI();
    bindEventos();

    function inicializarUI() {
        limpiarUI();
        setEstado("info", "Escribe tu número de cuenta.");
    }

    function bindEventos() {
        if (inputCuenta) {
            inputCuenta.addEventListener("input", manejarInputCuenta);
            inputCuenta.addEventListener("blur", manejarBlurCuenta);
            inputCuenta.addEventListener("keydown", manejarEnterCuenta);
        }

        if (btnPresencial) {
            btnPresencial.addEventListener("click", () => {
                ocultarOpcionesSecundarias();
                mostrarFlex(contOpcionesPresencial);
                setEstado("info", "Selecciona el tipo de documento presencial.");
            });
        }

        if (btnVirtual) {
            btnVirtual.addEventListener("click", () => {
                ocultarOpcionesSecundarias();
                mostrarFlex(contOpcionesVirtual);
                setEstado("info", "Selecciona el tipo de documento virtual.");
            });
        }

        if (btnVirtualTodasX) {
            btnVirtualTodasX.addEventListener("click", () => abrirDocumento("virtual_todas_x"));
        }

        if (btnVirtualMencion) {
            btnVirtualMencion.addEventListener("click", () => abrirDocumento("virtual_sin_mencion_honorifica"));
        }

        if (btnVirtualMedalla) {
            btnVirtualMedalla.addEventListener("click", () => abrirDocumento("virtual_sin_medalla_alfonso_caso"));
        }

        if (btnVirtualNinguna) {
            btnVirtualNinguna.addEventListener("click", () => abrirDocumento("virtual_sin_mencion_y_medalla"));
        }

        if (btnPresencialTodasX) {
            btnPresencialTodasX.addEventListener("click", () => abrirDocumento("presencial_todas_x"));
        }

        if (btnPresencialMencion) {
            btnPresencialMencion.addEventListener("click", () => abrirDocumento("presencial_sin_mencion_honorifica"));
        }

        if (btnPresencialMedalla) {
            btnPresencialMedalla.addEventListener("click", () => abrirDocumento("presencial_sin_medalla_alfonso_caso"));
        }

        if (btnPresencialNinguna) {
            btnPresencialNinguna.addEventListener("click", () => abrirDocumento("presencial_sin_mencion_y_medalla"));
        }
    }

    function setEstado(tipo, texto) {
        if (!msgEstado) return;
        msgEstado.className = "estado-validacion " + tipo;
        msgEstado.textContent = texto;
    }

    function mostrarFlex(elemento) {
        if (elemento) elemento.style.display = "flex";
    }

    function ocultar(elemento) {
        if (elemento) elemento.style.display = "none";
    }

    function ocultarOpcionesSecundarias() {
        ocultar(contOpcionesVirtual);
        ocultar(contOpcionesPresencial);
    }

    function limpiarUI() {
        ocultar(contBotones);
        ocultarOpcionesSecundarias();
        cuentaValidada = "";
        seleccionIdGlobal = "";
    }

    function normalizarCuenta(valor) {
        return (valor || "").replace(/\D/g, "").slice(0, 9);
    }

    async function validarCuenta() {
        const numeroDeCuenta = (inputCuenta?.value || "").trim();

        if (!numeroDeCuenta) return;

        setEstado("info", "Validando número de cuenta...");

        try {
            const response = await fetch("/dgaeGrado/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({ numeroDeCuenta })
            });

            const data = await response.json();

            if (!data.success) {
                limpiarUI();
                setEstado("error", data.error || "No se pudo validar la cuenta.");
                return;
            }

            if (data.multiples && data.multiples.length > 1) {
                cuentaValidada = numeroDeCuenta;
                seleccionIdGlobal = "";
                ocultar(contBotones);
                ocultarOpcionesSecundarias();
                mostrarModalSeleccion(data.multiples, data.resumen || "");
                setEstado("warn", "Selecciona el plan que deseas usar.");
                return;
            }

            cuentaValidada = numeroDeCuenta;
            setEstado("ok", "Cuenta validada correctamente.");
            mostrarFlex(contBotones);

        } catch (error) {
            console.error(error);
            limpiarUI();
            setEstado("error", "Error de red al validar la cuenta.");
        }
    }

    function mostrarModalSeleccion(opciones, resumenTexto) {
        let modal = document.getElementById("modalSeleccionPlanGrado");

        if (!modal) {
            modal = document.createElement("div");
            modal.id = "modalSeleccionPlanGrado";
            modal.className = "modal";

            modal.innerHTML = `
                <div class="modal-content">
                    <h2>Selecciona el plan para generar DGAE Grado</h2>
                    <p id="resumenProgramasGrado"></p>
                    <div id="opcionesPlanesGrado" class="opciones-planes"></div>
                    <button type="button" id="cerrarModalSeleccionGrado">Cerrar</button>
                </div>
            `;

            document.body.appendChild(modal);

            const btnCerrar = document.getElementById("cerrarModalSeleccionGrado");
            if (btnCerrar) {
                btnCerrar.addEventListener("click", cerrarModalSeleccion);
            }
        }

        const contenedor = document.getElementById("opcionesPlanesGrado");
        const resumen = document.getElementById("resumenProgramasGrado");

        if (!contenedor || !resumen) return;

        contenedor.innerHTML = "";
        resumen.textContent = resumenTexto || "";

        opciones.forEach(op => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.textContent = `${op.programa} · plan ${op.planEstudios} · ${op.especializacion || ""}`;

            btn.addEventListener("click", () => {
                seleccionIdGlobal = String(op.id);
                cerrarModalSeleccion();
                setEstado("ok", `Plan seleccionado: ${op.programa} · ${op.planEstudios}`);
                mostrarFlex(contBotones);
                ocultarOpcionesSecundarias();
            });

            contenedor.appendChild(btn);
        });

        modal.style.display = "flex";
    }

    function cerrarModalSeleccion() {
        const modal = document.getElementById("modalSeleccionPlanGrado");
        if (modal) {
            modal.style.display = "none";
        }
    }

    window.cerrarModalSeleccionGrado = cerrarModalSeleccion;

    function manejarInputCuenta() {
        if (!inputCuenta) return;

        inputCuenta.value = normalizarCuenta(inputCuenta.value);
        limpiarUI();

        if (debounceId) clearTimeout(debounceId);

        const val = inputCuenta.value.trim();

        if (val.length < 9) {
            setEstado("warn", "Escribe tu número de cuenta completo (9 dígitos).");
            return;
        }

        if (!/^\d{9}$/.test(val)) {
            setEstado("warn", "Solo se permiten números.");
            return;
        }

        setEstado("info", "Validando automáticamente...");
        debounceId = setTimeout(() => validarCuenta(), 350);
    }

    function manejarBlurCuenta() {
        const val = (inputCuenta?.value || "").trim();
        if (val.length === 9 && cuentaValidada !== val) {
            validarCuenta();
        }
    }

    function manejarEnterCuenta(event) {
        if (event.key !== "Enter") return;
        event.preventDefault();

        const val = (inputCuenta?.value || "").trim();
        if (val.length === 9 && cuentaValidada !== val) {
            validarCuenta();
        }
    }

    function abrirDocumento(tipoDocumento) {
        const numeroDeCuenta = (inputCuenta?.value || "").trim();

        if (!numeroDeCuenta) {
            setEstado("warn", "Primero escribe el número de cuenta.");
            return;
        }

        if (cuentaValidada !== numeroDeCuenta) {
            setEstado("warn", "Espera a que se valide la cuenta.");
            return;
        }

        setEstado("info", "Generando documento...");
        spinner.show("Generando documento...");

        const body = new URLSearchParams({
            numeroDeCuenta,
            tipoDocumento
        });

        if (seleccionIdGlobal) {
            body.append("seleccion_id", seleccionIdGlobal);
        }

        fetch("/dgaeGrado/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: body
        })
            .then(response => response.json())
            .then(data => {
                spinner.hide();
                if (data.success && data.documento) {
                    setEstado("ok", "Documento generado correctamente.");
                    window.open(data.documento, "_blank");
                } else {
                    setEstado("error", data.error || "No se pudo generar el documento.");
                }
            })
            .catch(error => {
                spinner.hide();
                console.error(error);
                setEstado("error", "Error de red al generar el documento.");
            });
    }

    // ESC, clic fuera y foco: modal.js (el modal se crea por código; se detecta al aparecer)
    Modal.registrar("modalSeleccionPlanGrado", cerrarModalSeleccion);
});
