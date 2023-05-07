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

function requestAccess(bookId) {
    fetch('books/' + bookId + '/request-access', { method: 'POST' })
        .then(function (response) {
            console.log(response)
            console.log(bookId)
            return response.text();
        })
        .then(function (data) {
            console.log(data)
            alert(data);
        })
        .catch(function (error) {
            console.error('Error:', error);
        });
}