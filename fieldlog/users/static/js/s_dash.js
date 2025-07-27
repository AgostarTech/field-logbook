// Cache DOM elements once
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const helpModal = document.getElementById('helpModal');

// Toggle sidebar visibility and manage aria-expanded attribute
sidebarToggle.addEventListener('click', () => {
  sidebar.classList.toggle('active');
  sidebarToggle.classList.toggle('active');
  sidebarOverlay.classList.toggle('active');

  const expanded = sidebarToggle.getAttribute('aria-expanded') === 'true';
  sidebarToggle.setAttribute('aria-expanded', String(!expanded));
});

// Close sidebar when clicking outside (overlay)
sidebarOverlay.addEventListener('click', () => {
  sidebar.classList.remove('active');
  sidebarToggle.classList.remove('active');
  sidebarOverlay.classList.remove('active');
  sidebarToggle.setAttribute('aria-expanded', 'false');
});

// Submenu toggle with smooth max-height animation and arrow rotation
function toggleSubMenu(submenuId) {
  const submenu = document.getElementById(submenuId);
  if (!submenu) return;

  const parent = submenu.parentElement;
  parent.classList.toggle('active');

  if (submenu.style.maxHeight) {
    submenu.style.maxHeight = null;
  } else {
    submenu.style.maxHeight = `${submenu.scrollHeight}px`;
  }
}

// Show help modal
function showHelpModal() {
  if (!helpModal) return;
  helpModal.style.display = 'block';
  // You can add focus trap here for accessibility if desired
}

// Close help modal
function closeHelpModal() {
  if (!helpModal) return;
  helpModal.style.display = 'none';
}

// Close modal when clicking outside the content
window.addEventListener('click', (e) => {
  if (e.target === helpModal) closeHelpModal();
});

// Close modal on ESC key press
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && helpModal.style.display === 'block') {
    closeHelpModal();
  }
});
