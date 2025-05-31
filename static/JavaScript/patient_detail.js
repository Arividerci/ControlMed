document.addEventListener('DOMContentLoaded', () => {
    // --------- patient form (основные данные) ---------
    const form = document.getElementById('patientForm');
    const saveButton = document.getElementById('saveButton');

    if (form && saveButton) {
        const originalValues = Array.from(form.elements).map(e => e.value);

        form.addEventListener('input', () => {
            const changed = Array.from(form.elements).some((e, i) => e.value !== originalValues[i]);
            saveButton.disabled = !changed;
        });

        const photoInput = document.getElementById('photoInput');
        if (photoInput) {
            photoInput.addEventListener('change', () => {
                saveButton.disabled = false;
            });
        }
    }

    // --------- hospitalization form (госпитализация) ---------
    const hospForm = document.getElementById('hospitalizationForm');
    const hospSaveBtn = document.getElementById('hospitalizationSaveBtn');

    if (hospForm && hospSaveBtn) {
        const fields = Array.from(hospForm.elements).filter(el => el.name && el.type !== 'hidden');
        const initialValues = fields.map(el => el.dataset.original ?? '');

        const isFormEmpty = initialValues.every(val => val === '');

        const updateSaveButton = () => {
            const changed = fields.some((el, i) => el.value !== initialValues[i]);
            hospSaveBtn.disabled = !changed;
        };

        if (isFormEmpty) {
            hospSaveBtn.disabled = false; // можно сразу вводить и сохранять
        } else {
            hospSaveBtn.disabled = true;
            hospForm.addEventListener('input', updateSaveButton);
        }
    }
});




function togglePhotoMenu(event) {
    event.stopPropagation(); 
    const menu = document.getElementById('photoMenu');
    menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
}

document.addEventListener('click', function (e) {
    const menu = document.getElementById('photoMenu');
    const wrapper = document.querySelector('.photo-wrapper');
    if (!wrapper.contains(e.target) && !menu.contains(e.target)) {
        menu.style.display = 'none';
    }
});



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function removePhoto(patientId) {
    if (confirm("Удалить фотографию пациента?")) {
        fetch(`/patients/remove-photo/${patientId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Обновим страницу — покажет фото по умолчанию
            } else {
                alert("Ошибка при удалении фото: " + data.error);
            }
        });
    }
}
function confirmDelete() {
    if (confirm("Вы точно хотите удалить пациента?")) {
        fetch(`/patients/delete/${PATIENT_ID}/`, {
            method: "POST",
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        }).then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = "/patients";
            } else {
                alert("Ошибка при удалении пациента");
            }
        });
    }
}

function switchSection(section) {
    document.querySelectorAll('.patient-section').forEach(s => s.style.display = 'none');
    document.querySelector(`#section-${section}`).style.display = 'block';

    document.querySelectorAll('.patient-sidebar-item').forEach(item => item.classList.remove('active'));
    document.querySelector(`#btn-${section}`).classList.add('active');

    const url = new URL(window.location);
    url.searchParams.set('tab', section);
    window.history.replaceState({}, '', url);
}