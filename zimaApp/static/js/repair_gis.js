document.addEventListener("DOMContentLoaded", () => {
    let allData = [];
    let filteredData = [];

    fetchAllData();

    // Инициализация фильтров
    document.querySelectorAll('.filter-select').forEach(select => {
        select.addEventListener('change', () => {
            applyFilters();
        });
    });

});// Функция для получения всех данных
async function fetchAllData() {
    try {
        const response = await fetch(`${apiBaseUrl}/all`);
        if (!response.ok) throw new Error('Ошибка загрузки данных');
        allData = await response.json();

        // После загрузки данных заполняем все фильтры
        populateFilters();
        filteredData = [...allData];
        renderTable(filteredData);
    } catch (e) {
        console.error(e);
        alert('Ошибка загрузки данных');
    }
}

function populateFilters() {
    document.querySelectorAll('.filter-select').forEach(select => {
        const column = select.dataset.column;
        const valuesSet = new Set();

        allData.forEach(item => {
            let value = item[column];

            // Если колонка с датой/временем
            if (column === 'Время сообщения' || column === 'Начало простоя' || column === 'Окончание простоя') {
                if (value) {
                    value = formatDateTime(value);
                }
            }

            if (value != null && value !== '') {
                valuesSet.add(value);
            }
        });

        const values = Array.from(valuesSet).sort();

        select.innerHTML = '<option value="">Все</option>';
        values.forEach(val => {
            const option = document.createElement('option');
            option.value = val;
            option.textContent = val;
            select.appendChild(option);
        });
    });
}

// Применение всех выбранных фильтров
function applyFilters() {
    const filters = {};
    document.querySelectorAll('.filter-select').forEach(select => {
        filters[select.dataset.column] = select.value;
    });

    filteredData = allData.filter(item => {
        return Object.entries(filters).every(([column, value]) => {
            if (!value) return true; // если значение "Все", пропускаем
            return item[column] == value;
        });
    });

    renderTable(filteredData);
}

function formatDateTime(dateStr) {

    const date = new Date(dateStr);
    if (isNaN(date)) return dateStr; // если не удалось распарсить, оставить как есть
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}.${month}.${day} ${hours}:${minutes}`;
}

function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    data.forEach(item => {
        // Форматируем даты для редактирования
        const messageInput = `<input type="datetime-local" value="${item.message_time ? new Date(item.message_time).toISOString().slice(0, 16) : ''}" onchange="updateField('${item.id}', 'message_time', this.value)">`;
        const downtimeStartInput = `<input type="datetime-local" value="${item.downtime_start ? new Date(item.downtime_start).toISOString().slice(0, 16) : ''}" onchange="updateField('${item.id}', 'downtime_start', this.value)">`;
        const downtimeEndInput = `<input type="datetime-local" value="${item.downtime_end ? new Date(item.downtime_end).toISOString().slice(0, 16) : ''}" onchange="updateField('${item.id}', 'downtime_end', this.value)">`;
        const downtimeDurationInput = `<input type="number" min="0" step="0.1" value="${item.downtime_duration || ''}" onchange="updateField('${item.id}', 'downtime_duration', this.value)">`;

        // Ограничение длины причины и подсказка
        const reasonText = item.downtime_reason || '';
        const shortReason = reasonText.length > 100 ? reasonText.slice(0, 100) + '...' : reasonText;

        // Создаем редактируемые поля для указанных колонок
        const workGoalInput = `<input type="text" value="${item.work_goal || ''}" onchange="updateField('${item.id}', 'work_goal', this.value)">`;
        const contractorOpinionInput = `
          <textarea rows="5" cols="40" onchange="updateField('${item.id}', 'contractor_opinion', this.value)">
            ${item.contractor_opinion || ''}
          </textarea>`;
        const meetingResultInput = `<input type="text" value="${item.meeting_result || ''}" onchange="updateField('${item.id}', 'meeting_result', this.value)">`;

        // HTML для файла или ссылки
        const fileLinkHtml = item.image_pdf
            ? `<a href="${item.image_pdf}" target="_blank">Открыть акт</a>
                 <button class="delete-file-btn" data-id="${item.id}">Удалить</button>`
            : `<input type="file" accept=".png,.jpeg,.jpg,.pdf" onchange="uploadFile('${item.id}', this.files)">`;

        // Подсказка для причины
        const reasonHtml = `
            <div class="tooltiptext">
                ${shortReason}
                <span class="tooltiptext">${reasonText}</span>
            </div>`;

        // Создаем строку таблицы
        const rowHtml = `
            <tr data-id="${item.id}">
                <td>${item.well_number || ''}</td>
                <td>${item.well_area || ''}</td>
                <td>
                    <select class="status-select" data-id="${item.id}">
                        <option value="открыт" ${item.status === 'открыт' ? 'selected' : ''}>открыт</option>
                        <option value="закрыт" ${item.status === 'закрыт' ? 'selected' : ''}>закрыт</option>
                        <option value="без простоя" ${item.status === 'без простоя' ? 'selected' : ''}>без простоя</option>
                    </select>
                </td>
                <td>${item.contractor_gis || ''}</td>                   

                <!-- Редактируемые поля -->
                <td>${messageInput}</td>
                <td>${downtimeStartInput}</td>
                <td>${downtimeEndInput}</td>
                <td>${downtimeDurationInput}</td>

                <!-- Причина с подсказкой -->
                <td>${reasonHtml}</td>

                <!-- Сделать редактируемыми -->
                <td>${workGoalInput}</td>
                <td>${contractorOpinionInput}</td>
                <td>${meetingResultInput}</td>

                <!-- Файл или ссылка -->
                <td class="file-link">${fileLinkHtml}</td>
            </tr>`;

        tbody.insertAdjacentHTML('beforeend', rowHtml);
    });

    // После вставки всех строк можно добавить обработчики для кнопок удаления файла
    document.querySelectorAll('.delete-file-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            deleteFile(id);
        });
    });
}


// Делегирование события клика по кнопкам "Удалить файл"
document.getElementById('tableBody').addEventListener('click', function (e) {
        if (e.target && e.target.classList.contains('delete-file-btn')) {
            const itemId = e.target.getAttribute('data-id');
            deleteFile(itemId);
        }
    }
)


async function deleteFile(itemId) {
    const token = localStorage.getItem('access_token');

    if (!confirm('Вы уверены, что хотите удалить файл?')) return;

    try {
        const response = await fetch('/files/delete_act_gis', {
            method: 'DELETE', // или 'DELETE', в зависимости от API
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({itemId})
        });

        const result = await response.json();

        if (response.ok) {
            // Обновляем таблицу: удаляем ссылку и кнопку
            const row = document.querySelector(`tr[data-id="${itemId}"]`);
            if (row) {
                const linkCell = row.querySelector('.file-link');
                linkCell.innerHTML = `
                    <input type="file" accept=".png,.jpeg,.jpg,.pdf" onchange="uploadFile('${itemId}', this.files)">
                `;
            }
        } else {
            alert('Ошибка: ' + result.message);
        }
    } catch (e) {
        console.error(e);
        alert('Ошибка при удалении файла');
    }
}

async function uploadFile(itemId, files) {
    if (!files || files.length === 0) return;
    const token = localStorage.getItem('access_token');
    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('itemId', itemId);

    try {
        const response = await fetch('/files/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData,
        });
        const result = await response.json();

        if (response.status === 200) {
            // Обновляем ссылку в таблице
            const row = document.querySelector(`tr[data-id="${itemId}"]`);
            if (row) {
                const linkCell = row.querySelector('.file-link');
                if (linkCell) {
                    linkCell.innerHTML = `
                        <a href="${result.fileUrl}" target="_blank">Открыть акт</a>
                        <button class="delete-file-btn" data-id="${itemId}">Удалить</button>
                    `;

                }
            }
        } else {
            alert('Ошибка загрузки: ' + result.message);
        }
    } catch (e) {
        console.error(e);
        alert('Ошибка при отправке файла');
    }
}



// Асинхронная функция для обновления поля записи
async function updateField(id, field, value) {
    const apiUrl = `${apiBaseUrl}/update`; // Убедитесь, что apiBaseUrl определен в вашем коде
    const data = {
        id: parseInt(id, 10),
        fields: {
            [field]: value
        }
    };
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(apiUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (response.status !== 200) {// Можно вывести статус и текст ошибки
            const errorText = await response.text();
            console.error(`Ошибка: ${response.status} - ${errorText}`);
            throw new Error(`Ошибка при запросе: ${response.status}`);
        }

        const result = await response.json();

        // Можно добавить логику для обновления данных в таблице или отображения успеха
        console.log(`Обновлено поле ${field} для записи ${id}`, result);
        // Перезагружаем страницу после успешного обновления
        window.location.reload();

    } catch (error) {
        console.error('Ошибка при обновлении данных:', error);
        alert('Не удалось обновить данные. Попробуйте еще раз.');
    }
}