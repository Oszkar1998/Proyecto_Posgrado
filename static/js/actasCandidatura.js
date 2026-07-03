function abrirModal(id) {
  const m = document.getElementById(id);
  if (m) m.style.display = "flex";
}

function cerrarModal(id) {
  const m = document.getElementById(id);
  if (m) m.style.display = "none";
}

/* =========================
   MODIFICAR — buscar registros por cuenta
========================= */
async function buscarParaModificar() {
  const inputCuenta = document.getElementById("mod_numeroCuenta_buscar");
  const lista = document.getElementById("mod_lista_registros");
  const formFields = document.getElementById("mod_form_fields");

  const numeroCuenta = (inputCuenta.value || "").trim();

  if (!numeroCuenta) {
    toast.warn("Ingresa el número de cuenta.");
    return;
  }

  lista.innerHTML = "";
  formFields.style.display = "none";

  try {
    const res = await fetch("/actasCandidatura/buscar_por_cuenta", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ numeroCuenta })
    });

    const data = await res.json();

    if (!data.success) {
      toast.error(data.error || "No se encontraron registros.");
      return;
    }

    data.registros.forEach(reg => {
      const div = document.createElement("div");
      div.className = "resultado-item";
      div.innerHTML = `
        <strong>${reg.nombre}</strong><br>
        Fecha: ${reg.fecha} &nbsp;·&nbsp; Evaluación: ${reg.evaluacion} &nbsp;·&nbsp; Resultado: ${reg.resultadoExamen}
        <div style="margin-top:6px; font-size:13px; color:#aaa;">Haz clic para editar este registro</div>
      `;
      div.style.cursor = "pointer";
      div.addEventListener("click", () => cargarRegistroParaModificar(reg.id));
      lista.appendChild(div);
    });

  } catch (error) {
    console.error(error);
    toast.error("Error de conexión con el servidor.");
  }
}

async function cargarRegistroParaModificar(id) {
  try {
    const res = await fetch("/actasCandidatura/get_acta", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id })
    });

    const data = await res.json();

    if (data.error) {
      toast.error(data.error);
      return;
    }

    const setVal = (elemId, val) => {
      const el = document.getElementById(elemId);
      if (el) el.value = (val ?? "");
    };

    setVal("mod_id", data.id);
    setVal("mod_numeroCuenta", data.numeroCuenta);
    setVal("mod_nombre", data.nombre);
    setVal("mod_semestreIngreso", data.semestreIngreso);
    setVal("mod_semestrePresentado", data.semestrePresentado);
    setVal("mod_evaluacion", data.evaluacion);
    setVal("mod_fecha", data.fecha);
    setVal("mod_hora", data.hora);
    setVal("mod_resultadoExamen", data.resultadoExamen);
    setVal("mod_presidente", data.presidente);
    setVal("mod_secretario", data.secretario);
    setVal("mod_vocal1", data.vocal1);
    setVal("mod_vocal2", data.vocal2);
    setVal("mod_vocal3", data.vocal3);

    document.getElementById("mod_form_fields").style.display = "block";

  } catch (error) {
    console.error(error);
    toast.error("Error al cargar el registro.");
  }
}

/* =========================
   INICIALIZACIÓN
========================= */
document.addEventListener("DOMContentLoaded", () => {

  // Abrir PDF desde los resultados de búsqueda principal
  document.body.addEventListener("click", (ev) => {
    const btn = ev.target.closest(".abrir-acta");
    if (!btn) return;

    ev.preventDefault();
    const url = btn.getAttribute("data-url");
    if (!url) return;

    const a = document.createElement("a");
    a.href = url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    a.remove();
  });

  // Abrir modales según query param ?open=
  const params = new URLSearchParams(window.location.search);
  const open = params.get("open");

  if (open === "capturar") abrirModal("modal-capturar-actaCandidatura");
  if (open === "modificar") abrirModal("modal-modificar-actaCandidatura");
  // "verActa" ya no usa modal — lleva directo a la página principal

  // Cerrar con ESC
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    cerrarModal("modal-capturar-actaCandidatura");
    cerrarModal("modal-modificar-actaCandidatura");
  });

  // Cerrar al hacer clic fuera del modal
  document.addEventListener("click", (e) => {
    ["modal-capturar-actaCandidatura", "modal-modificar-actaCandidatura"].forEach(id => {
      const modal = document.getElementById(id);
      if (modal && e.target === modal) {
        modal.style.display = "none";
      }
    });
  });
});
