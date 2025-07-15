// Ripple animation on submit button
document.addEventListener("DOMContentLoaded", function () {
  const button = document.querySelector("button[type='submit']");
  button.addEventListener("click", function (e) {
    const ripple = document.createElement("span");
    ripple.classList.add("ripple");
    ripple.style.left = `${e.offsetX}px`;
    ripple.style.top = `${e.offsetY}px`;
    this.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });

  // Input field glow on focus
  const inputs = document.querySelectorAll("input, select");
  inputs.forEach(input => {
    input.addEventListener("focus", () => input.classList.add("focused"));
    input.addEventListener("blur", () => input.classList.remove("focused"));
  });
});
