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

/**
 * escHTML(valor) — Convierte un valor en texto seguro para meterlo en HTML.
 * Úsalo SIEMPRE que pongas datos de la base o del servidor dentro de un
 * template string que vaya a innerHTML (nombres, títulos, folios, etc.).
 *   div.innerHTML = `<strong>${escHTML(r.nombre)}</strong>`;
 * Sirve también dentro de atributos: value="${escHTML(x)}".
 * Es global porque toast.js se carga en todas las páginas.
 */
function escHTML(valor) {
    if (valor === null || valor === undefined) return "";
    return String(valor)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}
window.escHTML = escHTML;

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
        // Errores y avisos se anuncian de inmediato a lectores de pantalla
        toast.setAttribute("role", tipo === "ok" ? "status" : "alert");
        toast.innerHTML = `
            <i class="${icons[tipo]} toast-icon"></i>
            <span class="toast-msg">${escHTML(mensaje)}</span>
            <button type="button" class="toast-close" aria-label="Cerrar notificación" onclick="this.parentElement.remove()">
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