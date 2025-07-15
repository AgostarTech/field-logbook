// progress_report.js

document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('.week-form');

  forms.forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();

      // Simulate AJAX submission (replace this with actual AJAX if needed)
      const weekNumber = form.dataset.week;
      const textarea = form.querySelector('textarea');
      const submitBtn = form.querySelector('.submit-btn');

      if (!textarea.value.trim()) {
        showAlert('Please enter a comment before submitting.', 'warning');
        return;
      }

      // Disable form elements on submit
      textarea.setAttribute('readonly', 'readonly');
      submitBtn.setAttribute('disabled', 'disabled');
      submitBtn.textContent = 'Submitted';

      showAlert(`Week ${weekNumber} comment submitted successfully!`, 'success');

      // TODO: Implement actual form submission with AJAX or normal POST
      // form.submit(); // uncomment to perform real submission instead of simulated
    });
  });
});

// Function to show alert messages
function showAlert(message, type = 'info') {
  const alertContainer = document.getElementById('alert-container');

  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.role = 'alert';
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;

  alertContainer.appendChild(alertDiv);

  // Auto-remove alert after 3.5 seconds
  setTimeout(() => {
    alertDiv.classList.remove('show');
    alertDiv.classList.add('hide');
    alertDiv.addEventListener('transitionend', () => alertDiv.remove());
  }, 3500);
}
