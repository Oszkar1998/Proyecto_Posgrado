/**
 * toast.js — Sistema de notificaciones para el sistema de Posgrado FI-UNAM
 * Reemplaza todos los alert() del proyecto.
 *
 * Uso:
 *   toast.ok("Datos guardados correctamente.")
 *   toast.warn("Por favor completa todos los campos.")
 *   toast.error("Error de conexión con el servidor.")
 *
 * Incluir en cada HTML antes del cierre de </body>:
 *   <link rel="stylesheet" href="/static/Estilos/toast.css">
 *   <script src="/static/js/toast.js"></script>
 */

const toast = (() => {

    // Crear contenedor si no existe
    function _getContainer() {
        let container = document.getElementById("toast-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "toast-container";
            document.body.appendChild(container);
        }
        return container;
    }

    // Crear y mostrar un toast
    function _show(mensaje, tipo = "ok", duracion = 3500) {
        const container = _getContainer();

        const icons = {
            ok:    "fa-solid fa-circle-check",
            warn:  "fa-solid fa-triangle-exclamation",
            error: "fa-solid fa-circle-xmark"
        };

        const toast = document.createElement("div");
        toast.className = `toast toast-${tipo}`;
        toast.innerHTML = `
            <i class="${icons[tipo]} toast-icon"></i>
            <span class="toast-msg">${mensaje}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;

        container.appendChild(toast);

        // Animación de entrada
        requestAnimationFrame(() => toast.classList.add("toast-visible"));

        // Auto-cerrar
        setTimeout(() => {
            toast.classList.remove("toast-visible");
            toast.addEventListener("transitionend", () => toast.remove(), { once: true });
        }, duracion);
    }

    return {
        ok:    (msg, dur) => _show(msg, "ok",    dur),
        warn:  (msg, dur) => _show(msg, "warn",  dur),
        error: (msg, dur) => _show(msg, "error", dur),
    };

})();