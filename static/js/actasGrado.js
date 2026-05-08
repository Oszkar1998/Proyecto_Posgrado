// static/js/actasGrado.js (LIMPIO)

function abrirModal(id) {
  const m = document.getElementById(id);
  if (m) m.style.display = "flex";
}

function cerrarModal(id) {
  const m = document.getElementById(id);
  if (m) m.style.display = "none";
}

function cerrarFlash() {
  const f = document.getElementById("flash-overlay");
  if (f) f.style.display = "none";
}

function abrirModalFechaExtra(campo) {
  const modal = document.getElementById("modal-fecha-extra-acta");
  const inputCampo = document.getElementById("campoFechaExtra");
  const titulo = document.getElementById("tituloFechaExtra");
  const descripcion = document.getElementById("descripcionFechaExtra");
  const opcionesPago = document.getElementById("opcionesPagoSinodales");

  if (!modal || !inputCampo || !titulo || !descripcion) {
    alert("No existe el modal de fecha extra en el HTML.");
    return;
  }

  inputCampo.value = campo;

  if (campo === "pagoSinodales") {
    titulo.textContent = "PAGO SINODALES";
    descripcion.textContent = "";
    if (opcionesPago) opcionesPago.style.display = "grid";

    const pago = document.getElementById("seccionPagoFecha");
    const busqueda = document.getElementById("seccionBusquedaPagoSinodales");

    if (pago) pago.style.display = "none";
    if (busqueda) busqueda.style.display = "none";
  }

  if (campo === "dgaeEntregaCarpeta") {
    titulo.textContent = "DGAE ENTREGA CARPETA";
    descripcion.textContent = "Ingresa número de cuenta, folio y la fecha de entrega de carpeta a DGAE.";
    if (opcionesPago) opcionesPago.style.display = "none";
    mostrarSeccionPagoSinodales("pago");
  }

  abrirModal("modal-fecha-extra-acta");
}

function mostrarSeccionPagoSinodales(seccion) {
  const pago = document.getElementById("seccionPagoFecha");
  const busqueda = document.getElementById("seccionBusquedaPagoSinodales");
  const descripcion = document.getElementById("descripcionFechaExtra");

  if (!pago || !busqueda) return;

  if (seccion === "pago") {
    pago.style.display = "block";
    busqueda.style.display = "none";
    if (descripcion) descripcion.textContent = "Ingresa número de cuenta, folio y la fecha de pago de sinodales.";
  }

  if (seccion === "busqueda") {
    pago.style.display = "none";
    busqueda.style.display = "block";
    if (descripcion) descripcion.textContent = "";
  }
}

async function buscarPagoSinodales() {
  const sinodal = document.getElementById("buscarSinodalPago").value.trim();
  const fechaInicio = document.getElementById("buscarPagoFechaInicio").value;
  const fechaFin = document.getElementById("buscarPagoFechaFin").value;
  const contenedor = document.getElementById("resultadosPagoSinodales");

  contenedor.innerHTML = "";

  if (!sinodal) {
    contenedor.innerHTML = `<p style="color:#ff8080;">Ingresa el nombre del sinodal.</p>`;
    return;
  }

  if ((fechaInicio && !fechaFin) || (!fechaInicio && fechaFin)) {
    contenedor.innerHTML = `<p style="color:#ff8080;">Si usas rango de fechas, coloca inicio y fin.</p>`;
    return;
  }

  let resp;
  let data;

  try {
    resp = await fetch("/actasGrado/buscar_pago_sinodales", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        sinodal,
        fechaInicio,
        fechaFin
      })
    });

    data = await resp.json();
  } catch (error) {
    contenedor.innerHTML = `<p style="color:#ff8080;">Error al conectar con el servidor.</p>`;
    return;
  }

  if (!resp.ok || !data.ok) {
    contenedor.innerHTML = `<p style="color:#ff8080;">${data.error || "Error en la búsqueda."}</p>`;
    return;
  }

  if (data.resultados.length === 0) {
    contenedor.innerHTML = `<p style="color:#f7c948;">No se encontraron coincidencias.</p>`;
    return;
  }

  let html = `
    <h3 style="color:#f7c948;">${data.resultados.length} resultado(s)</h3>
    <div style="max-height:260px; overflow:auto;">
  `;

  data.resultados.forEach(r => {
    html += `
      <div style="
        background:#1f2a37;
        border:1px solid rgba(247,201,72,.25);
        border-radius:10px;
        padding:12px;
        margin-bottom:10px;
        color:white;
      ">
        <strong>${r.nombreCompleto}</strong><br>
        Cuenta: ${r.numCuenta}<br>
        Folio: ${r.folio}<br>
        Fecha del acta: ${r.fechaActa}<br>
        Pago sinodales: <strong>${r.pagoSinodales}</strong>
      </div>
    `;
  });

  html += `</div>`;
  contenedor.innerHTML = html;
}

/**
 * Busca un acta (numCuenta + folio) y rellena el formulario de modificación.
 * Requiere backend: POST /actasGrado/get_acta (JSON) -> retorna los campos.
 */
async function buscarActaParaModificar() {
  const numCuentaEl = document.getElementById("mod_numCuenta_buscar");
  const folioEl = document.getElementById("mod_folio_buscar");

  if (!numCuentaEl || !folioEl) {
    alert("No existe el formulario de búsqueda para modificar en el HTML.");
    return;
  }

  const numCuenta = (numCuentaEl.value || "").trim();
  const folio = (folioEl.value || "").trim();

  if (!numCuenta || !folio) {
    alert("Ingresa número de cuenta y folio.");
    return;
  }

  let resp;
  try {
    resp = await fetch("/actasGrado/get_acta", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ numCuenta, folio }),
    });
  } catch (e) {
    alert("No se pudo conectar con el servidor.");
    return;
  }

  let data = {};
  try {
    data = await resp.json();
  } catch (e) {
    // si no viene json
  }

  if (!resp.ok) {
    alert(data.error || "No se encontró el acta.");
    return;
  }

  // Guardar llaves originales (hidden)
  const oldNum = document.getElementById("old_numCuenta");
  const oldFol = document.getElementById("old_folio");
  if (oldNum) oldNum.value = data.numCuenta ?? "";
  if (oldFol) oldFol.value = data.folio ?? "";

  // Helper para setear valores sin tronar si no existe el input
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.value = (val ?? "");
  };

  setVal("mod_folio", data.folio);
  setVal("mod_numCuenta", data.numCuenta);
  setVal("mod_nombreCompleto", data.nombreCompleto);
  setVal("mod_grado", data.grado);
  setVal("mod_semestreIngreso", data.semestreIngreso);
  setVal("mod_semestreEgreso", data.semestreEgreso);
  setVal("mod_promedio", data.promedio);
  setVal("mod_planEstudios", data.planEstudios);
  setVal("mod_dia", data.dia);
  setVal("mod_mes", data.mes);
  setVal("mod_anio", data.anio);
  setVal("mod_nacionalidad", data.nacionalidad);
  setVal("mod_resultado", data.resultado);
  setVal("mod_presidente", data.presidente);
  setVal("mod_secretario", data.secretario);
  setVal("mod_vocal1", data.vocal1);
  setVal("mod_vocal2", data.vocal2);
  setVal("mod_vocal3", data.vocal3);
  setVal("mod_sexo", data.sexo);
}

document.addEventListener("DOMContentLoaded", () => {
  // 1) Abrir PDF desde la lista
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

  // 2) Abrir modales según query param ?open=
  const params = new URLSearchParams(window.location.search);
  const open = params.get("open");

  if (open === "capturar") abrirModal("modal-capturar-acta");
  if (open === "buscar") abrirModal("modal-buscar-acta");
  if (open === "modificar") abrirModal("modal-modificar-acta");
  if (open === "pagoSinodales") abrirModalFechaExtra("pagoSinodales");
  if (open === "dgaeEntregaCarpeta") abrirModalFechaExtra("dgaeEntregaCarpeta");

  // 3) Cerrar con ESC
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    cerrarModal("modal-capturar-acta");
    cerrarModal("modal-buscar-acta");
    cerrarModal("modal-modificar-acta");
    cerrarModal("modal-fecha-extra-acta");
    cerrarFlash();
  });

  // 4) Click fuera para cerrar modales + flash
  document.addEventListener("click", (e) => {
    ["modal-capturar-acta", "modal-buscar-acta", "modal-modificar-acta", "modal-fecha-extra-acta"].forEach((id) => {
      const m = document.getElementById(id);
      if (m && m.style.display === "flex" && e.target === m) cerrarModal(id);
    });

    const f = document.getElementById("flash-overlay");
    if (f && f.style.display === "flex" && e.target === f) cerrarFlash();
  });
});