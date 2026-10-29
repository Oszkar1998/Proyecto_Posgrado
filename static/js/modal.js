/**
 * modal.js — Comportamiento común de todos los modales del sistema.
 *
 * Cada módulo sigue abriendo y cerrando sus modales con sus propias
 * funciones (mostrarModalX / cerrarModalX). Solo tiene que registrarlos:
 *
 *     Modal.registrar("modal-capturar", cerrarModalCapturar);
 *     Modal.registrar("modal-contador", () => closeModal("modal-contador"));
 *
 * A partir de ahí, modal.js se encarga de:
 *   - ESC: cierra solo el modal de hasta arriba (el último que se abrió).
 *   - Clic fuera (en el fondo oscuro): cierra el modal. Si el usuario ya
 *     escribió algo en el formulario, NO lo cierra y avisa, para no perder
 *     datos por un clic accidental. Con ESC o el botón Cerrar sí se cierra.
 *   - Foco: al abrir, el cursor pasa al primer campo del modal; Tab no se
 *     sale del modal; al cerrar, el foco regresa al botón que lo abrió.
 *
 * La función de cierre registrada es la del módulo, así que también se
 * ejecuta lo que esa función haga además de ocultar (limpiar, etc.).
 *
 * Opciones:  Modal.registrar(id, cerrar, { clicFuera: false })
 *   clicFuera  false = el clic en el fondo no cierra este modal.
 *
 * Se carga en base.html antes del JS de cada módulo.
 */
const Modal = (() => {

    const registrados = new Map();   // id -> { cerrar, opciones }
    const pila = [];                 // ids abiertos, el último es el de arriba
    const estado = new Map();        // id -> { abridor, editado }

    const ENFOCABLES = [
        "a[href]", "button:not([disabled])", "input:not([disabled]):not([type=hidden])",
        "select:not([disabled])", "textarea:not([disabled])", "[tabindex]:not([tabindex='-1'])"
    ].join(",");
    const CAMPOS = "input:not([type=hidden]):not([type=button]):not([type=submit]), select, textarea";

    function visible(el) {
        if (!el || !el.isConnected) return false;
        const cs = getComputedStyle(el);
        return cs.display !== "none" && cs.visibility !== "hidden";
    }

    function enfocables(el) {
        return [...el.querySelectorAll(ENFOCABLES)].filter(x => x.getClientRects().length);
    }

    function alAbrir(id, el) {
        const abridor = document.activeElement;
        estado.set(id, { abridor, editado: false });
        pila.push(id);
        el.classList.add("modal-sistema");   // base.css la usa para ajustar la ventana en celular
        if (!el.hasAttribute("role")) el.setAttribute("role", "dialog");
        el.setAttribute("aria-modal", "true");
        // Esto corre justo después de que el módulo terminó de mostrar el modal
        if (el.contains(document.activeElement)) return;  // el módulo ya puso el foco
        const campo = [...el.querySelectorAll(CAMPOS)].find(c => c.getClientRects().length);
        const destino = campo || enfocables(el)[0];
        if (destino) destino.focus({ preventScroll: true });
    }

    function alCerrar(id) {
        const i = pila.indexOf(id);
        if (i !== -1) pila.splice(i, 1);
        const st = estado.get(id);
        estado.delete(id);
        // Devolvemos el foco solo si se quedó "perdido": dentro del modal ya oculto,
        // en el body, o en algo que ya no se ve. Si el módulo lo movió a otro lado, se respeta.
        const act = document.activeElement;
        const el = document.getElementById(id);
        const perdido = !act || act === document.body || (el && el.contains(act)) ||
                        !act.getClientRects().length;
        if (st && st.abridor && st.abridor.isConnected && perdido) {
            st.abridor.focus({ preventScroll: true });
        }
    }

    // Revisa qué modales registrados están visibles y actualiza la pila
    function sincronizar() {
        for (const id of registrados.keys()) {
            const el = document.getElementById(id);
            const abierto = pila.includes(id);
            const ahora = visible(el);
            if (ahora && !abierto) alAbrir(id, el);
            else if (!ahora && abierto) alCerrar(id);
        }
    }

    function cerrar(id) {
        const r = registrados.get(id);
        if (!r) return;
        r.cerrar(id);
        sincronizar();
    }

    function registrar(id, cerrarFn, opciones = {}) {
        registrados.set(id, {
            cerrar: typeof cerrarFn === "function" ? cerrarFn
                  : (x) => { const el = document.getElementById(x); if (el) el.style.display = "none"; },
            opciones: { clicFuera: true, ...opciones }
        });
        sincronizar();
    }

    // --- Detecta aperturas y cierres sin tocar las funciones de cada módulo ---
    let pendiente = false;
    const observador = new MutationObserver(() => {
        if (pendiente) return;
        pendiente = true;
        // Microtarea: se revisa en cuanto el módulo termina su cambio, sin esperar
        // a que el navegador dibuje (en equipos lentos un cuadro puede tardar).
        queueMicrotask(() => { pendiente = false; sincronizar(); });
    });
    observador.observe(document.documentElement, {
        subtree: true, childList: true, attributes: true, attributeFilter: ["style", "class"]
    });

    // --- ¿El usuario escribió algo? ---
    // Solo cuentan eventos reales del teclado/ratón (isTrusted). Si el módulo
    // llena el formulario por código (p. ej. en "Modificar"), no cuenta.
    function marcarEditado(e) {
        if (!e.isTrusted || !pila.length) return;
        for (const id of pila) {
            const el = document.getElementById(id);
            if (el && el.contains(e.target) && e.target.matches(CAMPOS)) {
                const st = estado.get(id);
                if (st) st.editado = true;
            }
        }
    }
    document.addEventListener("input", marcarEditado, true);
    document.addEventListener("change", marcarEditado, true);

    // --- ESC y Tab ---
    document.addEventListener("keydown", (e) => {
        if (!pila.length) return;
        const id = pila[pila.length - 1];
        const el = document.getElementById(id);

        if (e.key === "Escape") {
            e.preventDefault();
            cerrar(id);
            return;
        }

        if (e.key === "Tab" && el) {
            const f = enfocables(el);
            if (!f.length) return;
            const primero = f[0], ultimo = f[f.length - 1];
            if (!el.contains(document.activeElement)) { e.preventDefault(); primero.focus(); }
            else if (e.shiftKey && document.activeElement === primero) { e.preventDefault(); ultimo.focus(); }
            else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primero.focus(); }
        }
    });

    // --- Clic en el fondo ---
    // Se exige que el clic EMPIECE y TERMINE en el fondo: así, seleccionar texto
    // dentro del modal y soltar el ratón afuera no lo cierra.
    let inicioEnFondo = null;
    document.addEventListener("mousedown", (e) => { inicioEnFondo = e.target; }, true);
    document.addEventListener("click", (e) => {
        if (!pila.length) return;
        const id = pila[pila.length - 1];
        const el = document.getElementById(id);
        const r = registrados.get(id);
        if (!el || e.target !== el || inicioEnFondo !== el || !r.opciones.clicFuera) return;

        const st = estado.get(id);
        if (st && st.editado) {
            // toast se declara con const en toast.js: no vive en window, por eso typeof
            if (typeof toast !== "undefined") toast.warn("Tienes datos sin guardar. Usa Cerrar o ESC si quieres salir sin guardar.");
            return;
        }
        cerrar(id);
    });

    return { registrar, cerrar, abiertos: () => [...pila] };
})();

window.Modal = Modal;
