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

  // 3) Cerrar con ESC
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    cerrarModal("modal-capturar-acta");
    cerrarModal("modal-buscar-acta");
    cerrarModal("modal-modificar-acta");
    cerrarFlash();
  });

  // 4) Click fuera para cerrar modales + flash
  document.addEventListener("click", (e) => {
    ["modal-capturar-acta", "modal-buscar-acta", "modal-modificar-acta"].forEach((id) => {
      const m = document.getElementById(id);
      if (m && m.style.display === "flex" && e.target === m) cerrarModal(id);
    });

    const f = document.getElementById("flash-overlay");
    if (f && f.style.display === "flex" && e.target === f) cerrarFlash();
  });
});