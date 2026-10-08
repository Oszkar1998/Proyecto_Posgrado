document.addEventListener("DOMContentLoaded", () => {
    obtenerContador();
    bindBusquedaAutomatica();
    bindNuevoUsuarioForm();
    resetUI();
});

/* =========================
   UTILIDADES GENERALES
========================= */
function setHint(msg) {
    const hint = document.getElementById("hint");
    if (hint) hint.textContent = msg || "";
}

function resetUI() {
    setHint("Escribe tu número de cuenta (9 dígitos). Validaremos automáticamente.");
}

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add("active");
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove("active");
}

/* =========================
   BÚSQUEDA AUTOMÁTICA
========================= */
function bindBusquedaAutomatica() {
    const searchForm = document.getElementById("searchForm");
    const cuentaInput = document.getElementById("numDeCuenta");

    if (searchForm) {
        searchForm.addEventListener("submit", (e) => e.preventDefault());
    }

    if (!cuentaInput) return;

    let timer;

    cuentaInput.addEventListener("input", () => {
        clearTimeout(timer);

        const valor = (cuentaInput.value || "").replace(/\D/g, "").slice(0, 9);
        cuentaInput.value = valor;

        if (!/^\d{9}$/.test(valor)) {
            resetUI();
            return;
        }

        setHint("Validando número de cuenta...");

        timer = setTimeout(() => {
            consultarRevision(valor);
        }, 250);
    });
}

async function consultarRevision(numCuenta) {
    spinner.show("Generando documento...");
    try {
        const res = await fetch("/revision/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `numDeCuenta=${encodeURIComponent(numCuenta)}`
        });

        const data = await res.json();

        if (data.success) {
            setHint("");

            if (data.multiples && data.multiples.length > 1) {
                spinner.hide();
                mostrarModalSeleccion(data.multiples, numCuenta, data.resumen);
                return;
            }

            if (data.pdf_url) {
                spinner.hide();
                window.open(data.pdf_url, "_blank");
                await actualizarContadorAutomaticamente();
                setTimeout(() => window.location.reload(), 500);
                return;
            }

            spinner.hide();
            toast.error("No se pudo generar el documento.");
            return;
        }

        if (data.no_encontrado) {
            spinner.hide();
            mostrarModalConfirmacion(numCuenta);
            return;
        }

        spinner.hide();
        resetUI();
        if (data.error) {
            toast.error(data.error);
        }
    } catch (error) {
        spinner.hide();
        console.error("Error al consultar revisión:", error);
        resetUI();
        toast.error("Ocurrió un error al consultar la información.");
    }
}


/* =========================
   CONTADOR
========================= */
function obtenerContador() {
    fetch("/revision/obtener_contador")
        .then(response => response.json())
        .then(data => {
            const span = document.getElementById("contador-valor");
            if (span && typeof data.contador !== "undefined") {
                span.textContent = data.contador;
            }
        })
        .catch(error => {
            console.error("❌ Error al obtener el contador:", error);
        });
}

function mostrarModalContador() {
    const input = document.getElementById("nuevoContador");
    const span = document.getElementById("contador-valor");

    if (input && span) {
        input.value = span.textContent.trim();
    }

    openModal("modal-contador");
}

function cerrarModalContador() {
    closeModal("modal-contador");
}

function actualizarContador() {
    const input = document.getElementById("nuevoContador");
    const nuevoValor = parseInt(input ? input.value : "", 10);

    if (isNaN(nuevoValor) || nuevoValor < 1) {
        toast.warn("Ingrese un valor válido.");
        return;
    }

    fetch("/revision/actualizar_contador", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ nuevoContador: nuevoValor })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const span = document.getElementById("contador-valor");
                if (span) span.textContent = data.contador;
                cerrarModalContador();
            } else {
                toast.error("Error al actualizar el contador: " + (data.error || "Desconocido"));
            }
        })
        .catch(error => {
            console.error("❌ Error en la solicitud:", error);
            toast.error("Ocurrió un error al actualizar el contador.");
        });
}

function actualizarContadorAutomaticamente() {
    return fetch("/revision/incrementar_contador", {
        method: "POST"
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const span = document.getElementById("contador-valor");
                if (span) span.textContent = data.contador;
            } else {
                console.error("⚠ Error al incrementar contador:", data.error);
            }
        })
        .catch(error => {
            console.error("❌ Error al incrementar contador:", error);
        });
}

/* =========================
   COORDINADOR
========================= */
function mostrarModalCoordinador() {
    fetch("/revision/obtener_coordinador")
        .then(response => response.json())
        .then(data => {
            const nombreInput = document.getElementById("nombreCoordinador");
            const sexoSelect = document.getElementById("sexoCoordinador");

            if (nombreInput) nombreInput.value = data.nombre || "";
            if (sexoSelect) sexoSelect.value = data.genero || "";

            openModal("modal-coordinador");
        })
        .catch(error => {
            console.error("❌ Error al obtener coordinador:", error);
            openModal("modal-coordinador");
        });
}

function cerrarModalCoordinador() {
    closeModal("modal-coordinador");
}

function actualizarCoordinador() {
    const nombre = (document.getElementById("nombreCoordinador")?.value || "").trim();
    const sexo = document.getElementById("sexoCoordinador")?.value || "";

    if (!nombre || !sexo) {
        toast.warn("Por favor llena ambos campos.");
        return;
    }

    fetch("/revision/actualizar_coordinador", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nombre: nombre,
            genero: sexo
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                toast.ok("Coordinador actualizado exitosamente.");
                cerrarModalCoordinador();
            } else {
                toast.error("Error al actualizar: " + (data.error || "Desconocido"));
            }
        })
        .catch(error => {
            console.error("❌ Error en la solicitud:", error);
            toast.error("Ocurrió un error al actualizar el coordinador.");
        });
}

/* =========================
   USUARIO NO ENCONTRADO
========================= */
function mostrarModalConfirmacion(numCuenta) {
    const modal = document.getElementById("modal-confirmar-nuevo");
    if (modal) {
        modal.dataset.cuentaTemp = numCuenta;
        openModal("modal-confirmar-nuevo");
    }
}

function cerrarModalConfirmacion() {
    closeModal("modal-confirmar-nuevo");
}

/* =========================
   NUEVO USUARIO
========================= */
function mostrarModalNuevoUsuario() {
    cerrarModalConfirmacion();

    const modalConfirmacion = document.getElementById("modal-confirmar-nuevo");
    const cuentaTemp = modalConfirmacion?.dataset?.cuentaTemp || "";

    const inputCuenta = document.getElementById("nuevoNumCuenta");
    if (inputCuenta) inputCuenta.value = cuentaTemp;

    openModal("modalNuevoUsuario");
}

function cerrarModalNuevoUsuario() {
    closeModal("modalNuevoUsuario");
}

function bindNuevoUsuarioForm() {
    const form = document.getElementById("nuevoUsuarioForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const payload = {
            nombre: (document.getElementById("nuevoNombre")?.value || "").trim(),
            cuenta: (document.getElementById("nuevoNumCuenta")?.value || "").trim(),
            plan: (document.getElementById("nuevoPlan")?.value || "").trim(),
            clave: (document.getElementById("nuevoClave")?.value || "").trim(),
            programa: (document.getElementById("nuevoPrograma")?.value || "").trim(),
            genero: (document.getElementById("nuevoGenero")?.value || "").trim()
        };

        if (!payload.nombre || !payload.cuenta || !payload.plan || !payload.clave || !payload.programa || !payload.genero) {
            toast.warn("Todos los campos son obligatorios.");
            return;
        }

        try {
            const res = await fetch("/revision/registrar_usuario", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (data.success) {
                toast.ok("Usuario registrado correctamente.");
                cerrarModalNuevoUsuario();
                window.location.reload();
            } else {
                toast.error("Error al registrar usuario: " + (data.error || "Desconocido"));
            }
        } catch (error) {
            console.error("❌ Error al registrar usuario:", error);
            toast.error("Ocurrió un error al registrar el usuario.");
        }
    });
}

/* =========================
   SELECCIÓN DE PLAN
========================= */
function mostrarModalSeleccion(opciones, numCuenta, resumenBackend) {
    const resumenEl = document.getElementById("resumenProgramas");
    const contenedor = document.getElementById("opcionesPlanes");

    if (!contenedor) return;

    if (resumenEl) {
        if (resumenBackend) {
            resumenEl.textContent = resumenBackend;
        } else {
            const programas = new Set(opciones.map(op => op.programa));
            resumenEl.textContent = "Este alumno tiene: " + Array.from(programas).sort().join(", ");
        }
    }

    contenedor.innerHTML = "";

    opciones.forEach(op => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn";

        const etiqueta = `${op.programa} · plan ${op.planEstudios}${op.especializacion ? " · " + op.especializacion : ""}`;
        btn.textContent = etiqueta;

        btn.addEventListener("click", () => {
            seleccionarPlan(numCuenta, op.id);
        });

        contenedor.appendChild(btn);
    });

    openModal("modalSeleccionPlan");
}

function cerrarModalSeleccion() {
    closeModal("modalSeleccionPlan");
}

function seleccionarPlan(numCuenta, seleccionId) {
    spinner.show("Generando documento...");
    fetch("/revision/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `numDeCuenta=${encodeURIComponent(numCuenta)}&seleccion_id=${encodeURIComponent(seleccionId)}`
    })
        .then(response => response.json())
        .then(async data => {
            if (data.success) {
                if (data.pdf_url) {
                    spinner.hide();
                    window.open(data.pdf_url, "_blank");
                }
                cerrarModalSeleccion();
                await actualizarContadorAutomaticamente();
                setTimeout(() => window.location.reload(), 500);
            } else {
                spinner.hide();
                toast.error(data.error || "Ocurrió un error.");
            }
        })
        .catch(error => {
            spinner.hide();
            console.error("Error al seleccionar plan:", error);
            toast.error("Ocurrió un error al seleccionar el plan.");
        });
}

document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;

    [
        "modal-contador",
        "modal-coordinador",
        "modal-confirmar-nuevo",
        "modalNuevoUsuario",
        "modalSeleccionPlan"
    ].forEach(id => closeModal(id));
});
