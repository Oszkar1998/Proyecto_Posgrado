document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");
    const inputCuenta = document.getElementById("numeroDeCuenta");
    const btnIngresar = document.querySelector("button[type='submit']");

    const botonesDocumentos = document.getElementById("botones-expediente");
    const btnDocumento1 = document.getElementById("btn-documento-1");
    const btnDocumento2 = document.getElementById("btn-documento-2");
    const botonesOpcionesDoc2 = document.getElementById("botones-opciones-doc2");
    const btnDoc2SinX = document.getElementById("btn-doc2-sinX");
    const btnDoc2ConX = document.getElementById("btn-doc2-conX");

    let seleccionIdGlobal = "";

    if (botonesDocumentos) botonesDocumentos.style.display = "none";
    if (botonesOpcionesDoc2) botonesOpcionesDoc2.style.display = "none";

    function cerrarModalSeleccion() {
        const modal = document.getElementById("modalSeleccionPlan");
        if (modal) modal.style.display = "none";
    }

    window.cerrarModalSeleccion = cerrarModalSeleccion;

    // ESC, clic fuera y foco: modal.js
    Modal.registrar("modalSeleccionPlan", cerrarModalSeleccion);

    function mostrarBotonesDocumentos() {
        if (btnIngresar) btnIngresar.style.display = "none";
        if (botonesDocumentos) botonesDocumentos.style.display = "block";
        if (botonesOpcionesDoc2) botonesOpcionesDoc2.style.display = "none";
    }

    function validarCuenta() {
        const numeroDeCuenta = inputCuenta.value.trim();

        seleccionIdGlobal = "";

        if (botonesDocumentos) botonesDocumentos.style.display = "none";
        if (botonesOpcionesDoc2) botonesOpcionesDoc2.style.display = "none";

        if (!/^\d{9}$/.test(numeroDeCuenta)) return;

        fetch("/dgae/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                numeroDeCuenta: numeroDeCuenta
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                toast.error(data.error || "No se encontró la cuenta.");
                return;
            }

            if (data.multiples && data.multiples.length > 1) {
                mostrarModalSeleccion(data.multiples, data.resumen || "");
                return;
            }

            mostrarBotonesDocumentos();
        })
        .catch(error => {
            console.error("Error:", error);
            toast.error("Error de red al validar la cuenta.");
        });
    }

    function mostrarModalSeleccion(opciones, resumenTexto) {
        let modal = document.getElementById("modalSeleccionPlan");

        if (!modal) {
            modal = document.createElement("div");
            modal.id = "modalSeleccionPlan";
            modal.className = "modal";

            modal.innerHTML = `
                <div class="modal-content">
                    <h2>Selecciona el plan para generar DGAE</h2>
                    <p id="resumenProgramas"></p>
                    <div id="opcionesPlanes" class="opciones-planes"></div>
                    <button type="button" id="cerrarModalSeleccion">Cerrar</button>
                </div>
            `;

            document.body.appendChild(modal);

            const btnCerrar = document.getElementById("cerrarModalSeleccion");
            if (btnCerrar) {
                btnCerrar.addEventListener("click", cerrarModalSeleccion);
            }
        }

        const contenedor = document.getElementById("opcionesPlanes");
        const resumen = document.getElementById("resumenProgramas");

        if (!contenedor || !resumen) return;

        contenedor.innerHTML = "";
        resumen.textContent = resumenTexto || "";

        opciones.forEach(op => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.textContent = `${op.programa} · plan ${op.planEstudios} · ${op.especializacion || ""}`;

            btn.addEventListener("click", function () {
                seleccionIdGlobal = String(op.id);
                cerrarModalSeleccion();
                mostrarBotonesDocumentos();
            });

            contenedor.appendChild(btn);
        });

        modal.style.display = "flex";
    }

    function obtenerDocumento(tipoDocumento) {
        const numeroDeCuenta = inputCuenta.value.trim();

        const body = new URLSearchParams({
            numeroDeCuenta: numeroDeCuenta,
            tipoDocumento: tipoDocumento
        });

        if (seleccionIdGlobal) {
            body.append("seleccion_id", seleccionIdGlobal);
        }

        spinner.show("Generando documento...");
        fetch("/dgae/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: body
        })
        .then(response => response.json())
        .then(data => {
            spinner.hide();
            if (!data.success) {
                toast.error(data.error || "No se pudo generar el documento.");
                return;
            }
            data.documentos.forEach(doc => {
                window.open(`/static/Documentos/${doc}`, "_blank");
            });
        })
        .catch(error => {
            spinner.hide();
            console.error("Error:", error);
            toast.error("Error de red al generar el documento.");
        });
    }

    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            validarCuenta();
        });
    }

    if (inputCuenta) {
        inputCuenta.addEventListener("input", function () {
            const cuenta = inputCuenta.value.trim();

            if (cuenta.length < 9) {
                seleccionIdGlobal = "";
                if (botonesDocumentos) botonesDocumentos.style.display = "none";
                if (botonesOpcionesDoc2) botonesOpcionesDoc2.style.display = "none";
                if (btnIngresar) btnIngresar.style.display = "block";
                return;
            }

            if (cuenta.length === 9) validarCuenta();
        });
    }

    if (btnDocumento1) {
        btnDocumento1.addEventListener("click", () => obtenerDocumento("documento1"));
    }

    if (btnDocumento2) {
        btnDocumento2.addEventListener("click", () => {
            if (botonesOpcionesDoc2) botonesOpcionesDoc2.style.display = "block";
        });
    }

    if (btnDoc2SinX) {
        btnDoc2SinX.addEventListener("click", () => obtenerDocumento("documento2_sinX"));
    }

    if (btnDoc2ConX) {
        btnDoc2ConX.addEventListener("click", () => obtenerDocumento("documento2_conX"));
    }
});