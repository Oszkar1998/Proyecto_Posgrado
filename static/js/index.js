
function togglePassword() {
    const passwordInput = document.getElementById("password");
    const eyeIcon = document.getElementById("eye-icon");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.className = "fa-solid fa-eye-slash";
    } else {
        passwordInput.type = "password";
        eyeIcon.className = "fa-solid fa-eye";
    }
}