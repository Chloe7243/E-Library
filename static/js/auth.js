const form = document.querySelector("form");

// toggling pssword visibility
form.addEventListener("click", e=>{
    if (e.target.tagName.toLowerCase() === "i") {
        const input = e.target.parentElement.querySelector("input");
        const type = input.getAttribute("type") === "password" ? "text" : "password";
        input.setAttribute("type", type);
        e.target.classList.toggle("bi-eye");
        e.target.classList.toggle("bi-eye-slash");
    }
})
