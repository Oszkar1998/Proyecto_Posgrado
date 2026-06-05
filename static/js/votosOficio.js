

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("login-form");
  const cuentaInput = document.getElementById("numeroDeCuenta");
  const hint = document.getElementById("hint");
  const botonesDocumentos = document.getElementById("botones-expediente");
  const btnDocumento2 = document.getElementById("btn-documento-2");

  function setHint(msg) { if (hint) hint.textContent = msg || ""; }

  function resetUI() {
    botonesDocumentos.style.display = "none";
    document.getElementById("botones-expediente").innerHTML = "";
    const m = document.getElementById("modalSeleccionPlanVotos");
    if (m) m.style.display = "none";
    setHint("Escribe tu número completo (9 dígitos)...");
  }

  async function consultarYMostrar(numeroCuenta) {
    // Rellena la tarjetita (nombre/especialización)
    busquedaPorCuenta();

    const res = await fetch("/votosOficio", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `numeroDeCuenta=${encodeURIComponent(numeroCuenta)}`
    });
    const data = await res.json();

    if (data.success) {
      setHint("");
      botonesDocumentos.style.display = "block";

      if (data.multiples && data.multiples.length > 1) {
        mostrarModalSeleccionVotos(data.multiples);
        return;
      }
      if (data.votos_url) {
        btnDocumento2.onclick = () => window.open(data.votos_url, "_blank");
        return;
      }
      alert("No se pudo generar el documento.");
    } else {
      resetUI();
    }
  }

  // Sin botón: no usamos submit; validamos al teclear
  let t;
  cuentaInput.addEventListener("input", function () {
    clearTimeout(t);
    const v = cuentaInput.value.trim();
    const ok = /^\d{9}$/.test(v);
    if (!ok) { resetUI(); return; }
    setHint("Validando…");
    t = setTimeout(() => consultarYMostrar(v), 220);
  });

  // Evita que presionar Enter recargue la página
  form.addEventListener("submit", (e) => e.preventDefault());

  resetUI();
});


// 🔹 Mostrar el modal captura
function mostrarModalCapturar() {
    document.getElementById("modal-capturar").style.display = "flex";
}

// 🔹 Cerrar el modal captura
function cerrarModalCapturar() {
    document.getElementById("modal-capturar").style.display = "none";
}

// 🔹 Cerrar el modal si se presiona ESC
document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        cerrarModalCapturar();
    }
});

// 🔹 Guardar nuevo Captura de Datos
function actualizarCapturar() {
    const data = {
        nombreCompleto: document.getElementById("nombreCompleto").value.trim(),
        numeroDeCuenta: document.getElementById("numeroDeCuentaCap").value.trim(),
        planEstudios: document.getElementById("planEstudios").value.trim(),
        especializacion: document.getElementById("especializacion").value.trim(),
        modalidad: document.getElementById("modalidad").value.trim(),
        tituloOtesina: document.getElementById("tituloOtesina").value.trim(),
        tutor: document.getElementById("tutor").value.trim(),
        sexoTutor: document.getElementById("sexoTutor").value,
        presidente: document.getElementById("presidente").value.trim(),
        vocal1: document.getElementById("vocal1").value.trim(),
        vocal2: document.getElementById("vocal2").value.trim(),
        vocal3: document.getElementById("vocal3").value.trim(),
        secretario: document.getElementById("secretario").value.trim(),
        sexo: document.getElementById("sexoCoordinador").value
    };

    if (!data.nombreCompleto || !data.numeroDeCuenta || !data.planEstudios || !data.modalidad || !data.presidente || !data.secretario || !data.vocal1 || !data.sexo || !data.especializacion) {
        alert("⚠ Por favor completa todos los campos obligatorios.");
        return;
    }

    fetch("/votosOficio/guardar_datos", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(res => {
        if (res.success) {
            alert("✅ Datos guardados correctamente.");
            cerrarModalCapturar();

            // ✅ Limpiar campos del modal
            document.querySelectorAll("#modal-capturar input, #modal-capturar select").forEach(el => {
                el.value = "";
            });

            // ✅ Recargar la página
            location.reload();
        } else {
            alert("❌ Error al guardar: " + res.error);
        }
    })
    .catch(error => {
        console.error("❌ Error en la solicitud:", error);
        alert("❌ Error en la conexión con el servidor.");
    });
}


// 🔹 Mostrar el modal Busqueda por nombre
function mostrarModalBusquedaNombre() {
    document.getElementById("modal-busquedaNombre").style.display = "flex";
}

// 🔹 Cerrar el modal Busqueda por nombre
function cerrarModalBusquedaNombre() {
    document.getElementById("modal-busquedaNombre").style.display = "none";
}

// 🔹 Cerrar el modal si se presiona ESC
document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        cerrarModalBusquedaNombre();
    }
});

function busquedaPorNombre() {
    const nombre = document.getElementById("nombreCompletoBusqueda").value.trim();

    if (!nombre) {
        alert("⚠ Por favor ingresa un nombre.");
        return;
    }

    fetch("/votosOficio/buscar_nombre", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ nombre })
    })
    .then(res => res.json())
    .then(data => {
        const contenedor = document.getElementById("resultadosBusqueda");
        contenedor.innerHTML = "";

        if (data.length === 0) {
            contenedor.innerHTML = "<p style='color: red; font-weight: bold;'>❌ No se encontraron resultados.</p>";
            return;
        }

        data.forEach(item => {
            const div = document.createElement("div");
            div.classList.add("resultado-item");

            div.innerHTML = `
              <p><strong>${item.nombreCompleto}</strong></p>
              <p><strong>Número de cuenta:</strong> ${item.numeroCuenta}</p>
              <p>Especialización: ${item.especializacion}</p>
              <p>Modalidad: ${item.modalidad}</p>
              <button onclick="generarVotosPorId(${item.id})">Votos (5 formatos)</button>
          `;

            contenedor.appendChild(div);
        });
    })
    .catch(error => {
        console.error("Error en búsqueda:", error);
    });
}


function generarVotos(numeroCuenta) {
    window.open(`/votosOficio/votos/${numeroCuenta}`, "_blank");
}

function generarVotosPorId(id) {
    window.open(`/votosOficio/votos_id/${id}`, "_blank");
}


function busquedaPorCuenta() {
    const cuenta = document.getElementById("numeroDeCuenta").value.trim();

    if (!cuenta) {
        alert("⚠ Por favor ingresa el número de cuenta.");
        return;
    }

    fetch("/votosOficio/buscar_cuenta", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ numeroCuenta: cuenta })
    })
    .then(res => res.json())
    .then(data => {
        const contenedor = document.getElementById("botones-expediente");
        contenedor.innerHTML = ""; // Limpiar

        if (data.length === 0) {
            contenedor.innerHTML = "<p style='color: red;'>❌ No se encontraron registros.</p>";
            return;
        }

        data.forEach(item => {
            const div = document.createElement("div");
            div.classList.add("resultado-item");

            div.innerHTML = `
                <p><strong>${item.nombreCompleto}</strong></p>
                <p>Especialización: ${item.especializacion}</p>
                <p>Modalidad: ${item.modalidad}</p>
                <button onclick="generarVotosPorId(${item.id})">Votos (5 formatos)</button>
            `;

            contenedor.appendChild(div);
        });
    })
    .catch(error => {
        console.error("Error:", error);
    });
}


// 🔹 Mostrar el modal Modificar Datos 
function mostrarModalModificarDatos() {
    document.getElementById("modal-modificarDatos").style.display = "flex";
}

// 🔹 Cerrar el modal Modificar Datos
function cerrarModalModificarDatos() {
    document.getElementById("modal-modificarDatos").style.display = "none";
}

// 🔹 Cerrar el modal si se presiona ESC
document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        cerrarModalModificarDatos();
    }
});

function buscarDatosModificar() {
  const numeroCuenta = document.getElementById("numeroCuentaModificar").value.trim();

  fetch("/votosOficio/obtener_datos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ numeroCuenta })
  })
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      alert(data.error || "No se encontraron datos.");
      return;
    }

    if (data.multiples && data.multiples.length > 1) {
      mostrarOpcionesModificar(data.multiples);
      return;
    }

    pintarFormularioModificar(data);
  })
  .catch(err => alert("No se encontraron datos con ese número de cuenta."));
}

function guardarCambiosModificar() {
  try {
    const datos = {
      id: document.getElementById("mod-id").value,
      sexo: document.getElementById("mod-sexo").value,
      numeroCuenta: document.getElementById("mod-numeroCuenta").value,

      nombre: document.getElementById("mod-nombre").value,
      especializacion: document.getElementById("mod-especializacion").value,
      modalidad: document.getElementById("mod-modalidad").value,
      planEstudios: document.getElementById("mod-planEstudios").value,
      tituloTesina: document.getElementById("mod-tituloTesina").value,
      tutor: document.getElementById("mod-tutor").value,
      sexoTutor: document.getElementById("mod-sexoTutor").value,
      presidente: document.getElementById("mod-presidente").value,
      secretario: document.getElementById("mod-secretario").value,
      vocal1: document.getElementById("mod-vocal1").value,
      vocal2: document.getElementById("mod-vocal2").value,
      vocal3: document.getElementById("mod-vocal3").value
    };

    fetch("/votosOficio/modificar_datos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
      alert("✅ Datos actualizados correctamente.");
      cerrarModalModificarDatos();
      // 🔄 Recargar la página automáticamente después de guardar
      location.reload();
    });
  } catch (error) {
    alert("❌ Error al guardar los cambios.");
  }
}


function debounce(fn, ms = 200) {
  let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}

function setupAutocomplete(inputSelector) {
  const input = document.querySelector(inputSelector);
  if (!input) return;

  // 🔧 Envuelve el input en un contenedor propio (si no existe)
  if (!input.parentElement.classList.contains("ac-wrap")) {
    const wrap = document.createElement("div");
    wrap.className = "ac-wrap";
    wrap.style.position = "relative";
    input.parentElement.insertBefore(wrap, input);
    wrap.appendChild(input);
  }
  const wrap = input.parentElement;

  // Crea la lista debajo del input
  const list = document.createElement("div");
  list.className = "ac-list";
  list.style.display = "none";
  wrap.appendChild(list);

  function render(items) {
    if (!items || !items.length) { list.style.display = "none"; return; }
    list.innerHTML = items.map(n => `<div class="ac-item" data-v="${n}">${n}</div>`).join("");
    list.style.display = "block";
  }

  const fetchSuggest = debounce(async () => {
    const q = input.value.trim();
    if (q.length < 2) { list.style.display = "none"; return; }
    try {
      const res = await fetch(`/votosOficio/sinodales?q=${encodeURIComponent(q)}`);
      render(await res.json());
    } catch { list.style.display = "none"; }
  }, 250);

  input.addEventListener("input", fetchSuggest);
  input.addEventListener("focus", fetchSuggest);
  input.addEventListener("blur", () => setTimeout(() => (list.style.display = "none"), 150));

  list.addEventListener("click", (e) => {
    const el = e.target.closest(".ac-item");
    if (el) { input.value = el.dataset.v; list.style.display = "none"; }
  });

  // ENTER = tomar primera sugerencia
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && list.firstChild) {
      e.preventDefault();
      input.value = list.firstChild.dataset.v || list.firstChild.textContent;
      list.style.display = "none";
    }
  });
}


// Actívalo cuando cargue la página (IDs de tus inputs)
document.addEventListener("DOMContentLoaded", () => {
  setupAutocomplete("#presidente");
  setupAutocomplete("#secretario");
  setupAutocomplete("#vocal1");
  setupAutocomplete("#vocal2");
  setupAutocomplete("#vocal3");
});

function mostrarModalSeleccionVotos(opciones) {
  const modal = document.getElementById("modalSeleccionPlanVotos");
  const cont  = document.getElementById("opcionesPlanesVotos");
  if (!modal || !cont) return;

  cont.innerHTML = "";
  opciones.forEach(op => {
    const btn = document.createElement("button");
    btn.className = "btn";
    const etiqueta = `${op.nombreCompleto} · plan ${op.planEstudios}` + (op.especializacion ? ` · ${op.especializacion}` : "");
    btn.textContent = etiqueta;
    btn.onclick = () => generarVotosPorId(op.id);
    cont.appendChild(btn);
  });

  modal.style.display = "flex";
}

function cerrarModalSeleccionVotos() {
  const modal = document.getElementById("modalSeleccionPlanVotos");
  if (modal) modal.style.display = "none";
}



// === Parámetros ===
const CUENTA_LEN = 9;

// === Utils ===
function soloDigitos(str) {
  return /^\d+$/.test(str);
}

function mostrarModalError(msg) {
  const modal = document.getElementById('modalError');
  const msgP = document.getElementById('modalErrorMsg');
  if (!modal) { alert(msg || 'No existe esa cuenta en la base.'); return; }
  if (msgP) msgP.textContent = msg || 'No existe esa cuenta en la base.';
  modal.style.display = 'block';
  void modal.offsetHeight; // reflow
  modal.classList.add('open');
  modal.querySelector('button')?.focus();
}
function cerrarModalError() {
  const modal = document.getElementById('modalError');
  if (modal) {
    modal.classList.remove('open');
    modal.style.display = 'none';
  }
}

// Cerrar modal con Escape y clic fuera
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') cerrarModalError(); });
window.addEventListener('click', (e) => {
  const modal = document.getElementById('modalError');
  if (modal && e.target === modal) cerrarModalError();
});

// Crea (si no existe) y devuelve el panel donde mostramos info
function ensureInfoPanel() {
  let panel = document.getElementById('panelInfo');
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'panelInfo';
    panel.className = 'panel-info';
    // lo colocamos justo después del formulario
    const form = document.getElementById('login-form');
    (form?.parentNode)?.insertBefore(panel, form.nextSibling);
  }
  return panel;
}

// Renderiza objeto plano como lista bonita
function renderKeyVals(obj) {
  if (!obj || typeof obj !== 'object') return '<p>(Sin detalles)</p>';
  const rows = Object.entries(obj)
    .filter(([k, v]) => v != null && v !== '')
    .map(([k, v]) => {
      const key = String(k).replace(/_/g, ' ').toUpperCase();
      return `<div class="kv"><span class="k">${key}:</span> <span class="v">${v}</span></div>`;
    })
    .join('');
  return `<div class="kv-list">${rows || '<p>(Sin detalles)</p>'}</div>`;
}

// Guarda la última URL de votos para abrirla al click
let ultimaVotosURL = null;

// === Lógica principal ===
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const inputCuenta = document.getElementById('numeroDeCuenta');
  if (!form || !inputCuenta) return;

  // 1) Validación “en vivo” PERO solo dispara cuando hay 9 dígitos
  let t;
  inputCuenta.addEventListener('input', () => {
    // opcional: forzar que el input contenga solo dígitos visualmente
    inputCuenta.value = inputCuenta.value.replace(/\D/g, '');

    clearTimeout(t);
    t = setTimeout(() => {
      const val = inputCuenta.value.trim();
      if (val.length === CUENTA_LEN && soloDigitos(val)) {
        form.requestSubmit?.(); // dispara el submit (interceptado abajo)
      } else {
        // si no tiene 9 dígitos, no hacemos nada (ni fetch ni modal)
      }
    }, 350); // debounce corto
  });

  // 2) Interceptar submit y SOLO continuar si hay 9 dígitos
  form.addEventListener('submit', async (evt) => {
    evt.preventDefault();

    const cuenta = inputCuenta.value.trim();
    if (!(cuenta.length === CUENTA_LEN && soloDigitos(cuenta))) {
      // nada de modales aquí; simplemente ignora hasta que cumpla 9 dígitos
      return;
    }

    // Prepara body como application/x-www-form-urlencoded
    const formData = new FormData(form);
    const body = new URLSearchParams();
    for (const pair of formData.entries()) body.append(pair[0], pair[1]);

    try {
      const resp = await fetch(form.action || '/votosOficio', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body
      });
      const data = await resp.json();

      // Caso cuenta NO encontrada
      if (!data || data.success === false) {
        const errMsg = (data && data.error) ? data.error : 'Número de cuenta no encontrado.';
        mostrarModalError(errMsg);
        return;
      }

      // Si el backend regresa múltiples coincidencias
      if (data.multiples) {
        // aquí puedes abrir tu modal de selección si ya lo manejas
        alert('Se encontraron múltiples registros. Selecciona el correcto en la lista.');
        return;
      }

      // === IMPORTANTE: YA NO redirigimos automáticamente al PDF ===
      // Mantén la URL (si la manda el backend), y la abrimos sólo al hacer clic en el botón.
      ultimaVotosURL = data.votos_url || data.voto_url || null;

      // Intenta detectar un objeto "info" razonable en la respuesta
      const info =
        data.info ||
        data.alumno ||
        data.registro ||
        data.detalles ||
        data.datos ||
        null;

      // Si ya tienes la info del alumno, solo deja que el backend renderice su tarjeta normal
      if (data.info || data.alumno || data.registro || data.detalles || data.datos) {
        console.log('Información del alumno cargada.');
      }

      // Guardamos la URL del PDF si existe, pero sin mostrar botón adicional
      ultimaVotosURL = data.votos_url || data.voto_url || null;


      // Click en botón: abrir en nueva pestaña
      const btn = document.getElementById('btnVerVotos');
      btn?.addEventListener('click', async () => {
        if (ultimaVotosURL) {
          // Abrimos directamente la URL que ya envió el backend
          window.open(ultimaVotosURL, '_blank', 'noopener');
          return;
        }
        // Si tu backend NO manda la URL y necesitas generar “on demand”,
        // podrías hacer aquí otro fetch a una ruta tipo /votosOficio/generar
        // con los mismos parámetros, y del JSON sacar la url para abrirla.
        mostrarModalError('No se recibió URL de votos del servidor.');
      });

    } catch (err) {
      console.error('Error comprobando número de cuenta:', err);
      mostrarModalError('Error al verificar. Revisa la conexión o el servidor.');
    }
  });
});

(function(){
  const params = new URLSearchParams(window.location.search);
  const open = params.get("open");

  if (!open) return;

  // Espera a que el DOM esté listo
  window.addEventListener("load", function(){
    if (open === "capturar" && typeof mostrarModalCapturar === "function") {
      mostrarModalCapturar();
    }
    if (open === "buscar" && typeof mostrarModalBusquedaNombre === "function") {
      mostrarModalBusquedaNombre();
    }
    if (open === "modificar" && typeof mostrarModalModificarDatos === "function") {
      mostrarModalModificarDatos();
    }
  });
})();

(function(){
  const params = new URLSearchParams(window.location.search);
  const open = params.get("open");
  if (!open) return;

  window.addEventListener("load", function(){
    if (open === "capturar" && typeof mostrarModalCapturar === "function") {
      mostrarModalCapturar();
    } else if (open === "buscar" && typeof mostrarModalBusquedaNombre === "function") {
      mostrarModalBusquedaNombre();
    } else if (open === "modificar" && typeof mostrarModalModificarDatos === "function") {
      mostrarModalModificarDatos();
    }
  });
})();

function mostrarOpcionesModificar(opciones) {
  const form = document.getElementById("datosModificarForm");

  form.innerHTML = `
    <h3 style="color:#f6c343;">Selecciona el plan que deseas modificar</h3>
  `;

  opciones.forEach(op => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = `${op.nombreCompleto} · plan ${op.planEstudios} · ${op.especializacion || ""}`;
    btn.onclick = () => cargarRegistroModificarPorId(op.id);
    form.appendChild(btn);
  });
}

function cargarRegistroModificarPorId(id) {
  fetch("/votosOficio/obtener_datos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id })
  })
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      alert(data.error || "No se pudo cargar el registro.");
      return;
    }

    pintarFormularioModificar(data);
  })
  .catch(err => alert("No se pudo cargar el registro seleccionado."));
}

function pintarFormularioModificar(data) {
  const form = document.getElementById("datosModificarForm");

  form.innerHTML = `
    <input type="hidden" id="mod-id" value="${data.id}" />
    <input type="hidden" id="mod-sexo" value="${data.sexo}" />
    <input type="hidden" id="mod-numeroCuenta" value="${data.numeroCuenta}" />

    <label>Nombre Completo:</label>
    <input type="text" id="mod-nombre" value="${data.nombreCompleto || ''}" />
    <label>Plan de Estudios:</label>
    <input type="text" id="mod-planEstudios" value="${data.planEstudios || ''}" />
    <label>Especialización:</label>
    <input type="text" id="mod-especializacion" value="${data.especializacion || ''}" />
    <label>Tesina o Título:</label>
    <input type="text" id="mod-tituloTesina" value="${data.tituloTesina || ''}" />
    <label>Tutor:</label>
    <input type="text" id="mod-tutor" value="${data.tutor || ''}" />
    <select id="mod-sexoTutor">
      <option value="">Seleccionar</option>
      <option value="M" ${data.sexoTutor === 'M' ? 'selected' : ''}>Masculino</option>
      <option value="F" ${data.sexoTutor === 'F' ? 'selected' : ''}>Femenino</option>
    </select>
    <label>Presidente:</label>
    <input type="text" id="mod-presidente" value="${data.presidente || ''}" />
    <label>Secretario:</label>
    <input type="text" id="mod-secretario" value="${data.secretario || ''}" />
    <label>Vocal 1:</label>
    <input type="text" id="mod-vocal1" value="${data.vocal1 || ''}" />
    <label>Vocal 2:</label>
    <input type="text" id="mod-vocal2" value="${data.vocal2 || ''}" />
    <label>Vocal 3:</label>
    <input type="text" id="mod-vocal3" value="${data.vocal3 || ''}" />
    <label>Modalidad:</label>
    <input type="text" id="mod-modalidad" value="${data.modalidad || ''}" />
  `;
}