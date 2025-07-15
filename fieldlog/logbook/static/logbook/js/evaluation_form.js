document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('evaluationForm');
  const submitBtn = document.getElementById('submitBtn');

  form.addEventListener('submit', (e) => {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
  });
});
