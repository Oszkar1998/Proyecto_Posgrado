
document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("numeroDeCuenta");
  const estado = document.getElementById("estado-validacion");
  const botones = document.getElementById("botones-expediente");

  const btnActa = document.getElementById("btn-documento-1");
  const btnCitatorio = document.getElementById("btn-documento-2");

  let cuentaActual = "";
  let timer = null;
  
  obtenerFolioActa();


  // --- helpers UI ---
  function setEstado(texto, cls) {
    if (!estado) return;
    estado.textContent = texto;
    estado.className = `estado-validacion ${cls || ""}`.trim();
  }

  function soloDigitos(v) {
    return (v || "").replace(/\D/g, "");
  }

  function ocultarBotones() {
    if (botones) botones.style.display = "none";
  }

  function mostrarBotones() {
    if (botones) botones.style.display = "block";
  }

  // --- API: consultar cuenta ---
  async function consultarCuenta(num) {
    setEstado("Buscando información…", "info");
    ocultarBotones();

    const formData = new FormData();
    formData.append("numeroDeCuenta", num);

    try {
      const resp = await fetch("/candidatura/consultar", {
        method: "POST",
        body: formData,
        credentials: "same-origin",
      });

      const data = await resp.json();

      if (!resp.ok || !data.success) {
        cuentaActual = "";
        setEstado(data.error || "No se pudo consultar.", "error");
        return;
      }

      // ✅ guardar cuenta válida para generar PDFs después
      cuentaActual = num;

      setEstado(`Encontrado: ${data.nombre || "registro válido"}`, "ok");
      mostrarBotones();
    } catch (e) {
      console.error(e);
      cuentaActual = "";
      setEstado("Error de conexión con el servidor.", "error");
    }
  }

  // --- API: generar PDF (acta / citatorio) ---
  async function generarPDF(tipo) {
    if (!cuentaActual || cuentaActual.length !== 9) {
      toast.warn("Primero ingresa un número de cuenta válido (9 dígitos).");
      return;
    }

    if (tipo === "acta") {
      obtenerFolioActa();
    }

    setEstado(`Generando ${tipo.toUpperCase()}…`, "info");

    const formData = new FormData();
    formData.append("numeroDeCuenta", cuentaActual);
    formData.append("tipo", tipo);

    spinner.show("Generando documento...");
    try {
      const resp = await fetch("/candidatura/generar_pdf", {
        method: "POST",
        body: formData,
        credentials: "same-origin",
      });

      const data = await resp.json();

      if (!resp.ok || !data.success) {
        spinner.hide();
        setEstado(data.error || "No se pudo generar el PDF.", "error");
        return;
      }

      if (data.pdf_url) {
        spinner.hide();
        window.open(data.pdf_url, "_blank");
        setEstado("PDF generado correctamente.", "ok");
      } else {
        spinner.hide();
        setEstado("El servidor no devolvió la URL del PDF.", "error");
      }
    } catch (e) {
      spinner.hide();
      console.error(e);
      setEstado("Error de conexión al generar PDF.", "error");
    }
  }

  // --- eventos botones ---
  if (btnActa) {
    btnActa.addEventListener("click", () => generarPDF("acta"));
  }
  if (btnCitatorio) {
    btnCitatorio.addEventListener("click", () => generarPDF("citatorio"));
  }

  // --- input automático sin enter ---
  if (input) {
    input.addEventListener("input", () => {
      const limpio = soloDigitos(input.value).slice(0, 9);
      input.value = limpio;

      if (timer) clearTimeout(timer);

      if (limpio.length === 0) {
        cuentaActual = "";
        setEstado("Escribe tu número (9 dígitos). Validaremos automáticamente.", "warn");
        ocultarBotones();
        return;
      }

      if (limpio.length < 9) {
        cuentaActual = "";
        setEstado(`Faltan ${9 - limpio.length} dígitos…`, "warn");
        ocultarBotones();
        return;
      }

      // ✅ ya son 9: consulta automático con debounce
      timer = setTimeout(() => consultarCuenta(limpio), 250);
    });
  }

  // ESC, clic fuera y foco: modal.js
  Modal.registrar("modal-capturar", cerrarModalCapturar);
  Modal.registrar("modal-busquedaNombre", cerrarModalBusquedaNombre);
  Modal.registrar("modal-modificarDatos", cerrarModalModificarDatos);
  Modal.registrar("modal-folio", cerrarModalFolioActa);


  // estado inicial
  setEstado("Escribe tu número (9 dígitos). Validaremos automáticamente.", "warn");
  ocultarBotones();
});

function mostrarModalCapturar() {
  const m = document.getElementById("modal-capturar");
  if (m) m.style.display = "flex";
}
function cerrarModalCapturar() {
  const m = document.getElementById("modal-capturar");
  if (m) m.style.display = "none";
}

function mostrarModalBusquedaNombre() {
  const m = document.getElementById("modal-busquedaNombre");
  if (m) m.style.display = "flex";
}
function cerrarModalBusquedaNombre() {
  const m = document.getElementById("modal-busquedaNombre");
  if (m) m.style.display = "none";
}

function mostrarModalModificarDatos() {
  const m = document.getElementById("modal-modificarDatos");
  if (m) m.style.display = "flex";
}
function cerrarModalModificarDatos() {
  const m = document.getElementById("modal-modificarDatos");
  if (m) m.style.display = "none";

  const fields = document.getElementById("mod_form_fields");
  if (fields) fields.style.display = "none";
}


async function buscarPorNombreCandidatura() {
  const nombre = document.getElementById("bus_nombre").value.trim();
  const cont = document.getElementById("bus_resultados");

  if (!nombre) {
    cont.innerHTML = "<p>Escribe un nombre.</p>";
    return;
  }

  cont.innerHTML = "Buscando…";

  try {
    const resp = await fetch(`/candidatura/api/buscar?nombre=${encodeURIComponent(nombre)}`);
    const data = await resp.json();

    if (!Array.isArray(data) || data.length === 0) {
      cont.innerHTML = "<p>No se encontraron resultados.</p>";
      return;
    }

    // El número de cuenta va en data-cuenta (no dentro del onclick) para que
    // un valor con comillas no rompa el botón.
    cont.innerHTML = data.map(r => `
      <div class="resultado-busqueda">
        <b>${escHTML(r.nombre_completo)}</b><br>
        Cuenta: ${escHTML(r.numero_cuenta)}
        <button type="button" class="btn-seleccionar-busqueda" data-cuenta="${escHTML(r.numero_cuenta)}">Seleccionar</button>
      </div>
    `).join("");
    cont.querySelectorAll(".btn-seleccionar-busqueda").forEach(b =>
      b.addEventListener("click", () => cargarDesdeBusqueda(b.dataset.cuenta))
    );
  } catch (e) {
    console.error(e);
    cont.innerHTML = "<p>Error al buscar.</p>";
  }
}

function cargarDesdeBusqueda(numeroCuenta){
  // Cerrar modal búsqueda
  cerrarModalBusquedaNombre();

  // Poner la cuenta en el input principal de consulta
  const inputConsulta = document.getElementById("numeroDeCuenta");
  if (inputConsulta) {
    inputConsulta.value = numeroCuenta;
    inputConsulta.dispatchEvent(new Event("input")); // dispara tu autovalidación
  }
}


async function cargarCandidaturaPorCuenta() {
  const num = document.getElementById("mod_numero_cuenta_buscar").value.trim();
  
  const fields = document.getElementById("mod_form_fields");
  if (fields) fields.style.display = "none"; // ✅ ocultar siempre antes

  if (!num || num.length !== 9) {
    toast.warn("Número de cuenta inválido.");
    return;
  }

  try {
    const resp = await fetch(`/candidatura/api/obtener?numero_cuenta=${encodeURIComponent(num)}`);
    const data = await resp.json();

    if (!data || !data.numero_cuenta) {
      toast.error("No se encontró ese registro.");
      return;
    }

    document.getElementById("mod_nombre_completo").value = data.nombre_completo;
    document.getElementById("mod_numero_cuenta").value = data.numero_cuenta;
    document.getElementById("mod_especialidad").value = data.especialidad;
    document.getElementById("mod_titulo_proyecto").value = data.titulo_proyecto;
    document.getElementById("mod_semestre_ingreso").value = data.semestre_ingreso;
    document.getElementById("mod_semestre_presentado").value = data.semestre_presentado;
    document.getElementById("mod_evaluacion").value = data.evaluacion;
    document.getElementById("mod_presidente").value = data.presidente;
    document.getElementById("mod_secretario").value = data.secretario;
    document.getElementById("mod_vocal1").value = data.vocal1;
    document.getElementById("mod_vocal2").value = data.vocal2;
    document.getElementById("mod_vocal3").value = data.vocal3;
    document.getElementById("mod_sexo").value = data.sexo;
    document.getElementById("mod_modalidad_sede").value = data.modalidad_sede;
    document.getElementById("mod_fecha_examen").value = data.fecha_examen;
    document.getElementById("mod_hora_examen").value = data.hora_examen;
    
    // ✅ MOSTRAR CAMPOS YA CARGADOS
    if (fields) fields.style.display = "block";

  } catch (e) {
    console.error(e);
    toast.error("Error al cargar datos.");
  }
}

async function guardarCambiosCandidatura() {
  const payload = {
    numero_cuenta: document.getElementById("mod_numero_cuenta").value.trim(),
    nombre_completo: document.getElementById("mod_nombre_completo").value.trim(),
    especialidad: document.getElementById("mod_especialidad").value.trim(),
    titulo_proyecto: document.getElementById("mod_titulo_proyecto").value.trim(),
    semestre_ingreso: document.getElementById("mod_semestre_ingreso").value.trim(),
    semestre_presentado: document.getElementById("mod_semestre_presentado").value,
    evaluacion: document.getElementById("mod_evaluacion").value,
    presidente: document.getElementById("mod_presidente").value.trim(),
    secretario: document.getElementById("mod_secretario").value.trim(),
    vocal1: document.getElementById("mod_vocal1").value.trim(),
    vocal2: document.getElementById("mod_vocal2").value.trim(),
    vocal3: document.getElementById("mod_vocal3").value.trim(),
    sexo: document.getElementById("mod_sexo").value,
    modalidad_sede: document.getElementById("mod_modalidad_sede").value.trim(),
    fecha_examen: document.getElementById("mod_fecha_examen").value,
    hora_examen: document.getElementById("mod_hora_examen").value
  };

  try {
    const resp = await fetch("/candidatura/api/actualizar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await resp.json();

    if (!resp.ok || !data.ok) {
      toast.error(data.error || "Error al guardar.");
      return;
    }

    toast.ok("Datos actualizados correctamente.");
    cerrarModalModificarDatos();
  } catch (e) {
    console.error(e);
    toast.error("Error de conexión.");
  }
}

async function guardarCapturaCandidatura() {
  const payload = {
    nombre_completo: document.getElementById("cap_nombre_completo").value.trim(),
    numero_cuenta: document.getElementById("cap_numero_cuenta").value.trim(),
    especialidad: document.getElementById("cap_especialidad").value.trim(),
    titulo_proyecto: document.getElementById("cap_titulo_proyecto").value.trim(),
    semestre_ingreso: document.getElementById("cap_semestre_ingreso").value.trim(),
    semestre_presentado: document.getElementById("cap_semestre_presentado").value,
    evaluacion: document.getElementById("cap_evaluacion").value,
    presidente: document.getElementById("cap_presidente").value.trim(),
    secretario: document.getElementById("cap_secretario").value.trim(),
    vocal1: document.getElementById("cap_vocal1").value.trim(),
    vocal2: document.getElementById("cap_vocal2").value.trim(),
    vocal3: document.getElementById("cap_vocal3").value.trim(),
    sexo: document.getElementById("cap_sexo").value,
    modalidad_sede: document.getElementById("cap_modalidad_sede").value.trim(),
    fecha_examen: document.getElementById("cap_fecha_examen").value,
    hora_examen: document.getElementById("cap_hora_examen").value
  };

  // Validación mínima rápida
  if (!payload.nombre_completo) return toast.warn("Falta: Nombre completo");
  if (!/^\d{9}$/.test(payload.numero_cuenta)) return toast.warn("Número de cuenta inválido (9 dígitos).");
  if (!payload.especialidad) return toast.warn("Falta: Especialidad");
  if (!payload.titulo_proyecto) return toast.warn("Falta: Título del proyecto");
  if (!payload.semestre_ingreso) return toast.warn("Falta: Semestre ingreso");
  if (!payload.semestre_presentado) return toast.warn("Falta: Semestre presentado");
  if (!payload.evaluacion) return toast.warn("Falta: Evaluación");
  if (!payload.presidente) return toast.warn("Falta: Presidente");
  if (!payload.secretario) return toast.warn("Falta: Secretario");
  if (!payload.vocal1) return toast.warn("Falta: Vocal 1");
  if (!payload.vocal2) return toast.warn("Falta: Vocal 2");
  if (!payload.vocal3) return toast.warn("Falta: Vocal 3");
  if (!payload.sexo) return toast.warn("Falta: Sexo");
  if (!payload.modalidad_sede) return toast.warn("Falta: Modalidad / Sede");
  if (!payload.fecha_examen) return toast.warn("Falta: Fecha examen");
  if (!payload.hora_examen) return toast.warn("Falta: Hora examen");

  try {
    const resp = await fetch("/candidatura/api/crear", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await resp.json();

    if (!resp.ok || !data.ok) {
      toast.error(data.error || "Error al guardar.");
      return;
    }

    toast.ok("Registro guardado correctamente");
    cerrarModalCapturar();
  } catch (e) {
    console.error(e);
    toast.error("Error de conexión.");
  }
}

function obtenerFolioActa() {
  fetch("/candidatura/obtener_folio_acta")
    .then(r => r.json())
    .then(data => {
      const span = document.getElementById("folio-valor");
      if (span && typeof data.folio !== "undefined") span.textContent = data.folio;
    })
    .catch(err => console.error("Error folio:", err));
}

function mostrarModalFolioActa() {
  const m = document.getElementById("modal-folio");
  if (m) m.style.display = "flex";
}
function cerrarModalFolioActa() {
  const m = document.getElementById("modal-folio");
  if (m) m.style.display = "none";
}

function actualizarFolioActa() {
  const input = document.getElementById("nuevoFolioActa");
  const nuevo = parseInt(input?.value || "", 10);

  if (isNaN(nuevo) || nuevo < 1) return toast.warn("Ingresa un valor válido.");

  fetch("/candidatura/actualizar_folio_acta", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ nuevoFolio: nuevo })
  })
  .then(r => r.json())
  .then(data => {
    if (!data.success) return toast.error(data.error || "No se pudo actualizar.");
    const span = document.getElementById("folio-valor");
    if (span) span.textContent = data.folio;
    cerrarModalFolioActa();
  })
  .catch(err => console.error(err));
}

// Abrir modal automáticamente cuando vienes desde Captura
window.addEventListener("load", () => {
  const params = new URLSearchParams(window.location.search);

  const open =
    params.get("open") ||
    params.get("modal") ||
    params.get("accion") ||
    params.get("ventana");

  const btnCapturar = document.getElementById("capturar-container");
  const btnBuscar = document.getElementById("busquedaNombre-container");
  const btnModificar = document.getElementById("modificarDatos-container");

  if (btnCapturar) btnCapturar.style.display = "none";
  if (btnBuscar) btnBuscar.style.display = "none";
  if (btnModificar) btnModificar.style.display = "none";

  if (!open) return;

  if (open === "capturar" || open === "captura") {
    mostrarModalCapturar();
  }

  if (open === "buscar" || open === "busqueda" || open === "busquedaNombre") {
    mostrarModalBusquedaNombre();
  }

  if (open === "modificar" || open === "modificarDatos") {
    mostrarModalModificarDatos();
  }
});

