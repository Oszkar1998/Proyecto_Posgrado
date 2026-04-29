
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
    const inputCuenta = document.getElementById("numeroDeCuenta");
    const msgEstado = document.getElementById("estado-validacion");

    const contBotones = document.getElementById("botones-expediente");
    const btnDocumento1 = document.getElementById("btn-documento-1");
    const btnDocumento2 = document.getElementById("btn-documento-2");

    const contOpcionesDoc2 = document.getElementById("botones-opciones-doc2");
    const btnDoc2SinX = document.getElementById("btn-doc2-sinX");
    const btnDoc2ConX = document.getElementById("btn-doc2-conX");

    form.addEventListener("submit", (e) => e.preventDefault());

    // Estado interno
    let cuentaValidada = "";
    let debounceId = null;

    // ===== UTIL =====
    function setEstado(tipo, texto) {
        msgEstado.className = "estado-validacion " + tipo;
        msgEstado.textContent = texto;
    }

    function limpiarUI() {
        contBotones.style.display = "none";
        contOpcionesDoc2.style.display = "none";
        cuentaValidada = "";
    }

    function soloNumeros(valor) {
        return valor.replace(/\D/g, "").slice(0, 9);
    }

    // ===== VALIDACIÓN =====
    async function validarCuenta() {
        const numeroDeCuenta = (inputCuenta.value || "").trim();

        if (!numeroDeCuenta) return;

        setEstado("info", "Validando número de cuenta...");

        try {
            const response = await fetch("/dgae/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({ numeroDeCuenta })
            });

            const data = await response.json();

            if (data.success) {
                cuentaValidada = numeroDeCuenta;
                setEstado("ok", "✅ Cuenta validada. Puedes generar documentos.");
                contBotones.style.display = "block";
            } else {
                limpiarUI();
                setEstado("error", data.error || "Cuenta no válida.");
            }

        } catch (error) {
            console.error(error);
            limpiarUI();
            setEstado("error", "Error de red al validar.");
        }
    }

    // ===== INPUT =====
    inputCuenta.addEventListener("input", () => {
        let valor = soloNumeros(inputCuenta.value);
        inputCuenta.value = valor;

        limpiarUI();

        if (debounceId) clearTimeout(debounceId);

        if (valor.length < 9) {
            setEstado("warn", "Escribe tu número completo (9 dígitos)...");
            return;
        }

        setEstado("info", "Validando automáticamente...");

        debounceId = setTimeout(() => {
            validarCuenta();
        }, 300);
    });

    inputCuenta.addEventListener("blur", () => {
        const val = inputCuenta.value.trim();
        if (val.length === 9 && cuentaValidada !== val) {
            validarCuenta();
        }
    });

    // ===== GENERAR DOCUMENTOS =====
    function generarDocumento(tipoDocumento) {
        const numeroDeCuenta = inputCuenta.value.trim();

        if (!numeroDeCuenta) {
            setEstado("warn", "Primero ingresa el número de cuenta.");
            return;
        }

        if (cuentaValidada !== numeroDeCuenta) {
            setEstado("warn", "Espera a que se valide el número.");
            return;
        }

        setEstado("info", "Generando documento...");

        fetch("/dgae/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                numeroDeCuenta,
                tipoDocumento
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                setEstado("ok", "Documento generado correctamente.");

                (data.documentos || []).forEach(doc => {
                    const url = `/static/Documentos/${doc}`;
                    window.open(url, "_blank");
                });

            } else {
                setEstado("error", data.error || "Error al generar documento.");
            }
        })
        .catch(() => {
            setEstado("error", "Error de red al generar documento.");
        });
    }

    // ===== EVENTOS BOTONES =====
    btnDocumento1.addEventListener("click", () => generarDocumento("documento1"));

    btnDocumento2.addEventListener("click", () => {
        contOpcionesDoc2.style.display = "block";
    });

    btnDoc2SinX.addEventListener("click", () => generarDocumento("documento2_sinX"));
    btnDoc2ConX.addEventListener("click", () => generarDocumento("documento2_conX"));
});
