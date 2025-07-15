document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".ripple-container");

  buttons.forEach(button => {
    button.addEventListener("click", function (e) {
      const ripple = document.createElement("span");
      ripple.classList.add("ripple");

      const rect = button.getBoundingClientRect();
      ripple.style.left = `${e.clientX - rect.left}px`;
      ripple.style.top = `${e.clientY - rect.top}px`;

      button.appendChild(ripple);

      setTimeout(() => ripple.remove(), 600);
    });
  });
});
