// logentry.js

document.addEventListener('DOMContentLoaded', function () {
  const placeSelect = document.getElementById('id_place');
  const institutionSelect = document.getElementById('id_institution');
  const dateInput = document.getElementById('id_date');
  const dayNumberSpan = document.getElementById('day-number');
  const maxDays = 25;

  // Validate and parse field start date
  let fieldStartDate;
  try {
    fieldStartDate = new Date(fieldStartDateStr);
    if (isNaN(fieldStartDate.getTime())) throw new Error("Invalid start date");
  } catch (e) {
    console.error("Failed to parse fieldStartDate:", e);
    fieldStartDate = new Date(); // fallback to today
  }

  // --- 1. Dynamic Institution Dropdown ---
  if (placeSelect && institutionSelect) {
    placeSelect.addEventListener('change', () => {
      const placeId = placeSelect.value;
      if (!placeId) {
        institutionSelect.innerHTML = '<option value="">Select Institution</option>';
        return;
      }

      fetch(`/logbook/ajax/get_institutions?place_id=${placeId}`)
        .then(response => response.json())
        .then(data => {
          institutionSelect.innerHTML = '<option value="">Select Institution</option>';
          data.forEach(inst => {
            const opt = document.createElement('option');
            opt.value = inst.id;
            opt.textContent = inst.name;
            institutionSelect.appendChild(opt);
          });
        })
        .catch(err => {
          console.error('Error fetching institutions:', err);
        });
    });
  }

  // --- 2. Working Days Calculation ---
  function countWorkingDays(start, end) {
    let count = 0;
    let cur = new Date(start);
    while (cur <= end) {
      const day = cur.getDay();
      if (day !== 0 && day !== 6) count++; // Exclude weekends
      cur.setDate(cur.getDate() + 1);
    }
    return count;
  }

  if (dateInput && dayNumberSpan) {
    dateInput.addEventListener('change', () => {
      const selectedDate = new Date(dateInput.value);
      if (selectedDate >= fieldStartDate) {
        const workingDays = countWorkingDays(fieldStartDate, selectedDate);
        dayNumberSpan.textContent = workingDays <= maxDays ? workingDays : maxDays;
      } else {
        dayNumberSpan.textContent = '1';
      }
    });
  }

  // --- 3. Departure Time Display ---
  const showDepartureBtn = document.getElementById('show-departure-btn');
  const departureTimeDiv = document.getElementById('departure-time');
  const departureTimeText = document.getElementById('departure-time-text');
  const departureTimeInput = document.getElementById('id_departure_time');

  if (showDepartureBtn && departureTimeDiv && departureTimeText && departureTimeInput) {
    showDepartureBtn.addEventListener('click', () => {
      const now = new Date();
      const timeStr = now.toTimeString().slice(0, 5); // HH:MM format
      departureTimeText.textContent = timeStr;
      departureTimeInput.value = timeStr;
      departureTimeDiv.style.display = 'block';
    });
  }
});
