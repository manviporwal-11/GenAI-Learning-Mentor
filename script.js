function startLearning() {
    window.location.href = "login.html";
}

function feature(name) {
    const modal = document.getElementById("modal");
    const title = document.getElementById("modalTitle");
    const text = document.getElementById("modalText");

    title.textContent = name;
    text.textContent = "Explore this feature in your personalized learning journey.";

    modal.classList.add("active");
}

function closeModal() {
    document.getElementById("modal").classList.remove("active");
}
function loginUser(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (email && password) {
        window.location.href = "dashboard.html";
    }
}