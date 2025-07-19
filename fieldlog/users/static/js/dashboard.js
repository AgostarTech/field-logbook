// Wait for DOM
document.addEventListener('DOMContentLoaded', () => {

  // Modal helpers
  const uploadBtn = document.getElementById('uploadFileBtn');
  const uploadModal = document.getElementById('uploadFileModal');
  const uploadCancel = document.getElementById('uploadFileCancel');

  const assignBtn = document.getElementById('assignTaskBtn');
  const assignModal = document.getElementById('assignTaskModal');
  const assignCancel = document.getElementById('assignTaskCancel');

  function openModal(modal) {
    modal.hidden = false;
    modal.querySelector('input, textarea, select, button').focus();
  }
  function closeModal(modal) {
    modal.hidden = true;
  }

  uploadBtn.addEventListener('click', () => openModal(uploadModal));
  uploadCancel.addEventListener('click', () => closeModal(uploadModal));

  assignBtn.addEventListener('click', () => openModal(assignModal));
  assignCancel.addEventListener('click', () => closeModal(assignModal));

  window.addEventListener('click', e => {
    if (e.target === uploadModal) closeModal(uploadModal);
    if (e.target === assignModal) closeModal(assignModal);
  });

  // Approve/Reject buttons with SweetAlert2 confirmation
  document.querySelectorAll('.btn-approve, .btn-reject').forEach(button => {
    button.addEventListener('click', e => {
      e.preventDefault();
      const btn = e.currentTarget;
      const logId = btn.dataset.logId;
      const action = btn.classList.contains('btn-approve') ? 'approve' : 'reject';
      const actionText = action.charAt(0).toUpperCase() + action.slice(1);

      Swal.fire({
        title: `${actionText} this log?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: actionText,
        cancelButtonText: 'Cancel'
      }).then((result) => {
        if (result.isConfirmed) {
          btn.disabled = true;
          btn.classList.add('btn-disabled');
          // TODO: AJAX request here to update log status
          Swal.fire(`${actionText}d!`, `The log has been ${action}d.`, 'success');
          // Optional: remove or update row in table after successful AJAX
        }
      });
    });
  });

  // Search Filter
  const searchInput = document.getElementById('searchInput');
  const filterType = document.getElementById('filterType');

  function filterTable(tableId) {
    const filterText = searchInput.value.toLowerCase();
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);

    rows.forEach(row => {
      const textContent = row.textContent.toLowerCase();
      row.style.display = textContent.includes(filterText) ? '' : 'none';
    });
  }

  function searchFilter() {
    const type = filterType.value;
    const filterText = searchInput.value.toLowerCase();

    if (type === 'students' || type === 'all') {
      document.getElementById('studentsTable').style.display = '';
      filterTable('studentsTable');
    } else {
      document.getElementById('studentsTable').style.display = 'none
