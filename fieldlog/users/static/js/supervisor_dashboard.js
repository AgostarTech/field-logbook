document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("studentSearch");
    const tableBody = document.getElementById("studentBody");
    const taskModal = document.getElementById("taskModal");
    const modalStudentId = document.getElementById("modalStudentId");
    const closeModalBtn = document.getElementById("closeModal");
    const assignButtons = document.querySelectorAll(".assign-btn");
    const taskForm = document.getElementById("taskForm");

    // Search filtering
    searchInput.addEventListener("keyup", () => {
        const keyword = searchInput.value.toLowerCase();
        const rows = tableBody.getElementsByTagName("tr");
        for (const row of rows) {
            const name = row.cells[0].textContent.toLowerCase();
            const reg = row.cells[1].textContent.toLowerCase();
            row.style.display = (name.includes(keyword) || reg.includes(keyword)) ? "" : "none";
        }
    });

    // Attach click events to all assign buttons
    assignButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            openTaskModal(btn.dataset.student);
        });
    });

    // Close modal on clicking close button
    closeModalBtn.addEventListener("click", closeTaskModal);

    // Close modal on outside click
    window.addEventListener("click", e => {
        if (e.target === taskModal) {
            closeTaskModal();
        }
    });

    // Expose toggleTable and modal open/close functions globally (needed by inline onclick handlers)
    window.toggleTable = function (id) {
        const table = document.getElementById(id);
        table.style.display = (table.style.display === "none" || !table.style.display) ? "block" : "none";
    };

    window.openTaskModal = function (studentId) {
        modalStudentId.value = studentId;
        taskModal.style.display = "flex";
    };

    window.closeTaskModal = closeTaskModal;

    function closeTaskModal() {
        taskModal.style.display = "none";
        taskForm.reset();
    }
});
function openTaskModal(studentId) {
    document.getElementById("modalStudentId").value = studentId;
    const modal = document.getElementById("taskModal");
    modal.classList.add("show");
}

function closeTaskModal() {
    const modal = document.getElementById("taskModal");
    modal.classList.remove("show");
    document.getElementById("taskForm").reset();
}
