const nav = document.querySelector(".navigation");

// displaying the contents based on which link is clicked
nav.addEventListener("click", (e) => {
  console.log(e.target);
  if (e.target.tagName.toLowerCase() === "a") {
    e.preventDefault();
    document
      .querySelector(e.target.getAttribute("href"))
      .classList.remove("inactive-content");
    console.log(document.querySelector(e.target.getAttribute("href")));

    nav.querySelectorAll("li").forEach((el) => {
      if (el.classList.contains("active")) {
        console.log(
          document.querySelector(el.querySelector("a").getAttribute("href"))
        );
        if (el != e.target.parentElement) {
          document
            .querySelector(el.querySelector("a").getAttribute("href"))
            .classList.add("inactive-content");
          el.classList.remove("active");
        }
      }
    });

    e.target.parentElement.classList.add("active");
  }
});

