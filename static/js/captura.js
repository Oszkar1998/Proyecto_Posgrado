
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

// Cerrar al dar click fuera (para ambos modales)
document.addEventListener("click", function(e){
  const mv = document.getElementById("modal-menu-votos");
  if (mv && mv.style.display === "flex" && e.target === mv) cerrarMenuVotos();

  const mc = document.getElementById("modal-menu-candidatura");
  if (mc && mc.style.display === "flex" && e.target === mc) cerrarMenuCandidatura();

  const ma = document.getElementById("modal-menu-actas");
  if (ma && ma.style.display === "flex" && e.target === ma) cerrarMenuActasGrado();
});


// ESC para cerrar ambos
document.addEventListener("keydown", function(e){
  if (e.key !== "Escape") return;
  cerrarMenuVotos();
  cerrarMenuCandidatura();
  cerrarMenuActasGrado();
});

function mostrarMenuActasGrado(){
  const m = document.getElementById("modal-menu-actas");
  if (m) m.style.display = "flex";
}

function cerrarMenuActasGrado(){
  const m = document.getElementById("modal-menu-actas");
  if (m) m.style.display = "none";
}

function abrirActasGrado(accion){
  // Mandamos a actasGrado y le decimos qué abrir
  window.location.href = `/actasGrado/?open=${encodeURIComponent(accion)}`;
}
