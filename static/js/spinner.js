/**
 * spinner.js — Indicador de carga para el sistema de Posgrado FI-UNAM
 * Muestra una pantalla de carga mientras se genera un PDF.
 *
 * Uso:
 *   spinner.show()         // Mostrar antes del fetch
 *   spinner.hide()         // Ocultar cuando termina (éxito o error)
 *
 * Incluir en cada HTML antes del cierre de </body>:
 *   <link rel="stylesheet" href="/static/Estilos/spinner.css">
 *   <script src="/static/js/spinner.js"></script>
 */

const spinner = (() => {

    function _getOverlay() {
        let overlay = document.getElementById("spinner-overlay");
        if (!overlay) {
            overlay = document.createElement("div");
            overlay.id = "spinner-overlay";
            overlay.innerHTML = `
                <div class="spinner-box">
                    <div class="spinner-ring"></div>
                    <p class="spinner-msg">Generando documento...</p>
                    <p class="spinner-submsg">Por favor espera</p>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        return overlay;
    }

    function show(mensaje = "Generando documento...") {
        const overlay = _getOverlay();
        overlay.querySelector(".spinner-msg").textContent = mensaje;
        overlay.classList.add("spinner-visible");
        document.body.style.overflow = "hidden"; // evita scroll mientras carga
    }

    function hide() {
        const overlay = document.getElementById("spinner-overlay");
        if (overlay) {
            overlay.classList.remove("spinner-visible");
            document.body.style.overflow = "";
        }
    }

    return { show, hide };

})();