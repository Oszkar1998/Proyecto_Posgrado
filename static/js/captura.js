function mostrarMenuVotos(){
  const m = document.getElementById("modal-menu-votos");
  if (m) m.style.display = "flex";
}

function cerrarMenuVotos(){
  const m = document.getElementById("modal-menu-votos");
  if (m) m.style.display = "none";
}

function abrirVotos(accion){
  // Mandamos a votosOficio y le decimos qué abrir
  window.location.href = `/votosOficio/?open=${encodeURIComponent(accion)}`;
}

function mostrarMenuCandidatura(){
  const m = document.getElementById("modal-menu-candidatura");
  if (m) m.style.display = "flex";
}

function cerrarMenuCandidatura(){
  const m = document.getElementById("modal-menu-candidatura");
  if (m) m.style.display = "none";
}

function abrirCandidatura(accion){
  // Mandamos a candidatura y le decimos qué abrir
  window.location.href = `/candidatura/?open=${encodeURIComponent(accion)}`;
}

function mostrarMenuActasGrado(){
  const m = document.getElementById("modal-menu-actas-grado");
  if (m) m.style.display = "flex";
}

function cerrarMenuActasGrado(){
  const m = document.getElementById("modal-menu-actas-grado");
  if (m) m.style.display = "none";
}

function abrirActasGrado(accion){
  // Mandamos a actasGrado y le decimos qué abrir
  window.location.href = `/actasGrado/?open=${encodeURIComponent(accion)}`;
}

function mostrarMenuActasCandidatura(){
  const m = document.getElementById("modal-menu-actas-candidatura");
  if (m) m.style.display = "flex";
}

function cerrarMenuActasCandidatura(){
  const m = document.getElementById("modal-menu-actas-candidatura");
  if (m) m.style.display = "none";
}


function abrirActasCandidatura(accion){
  if (accion === "verActa") {
    window.location.href = `/actasCandidatura/`;
  } else {
    window.location.href = `/actasCandidatura/?open=${encodeURIComponent(accion)}`;
  }
}

// ESC, clic fuera y foco: modal.js
Modal.registrar("modal-menu-votos", cerrarMenuVotos);
Modal.registrar("modal-menu-candidatura", cerrarMenuCandidatura);
Modal.registrar("modal-menu-actas-grado", cerrarMenuActasGrado);
Modal.registrar("modal-menu-actas-candidatura", cerrarMenuActasCandidatura);
