// login.js

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('.login-form');

  // Optional: Add shake animation on invalid submit (for demo purpose)
  form.addEventListener('submit', (e) => {
    // Just a fake validation demo (replace with real validation or server error)
    const username = form.querySelector('input[name="username"]').value.trim();
    const password = form.querySelector('input[name="password"]').value.trim();

    if (!username || !password) {
      e.preventDefault();
      triggerShake(form);
    }
  });
});

function triggerShake(element) {
  element.classList.add('shake');
  setTimeout(() => element.classList.remove('shake'), 500);
}
