const form = document.querySelector("form");

form.addEventListener("click", e=>{
    if (e.target.tagName.toLowerCase() === "i") {
        const input = e.target.parentElement.querySelector("input");
        const type = input.getAttribute("type") === "password" ? "text" : "password";
        input.setAttribute("type", type);
        e.target.classList.toggle("bi-eye");
        e.target.classList.toggle("bi-eye-slash");
    }
})

// sidebar.addEventListener("click", (e) => {
//     setTimeout(() => {e.preventDefault()}, 1000);
//   if (e.target.tagName.toLowerCase() === "a") {
//     currActive.classList.remove("active");
//     e.target.classList.add("active");
//     currActive = e.target;
//   }
// });
// console.log(currActive);
