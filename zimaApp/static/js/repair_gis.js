async function fetchAndDisplayData() {
    const loadingEl = document.getElementById('loading');
    const tableBody = document.getElementById('tableBody');
    const repairsTable = document.getElementById('repairs');

    if (loadingEl) {
        loadingEl.innerText = "Загрузка данных...";
        loadingEl.style.display = 'block';
    }
    if (repairsTable) {
        repairsTable.style.display = 'none';
    }

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error("Ошибка сети");
        const data = await response.json();

        // Очистка таблицы
        if (tableBody) tableBody.innerHTML = '';

        // Заполнение таблицы данными
        data.forEach(item => {
            const row = document.createElement('tr');
            // добавьте ячейки для каждого поля item
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.well_id}</td>
                <td>${item.status}</td>
                <td>${item.contractor_gis}</td>
                <td>${item.message_time}</td>
                <td>${item.start_time}</td>
                <td>${item.end_time}</td>
                <td>${item.duration_hours}</td>
                <td>${item.reason}</td>
                <td>${item.work_goal}</td>
                <td>${item.contractor_opinion}</td>
                <td>${item.meeting_result}</td>
                <td><a href="${item.pdf_url}" target="_blank">PDF</a></td>
            `;
            tableBody.appendChild(row);
        });

        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
        if (repairsTable) {
            repairsTable.style.display = 'table';
        }
    } catch (error) {
        if (loadingEl) {
            loadingEl.innerText = "Ошибка загрузки данных.";
        }
        console.error(error);
    }
}

// Вызов при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    fetchAndDisplayData();
});

// Обработчик изменения
async function handleUpdate(event) {
    const target = event.target;
    const id = target.dataset.id;

    let fieldName;
    let newValue;

    if (target.classList.contains('status-select')) {
        fieldName = 'status';
        newValue = target.value;
    } else if (target.classList.contains('work-goal-input')) {
        fieldName = 'work_goal';
        newValue = target.value;
    } else if (target.classList.contains('contractor-opinion-input')) {
        fieldName = 'contractor_opinion';
        newValue = target.value;
    } else if (target.classList.contains('meeting-result-input')) {
        fieldName = 'meeting_result';
        newValue = target.value;
    } else {
        return; // Неизвестный элемент
    }

    // Формируем объект обновления
    const updateData = {
        id: id,
        [fieldName]: newValue
    };

    try {
        const response = await fetch('/repair_gis/update', { // Укажите правильный маршрут
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });

        if (!response.ok) {
            throw new Error(`Ошибка при обновлении: ${response.status}`);
        }

        const result = await response.json();

        // Можно добавить уведомление об успешном обновлении или обработку ошибок
        console.log('Обновлено:', result);

    } catch (error) {
        alert("Ошибка при сохранении данных");
        console.error(error);
    }
}

function formatDate(dateString) {
    if (!dateString) return "";
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return ""; // Проверка на некорректную дату
    // Форматируем дату, например: "ДД.ММ.ГГГГ ЧЧ:ММ"
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${day}.${month}.${year} ${hours}:${minutes}`;
}