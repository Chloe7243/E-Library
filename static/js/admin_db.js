const sidebar = document.querySelector(".nav-pills");
let currActive = document.querySelector(".nav-pills").querySelector(".active");

console.log(currActive);
console.log(sidebar);

// sidebar.addEventListener("click", (e) => {
//     setTimeout(() => {e.preventDefault()}, 1000);
//   if (e.target.tagName.toLowerCase() === "a") {
//     currActive.classList.remove("active");
//     e.target.classList.add("active");
//     currActive = e.target;
//   }
// });
// console.log(currActive);
