function toggleFilterPanel() {
        const panel = document.getElementById("filter-panel");
        panel.style.display = panel.style.display === "none" ? "block" : "none";
    }

function switchView(view, button) {
    const isTable = view === 'table';

    document.getElementById('table-view').style.display = isTable ? 'block' : 'none';
    document.getElementById('card-view').style.display = isTable ? 'none' : 'flex';

    document.getElementById('table-toolbar-right').style.display = isTable ? 'flex' : 'none';
    document.getElementById('card-toolbar-right').style.display = isTable ? 'none' : 'flex';

    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    if (button) button.classList.add('active');
}


function filterPatients() {
    const tableInput = document.getElementById("searchInput");
    const cardInput = document.getElementById("searchCardInput");

    const input = (tableInput?.value || cardInput?.value || "").toUpperCase();

    // Таблица
    const tableRows = document.querySelectorAll("#patientTable tbody tr");
    tableRows.forEach(row => {
        const cells = row.querySelectorAll("td");
        const match = Array.from(cells).some(cell =>
            cell.textContent.toUpperCase().includes(input)
        );
        row.style.display = match ? "" : "none";
    });

    // Карточки
    const cards = document.querySelectorAll(".patient-card");
    cards.forEach(card => {
        const text = card.innerText.toUpperCase();
        card.style.display = text.includes(input) ? "" : "none";
    });
}

function goToPatientCabinet(patientId) {
    window.location.href = `/patients/${patientId}/`;
}


let currentSortColumn = null;
let currentSortDirection = 'asc';

function sortTable(thElement) {
    const columnIndex = parseInt(thElement.getAttribute("data-col"));
    const table = document.getElementById("patientTable");
    const rows = Array.from(table.rows).slice(1); // exclude header
    const isSameColumn = currentSortColumn === columnIndex;
    currentSortDirection = isSameColumn && currentSortDirection === 'asc' ? 'desc' : 'asc';
    currentSortColumn = columnIndex;

    rows.sort((a, b) => {
        let aText = a.cells[columnIndex].innerText.trim();
        let bText = b.cells[columnIndex].innerText.trim();

        if (!isNaN(parseFloat(aText)) && !isNaN(parseFloat(bText))) {
            aText = parseFloat(aText);
            bText = parseFloat(bText);
        }

        if (aText < bText) return currentSortDirection === 'asc' ? -1 : 1;
        if (aText > bText) return currentSortDirection === 'asc' ? 1 : -1;
        return 0;
    });

    rows.forEach(row => table.tBodies[0].appendChild(row));
    updateSortIndicators(columnIndex);
}



function toggleColumnMenu() {
    const menu = document.getElementById("columnMenu");
    menu.style.display = (menu.style.display === "none") ? "block" : "none";
}

function toggleColumn(colIndex) {
    const table = document.getElementById("patientTable");
    const rows = table.rows;
    for (let i = 0; i < rows.length; i++) {
        const cell = rows[i].cells[colIndex];
        if (cell) {
            cell.style.display = (cell.style.display === "none") ? "" : "none";
        }
    }
}
function toggleAllRows(master) {
    const checkboxes = document.querySelectorAll(".row-checkbox");
    checkboxes.forEach(cb => cb.checked = master.checked);
    updateBatchPanel();
}

function updateBatchPanel() {
    const selected = document.querySelectorAll(".row-checkbox:checked").length;
    const panel = document.getElementById("batch-panel");
    const counter = document.getElementById("selected-count");

    if (selected >= 1) {
        panel.style.display = "flex";
        counter.textContent = `${selected} выбрано`;
    } else {
        panel.style.display = "none";
    }
}

function batchDelete() {
    const selectedCheckboxes = document.querySelectorAll(".row-checkbox:checked");
    const ids = Array.from(document.querySelectorAll(".row-checkbox:checked"))
        .map(cb => cb.closest("tr").dataset.id)
        .filter(id => id && /^\d+$/.test(id))  
        .map(id => parseInt(id));


    if (ids.length === 0) {
        alert("Выберите хотя бы одного пациента.");
        return;
    }

    if (!confirm("Вы уверены, что хотите удалить выбранных пациентов?")) return;

    fetch("/delete-patients/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie('csrftoken')
        },
        body: JSON.stringify({ ids: ids })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // перезагружаем список
        } else {
            alert("Ошибка при удалении: " + data.error);
        }
    })
    .catch(error => {
        alert("Произошла ошибка при удалении.");
        console.error(error);
    });
}

// Получить CSRF токен из cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// static/JavaScript/patient.js

function getSelectedPatientIds() {
    const checkboxes = document.querySelectorAll(".row-checkbox:checked");
    const ids = Array.from(checkboxes).map(cb => cb.closest("tr").dataset.id);
    return ids;
}

function updateBatchPanel() {
    const count = getSelectedPatientIds().length;
    const panel = document.getElementById("batch-panel");
    const countSpan = document.getElementById("selected-count");
    countSpan.textContent = `${count} выбрано`;
    panel.style.display = count > 0 ? "flex" : "none";
}

function toggleAllRows(masterCheckbox) {
    const checkboxes = document.querySelectorAll(".row-checkbox");
    checkboxes.forEach(cb => cb.checked = masterCheckbox.checked);
    updateBatchPanel();
}

function batchDelete() {
    const ids = getSelectedPatientIds();
    if (ids.length === 0) return;

    if (!confirm("Вы уверены, что хотите удалить выбранных пациентов?")) return;

    fetch("/patients/delete-selected/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ ids: ids })
    })
    .then(response => {
        if (!response.ok) throw new Error("Ошибка удаления");
        return response.json();
    })
    .then(data => {
        if (data.success) {
            ids.forEach(id => {
                const row = document.querySelector(`tr[data-id='${id}']`);
                if (row) row.remove();
            });
            updateBatchPanel();
        }
    })
    .catch(err => alert(err.message));
}

function getCSRFToken() {
    const cookieValue = document.cookie.match('(^|;)\s*csrftoken\s*=\s*([^;]+)');
    return cookieValue ? cookieValue.pop() : '';
}

function updateSortIndicators(columnIndex) {
    const headers = document.querySelectorAll('th.sortable');
    headers.forEach((th) => {
        const thCol = parseInt(th.getAttribute('data-col'));
        th.classList.remove('sort-asc', 'sort-desc');
        if (thCol === columnIndex) {
            th.classList.add(currentSortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
        }
    });
}




