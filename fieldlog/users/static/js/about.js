document.addEventListener("DOMContentLoaded", () => {
  const listItems = document.querySelectorAll(".team-list li, .expertise-list li");

  listItems.forEach((li, index) => {
    li.style.opacity = 0;
    setTimeout(() => {
      li.style.transition = "opacity 0.6s ease";
      li.style.opacity = 1;
    }, 300 * index);
  });

  const footer = document.querySelector(".about-footer");
  footer.style.opacity = 0;
  setTimeout(() => {
    footer.style.transition = "opacity 1s ease";
    footer.style.opacity = 1;
  }, 2000);
});
