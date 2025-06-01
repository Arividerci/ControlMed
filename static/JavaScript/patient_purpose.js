function markChanged(el) {
        const row = el.closest('tr');
        const saveBtn = row.querySelector('button.save-button');
        saveBtn.disabled = false;
    }

    function addMedicationSelect(button) {
        const wrapper = button.closest('.medications-wrapper');
        const select = document.createElement('select');
        select.className = 'form-select medication-select';
        select.innerHTML = document.getElementById('medication-options-template').innerHTML;
        select.onchange = () => markChanged(select);

        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.textContent = '❌';
        deleteBtn.onclick = function () {
            wrapper.removeChild(div);
            markChanged(deleteBtn);
        };

        const div = document.createElement('div');
        div.className = 'medication-select-wrapper';
        div.appendChild(select);
        div.appendChild(deleteBtn);

        wrapper.insertBefore(div, button);
    }

    function addProcedureSelect(button) {
        const wrapper = button.closest('.procedures-wrapper');
        const select = document.createElement('select');
        select.className = 'form-select procedure-select';
        select.innerHTML = document.getElementById('procedure-options-template').innerHTML;
        select.onchange = () => markChanged(select);

        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.textContent = '❌';
        deleteBtn.onclick = function () {
            wrapper.removeChild(div);
            markChanged(deleteBtn);
        };

        const div = document.createElement('div');
        div.className = 'procedure-select-wrapper';
        div.appendChild(select);
        div.appendChild(deleteBtn);

        wrapper.insertBefore(div, button);
    }


    function addRow() {
        const tbody = document.getElementById("purposesTable").querySelector("tbody");
        const row = document.createElement("tr");

        const medOptions = document.getElementById("medication-options-template").innerHTML;
        const procOptions = document.getElementById("procedure-options-template").innerHTML;

        row.innerHTML = `
            <td><input type="date" value="${new Date().toISOString().split('T')[0]}" onchange="markChanged(this)" /></td>
            <td><input type="number" value="1" onchange="markChanged(this)" /></td>
            <td><input type="text" value="" onchange="markChanged(this)" /></td>
            <td>
                <div class="medications-wrapper inline-selects">
                    <!-- Без начальных select -->
                    <button type="button" onclick="addMedicationSelect(this)">➕</button>
                </div>
            </td>
            <td>
                <div class="procedures-wrapper inline-selects">
                    <!-- Без начальных select -->
                    <button type="button" onclick="addProcedureSelect(this)">➕</button>
                </div>
            </td>
            <td>
                <select class="form-select" onchange="markChanged(this)">
                    <option>Активный</option>
                    <option>Завершено</option>
                    <option>Приостановлено</option>
                </select>
            </td>
            <td>
                <button class="save-button" onclick="saveRow(this)">Сохранить</button>
                <button class="save-button" style="background-color:#dc3545" onclick="deleteRow(this)">Удалить</button>
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

        fetch("{% url 'save_purpose_row' patient.patient_id %}", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": "{{ csrf_token }}"
            },
            body: JSON.stringify(data)
        }).then(res => res.json()).then(resp => {
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
        row.remove(); // если новая строка, просто удаляем
        return;
    }

    if (!confirm("Вы уверены, что хотите удалить это назначение?")) return;

    fetch(`/patients/{{ patient.patient_id }}/purpose/delete/${purposeId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}"
        }
    }).then(res => res.json()).then(resp => {
        if (resp.success) {
            row.remove();
        } else {
            alert("Ошибка при удалении: " + resp.error);
        }
    });
}