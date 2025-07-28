// Получение данных и отображение таблицы
async function fetchAndDisplayData() {
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`Ошибка при получении данных: ${response.status}`);
        }
        const data = await response.json();

        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = ""; // Очистка перед вставкой

        data.forEach(item => {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${item.id}</td>
        <td>${item.well_id}</td>
        <td>
            <select class="status-select" data-id="${item.id}">
                <option value="открыт" ${item.status === 'открыт' ? 'selected' : ''}>открыт</option>
                <option value="закрыт" ${item.status === 'закрыт' ? 'selected' : ''}>закрыт</option>
                <option value="без простоя" ${item.status === 'без простоя' ? 'selected' : ''}>без простоя</option>
            </select>
        </td>
        <td>${item.contractor_gis}</td>
        <td>${formatDate(item.message_time)}</td>
        <td>${formatDate(item.downtime_start)}</td>
        <td>${formatDate(item.downtime_end)}</td>
        <td>${item.downtime_duration !== null ? item.downtime_duration.toFixed(2) : ""}</td>
        <td>${item.downtime_reason || ""}</td>
        <td><input type="text" class="work-goal-input" data-id="${item.id}" value="${item.work_goal || ''}"></td>
        <td><input type="text" class="contractor-opinion-input" data-id="${item.id}" value="${item.contractor_opinion || ''}"></td>
        <td><input type="text" class="meeting-result-input" data-id="${item.id}" value="${item.meeting_result || ''}"></td>
        ${item.image_pdf ? `<td><a href="${item.image_pdf}" target="_blank">Открыть PDF</a></td>` : `<td></td>`}
    `;
    tbody.appendChild(row);
});

        // Назначаем обработчики изменения для селектов и инпутов
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', handleUpdate);
        });
        document.querySelectorAll('.work-goal-input').forEach(input => {
            input.addEventListener('change', handleUpdate);
        });
        document.querySelectorAll('.contractor-opinion-input').forEach(input => {
            input.addEventListener('change', handleUpdate);
        });
        document.querySelectorAll('.meeting-result-input').forEach(input => {
            input.addEventListener('change', handleUpdate);
        });

        document.getElementById('loading').style.display = 'none';
        document.getElementById('repairs').style.display = 'table';

    } catch (error) {
        document.getElementById('loading').innerText = "Ошибка загрузки данных.";
        console.error(error);
    }
}

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