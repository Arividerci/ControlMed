
function addMedicationSelect(button) {
    const wrapper = button.closest('.medications-wrapper');

    const select = document.createElement('select');
    select.className = 'form-select medication-select';
    select.innerHTML = document.getElementById('medication-options-template').innerHTML;
    select.onchange = () => markChanged(select);

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.innerText = '✖';
    removeBtn.style.marginLeft = '4px';
    removeBtn.style.backgroundColor = '#dc3545';
    removeBtn.style.color = 'white';
    removeBtn.style.border = 'none';
    removeBtn.style.borderRadius = '4px';
    removeBtn.style.padding = '4px 8px';
    removeBtn.style.cursor = 'pointer';
    removeBtn.onclick = () => removeMedicationSelect(removeBtn);

    const div = document.createElement('div');
    div.className = 'medication-select-wrapper';
    div.style.display = 'flex';
    div.style.alignItems = 'center';
    div.style.gap = '6px';

    div.appendChild(select);
    div.appendChild(removeBtn);

    wrapper.insertBefore(div, button);
    markChanged(button);
}

function addProcedureSelect(button) {
    const wrapper = button.closest('.procedures-wrapper');

    const select = document.createElement('select');
    select.className = 'form-select procedure-select';
    select.innerHTML = document.getElementById('procedure-options-template').innerHTML;
    select.onchange = () => markChanged(select);

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.innerText = '✖';
    removeBtn.style.marginLeft = '4px';
    removeBtn.style.backgroundColor = '#dc3545';
    removeBtn.style.color = 'white';
    removeBtn.style.border = 'none';
    removeBtn.style.borderRadius = '4px';
    removeBtn.style.padding = '4px 8px';
    removeBtn.style.cursor = 'pointer';
    removeBtn.onclick = () => removeProcedureSelect(removeBtn);

    const div = document.createElement('div');
    div.className = 'procedure-select-wrapper';
    div.style.display = 'flex';
    div.style.alignItems = 'center';
    div.style.gap = '6px';

    div.appendChild(select);
    div.appendChild(removeBtn);

    wrapper.insertBefore(div, button);
    markChanged(button);
}

function addRow() {
    const tbody = document.getElementById("purposesTable").querySelector("tbody");
    const medOptions = document.getElementById("medication-options-template").innerHTML;
    const procOptions = document.getElementById("procedure-options-template").innerHTML;

    const row = document.createElement("tr");
    row.innerHTML = `
        <td><input type="date" value="${new Date().toISOString().split('T')[0]}" onchange="markChanged(this)" /></td>
        <td><input type="number" value="1" onchange="markChanged(this)" /></td>
        <td><input type="text" value="" onchange="markChanged(this)" /></td>
        <td>
            <div class="medications-wrapper inline-selects">
                <div class="medication-select-wrapper">
                    <select class="form-select medication-select" onchange="markChanged(this)">${medOptions}</select>
                </div>
                <button type="button" class="add-button" onclick="addMedicationSelect(this)">+</button>
            </div>
        </td>
        <td>
            <div class="procedures-wrapper inline-selects">
                <div class="procedure-select-wrapper">
                    <select class="form-select procedure-select" onchange="markChanged(this)">${procOptions}</select>
                </div>
                <button type="button" class="add-button" onclick="addProcedureSelect(this)">+</button>
            </div>
        </td>
        <td>
            <select class="form-select" onchange="markChanged(this)">
                <option selected>Активный</option>
                <option>Завершено</option>
                <option>Приостановлено</option>
            </select>
        </td>
        <td class="but-sd">
            <button class="save-button" onclick="saveRow(this)">Сохранить</button>
            <button class="delete-button" onclick="deleteRow(this)">Удалить</button>
        </td>
    `;
    tbody.appendChild(row);
}

function saveRow(button) {
    const row = button.closest("tr");
    const cells = row.querySelectorAll("td");

    const selectedMedications = Array.from(
        row.querySelectorAll('.medication-select')
    ).map(select => parseInt(select.value));

    const selectedProcedures = Array.from(
        row.querySelectorAll('.procedure-select')
    ).map(select => parseInt(select.value));

    const data = {
        startdate: cells[0].querySelector("input").value,
        duration: cells[1].querySelector("input").value,
        diagnosis: cells[2].querySelector("input").value,
        medications: selectedMedications,
        procedures: selectedProcedures,
        status: cells[5].querySelector("select").value,
        id: row.dataset.id || null
    };

    fetch(savePurposeUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(resp => {
        if (resp.success) {
            button.disabled = true;
            if (!row.dataset.id) {
                row.dataset.id = resp.id;
            }
            alert("Сохранено");
        } else {
            alert("Ошибка при сохранении: " + resp.error);
        }
    });
}

function deleteRow(button) {
    const row = button.closest("tr");
    const purposeId = row.dataset.id;

    if (!purposeId) {
        row.remove();
        return;
    }

    if (!confirm("Вы уверены, что хотите удалить это назначение?")) return;

    fetch(`${deletePurposeUrlBase}${purposeId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken
        }
    })
    .then(res => res.json())
    .then(resp => {
        if (resp.success) {
            row.remove();
        } else {
            alert("Ошибка при удалении: " + resp.error);
        }
    });
}

function removeMedicationSelect(button) {
    const wrapper = button.closest('.medication-select-wrapper');
    wrapper.remove();
    markChanged(button);
}

function removeProcedureSelect(button) {
    const wrapper = button.closest('.procedure-select-wrapper');
    wrapper.remove();
    markChanged(button);
}

function markChanged(el) {
    const row = el.closest('tr');
    const saveBtn = row.querySelector('.save-button');
    if (saveBtn) {
        saveBtn.disabled = false;
    }
}
