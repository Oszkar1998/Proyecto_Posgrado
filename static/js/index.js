
function togglePassword() {
    const passwordInput = document.getElementById("password");
    const eyeIcon = document.getElementById("eye-icon");
    const boton = eyeIcon ? eyeIcon.closest("button") : null;

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.className = "fa-solid fa-eye-slash";
        if (boton) { boton.setAttribute("aria-label", "Ocultar contraseña"); boton.setAttribute("aria-pressed", "true"); }
    } else {
        passwordInput.type = "password";
        eyeIcon.className = "fa-solid fa-eye";
        if (boton) { boton.setAttribute("aria-label", "Mostrar contraseña"); boton.setAttribute("aria-pressed", "false"); }
    }
}