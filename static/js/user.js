const nav = document.querySelector(".navigation");

nav.addEventListener("click", e => {
    console.log(e.target);
    if (e.target.tagName.toLowerCase() === "a") {
        nav.querySelectorAll("li").forEach(el => {
            if (el.classList.contains("active"))
                    el.classList.remove("active")
        })
        e.target.parentElement.classList.add("active");
    }
})