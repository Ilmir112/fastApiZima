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

async function showDropdown(values, column) {
    let dropdown = document.getElementById('columnFilterDropdown');
    if (!dropdown) {
        dropdown = document.createElement('select');
        dropdown.id = 'columnFilterDropdown';
        document.body.appendChild(dropdown);
    }
    dropdown.innerHTML = '';

    function getColumnIndex(columnName) {
        const headers = document.querySelectorAll('#repairs thead th');
        console.log('Найденные заголовки:', headers.length);
        headers.forEach((header, index) => {
            console.log(`Header ${index}:`, header.innerText.trim());
        });
        for (let i = 0; i < headers.length; i++) {
            if (headers[i].innerText.trim() === columnName) return i;
        }
        return -1;
    }

    async function filterTableByColumn(column, value) {
        const tbody = document.getElementById('tableBody');
        if (!tbody) return;
        const columnIndex = getColumnIndex(column);
        if (columnIndex === -1) {
            console.warn(`Колонка "${column}" не найдена`);
            return;
        }

        Array.from(tbody.rows).forEach(row => {
            const cells = row.cells;
            if (cells.length > columnIndex) {
                const cellText = cells[columnIndex].innerText.trim();
                if (cellText === value || value === '') {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            }
        });
    }

    values.forEach(val => {
        const option = document.createElement('option');
        option.value = val;
        option.textContent = val;
        dropdown.appendChild(option);
    });

    // Позиционируем рядом с кнопкой
    const btn = document.querySelector(`button[data-column="${column}"]`);
    if (btn) {
        const rect = btn.getBoundingClientRect();
        dropdown.style.position = 'absolute';
        dropdown.style.top = `${rect.bottom + window.scrollY}px`;
        dropdown.style.left = `${rect.left + window.scrollX}px`;
        dropdown.style.display = 'block';

        // Обработчик выбора
        dropdown.onchange = () => {
            filterTableByColumn(column, dropdown.value);
            dropdown.style.display = 'none';
        };
    }
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
        const contractorOpinionInput = `<input type="text" value="${item.contractor_opinion || ''}" onchange="updateField('${item.id}', 'contractor_opinion', this.value)">`;
        const meetingResultInput = `<input type="text" value="${item.meeting_result || ''}" onchange="updateField('${item.id}', 'meeting_result', this.value)">`;


        const reasonHtml = `
            <div class="tooltiptext">
                ${shortReason}
                <span class="tooltiptext">${reasonText}</span>
            </div>`;

        // Создаем строку таблицы
        const rowHtml = `

                <tr>
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
                    <td>${meetingResultInput}
                    <td>

                    <!-- PDF или изображение -->
                    ${item.image_pdf ? `<a href="${item.image_pdf}" target="_blank">Открыть PDF/Изображение</a>` : ''}
                    </td>
                </tr>`;

        tbody.insertAdjacentHTML('beforeend', rowHtml);
    });

    // loadingEl.style.display = 'none';
    // tableEl.style.display = '';

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

// Асинхронная функция для обновления поля записи
async function updateField(id, field, value) {
    const apiUrl = `${apiBaseUrl}/update`; // Убедитесь, что apiBaseUrl определен в вашем коде
    const data = {
        id: parseInt(id, 10),
        fields: {
            [field]: value
        }
    };

    try {
        const response = await fetch(apiUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Ошибка при обновлении: ${response.statusText}`);
        }

        const result = await response.json();

        // Можно добавить логику для обновления данных в таблице или отображения успеха
        console.log(`Обновлено поле ${field} для записи ${id}`, result);
    } catch (error) {
        console.error('Ошибка при обновлении данных:', error);
        alert('Не удалось обновить данные. Попробуйте еще раз.');
    }
}