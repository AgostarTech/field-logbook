// oncampus.js

function filterStudents() {
  const input = document.getElementById("studentSearch");
  const filter = input.value.toLowerCase();
  const table = document.getElementById("studentTable");
  const tr = table.getElementsByTagName("tr");

  for (let i = 1; i < tr.length; i++) {
    const tdName = tr[i].getElementsByTagName("td")[0];
    const tdReg = tr[i].getElementsByTagName("td")[1];
    if (tdName && tdReg) {
      const name = tdName.textContent || tdName.innerText;
      const reg = tdReg.textContent || tdReg.innerText;
      tr[i].style.display =
        name.toLowerCase().includes(filter) || reg.toLowerCase().includes(filter)
          ? ""
          : "none";
    }
  }
}
