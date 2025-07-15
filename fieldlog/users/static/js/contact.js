document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll('.contact-card');
  cards.forEach((card, index) => {
    card.style.animation = `fadeInUp 0.6s ease ${index * 0.3}s forwards`;
  });
});
