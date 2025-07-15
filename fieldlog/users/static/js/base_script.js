// Toggle navigation menu
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');

  toggleBtn.addEventListener('click', () => {
    navMenu.classList.toggle('show');
  });
});
