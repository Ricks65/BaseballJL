function openLogin() {
    // Cambiamos a "loginModal" y usamos "flex" para que quede bien centrado
    document.getElementById("loginModal").style.display = "flex";
}

function closeLogin() {
    // Cerramos el contenedor principal
    document.getElementById("loginModal").style.display = "none";
}

function checkStaticLogin() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    
    if (username === "coach" && password === "1234") {
        alert("Welcome, Coach!");
        closeLogin();
        window.location.href = "/league/players/"; // Redirige a la lista de jugadores
    } else {
        alert("Invalid credentials. Please try again. Try username: coach, password: 1234");
    }
}