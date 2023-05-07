const due = document.querySelector("table").querySelector("#days");
const input = document.querySelector("table").querySelector("#due_date");

input.setAttribute("value", due.value);

due.addEventListener("click", (e) => {
  input.setAttribute("value", due.value);
});
