// Sidebar toggle button
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');

sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('active');
    sidebarToggle.classList.toggle('active');
    sidebarOverlay.classList.toggle('active');
});

// Clicking outside sidebar closes it
sidebarOverlay.addEventListener('click', () => {
    sidebar.classList.remove('active');
    sidebarToggle.classList.remove('active');
    sidebarOverlay.classList.remove('active');
});

// Submenu toggle with arrow rotation
function toggleSubMenu(id) {
    const submenuParent = document.getElementById(id).parentElement;
    submenuParent.classList.toggle('active');

    const submenu = document.getElementById(id);
    if (submenu.style.maxHeight) {
        submenu.style.maxHeight = null;
    } else {
        submenu.style.maxHeight = submenu.scrollHeight + "px";
    }
}

// Help modal logic
const helpModal = document.getElementById('helpModal');

function showHelpModal() {
    helpModal.style.display = "block";
}

function closeHelpModal() {
    helpModal.style.display = "none";
}

// Close modal when clicking outside content
window.onclick = function (event) {
    if (event.target === helpModal) {
        closeHelpModal();
    }
};
