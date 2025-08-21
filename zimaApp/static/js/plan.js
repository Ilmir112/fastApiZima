// Функция для генерации таблицы с цветами
function generateTableHTML(tableData) {
    const table = document.createElement('table');
    table.style.borderCollapse = 'collapse';
    table.style.width = '100%';
    table.style.fontFamily = 'Arial, sans-serif';
    table.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
    table.style.borderRadius = '2px';
    table.style.overflow = 'hidden';

    const occupied = {};

    tableData.row.forEach((rowData, rowIndex) => {
        const tr = document.createElement('tr');
        tr.style.height = rowData.height + 'px';

        rowData.cells.forEach(cell => {
            const {
                col,
                row: r,
                colSpan = 1,
                rowSpan = 1,
                content = '',
                style = {},
                alignment = 'left',
                border = {}
            } = cell;

            // Пропускаем первую колонку (col === 0)
            if (col === 0) return;

            if (occupied[`${r},${col}`]) return;

            const td = document.createElement('td');
            td.innerHTML = content;

            // Применяем стили с яркими цветами
            for (const [key, value] of Object.entries(style)) {
                td.style[key] = value;
            }

            // Выравнивание текста
            if (['left', 'center', 'right'].includes(alignment)) {
                td.style.textAlign = alignment;
            }

            // Внутренние отступы
            td.style.padding = '10px';

            // Обработка границ снизу
            if (border && typeof border === 'object') {
                for (const [borderSide, borderStyle] of Object.entries(border)) {
                    let side = borderSide;
                    if (side === 'border') side = 'border';

                    if (borderStyle === 'thin' || borderStyle === 'medium') {
                        td.style['border-' + side] = '1px solid #000000';
                    }
                }
            }

            // Объединения ячеек
            if (colSpan > 1) td.colSpan = colSpan;
            if (rowSpan > 1) td.rowSpan = rowSpan;

            // Фоновый цвет
            td.style.backgroundColor = '#faf7f7';

            tr.appendChild(td);

            // Помечаем занятые ячейки из-за объединений
            for (let rOffset = 0; rOffset < rowSpan; rOffset++) {
                for (let cOffset = 0; cOffset < colSpan; cOffset++) {
                    if (rOffset === 0 && cOffset === 0) continue;
                    occupied[`${r + rOffset},${col + cOffset}`] = true;
                }
            }
        });

        table.appendChild(tr);
    });

    // Вставляем таблицу в контейнер с ярким фоном
    const container = document.getElementById('tableContainer');
    container.innerHTML = '';
    container.style.backgroundColor = '#f0f8ff'; // светло-голубой фон контейнера
    container.style.padding = '10px 15px 20px 25px'; // top right bottom left
    container.appendChild(table);
}

// Остальной код без изменений, добавим стили для кнопок и модального окна

// Стиль для кнопок загрузки файла и удаления файла
const styleSheet = document.createElement('style');
styleSheet.innerText = `
/* Общие стили для кнопок */
button {
    background-color: #4CAF50; /* зеленый */
    color: white;
    border: none;
    padding: 8px 12px;
    margin: 4px;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
}
button:hover {
    background-color: #45a049;
}

/* Стиль для кнопки удаления */
button.delete-file-btn {
    background-color: #e74c3c; /* красный */
}
button.delete-file-btn:hover {
    background-color: #c0392b;
}

/* Стиль для ссылок "Открыть план" */
a {
    color: #2980b9; /* синий */
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}



/* Стиль для таблицы данных */
#dataTable {
   width: 100%;
   border-collapse: collapse;
   margin-top:20px;
   font-family:'Arial Rounded MT Bold', cursive, sans-serif ;
}
#dataTable th, #dataTable td {
   padding:10px ;
   border-bottom :2 px solid #ddd ;
}
#dataTable th{
   background-color:#ffe4b5 ; /* светло-оранжевый */
   color:#333 ;
}
#dataTable tr:nth-child(even){
   background-color:#f9f9f9 ;
}
`;
document.head.appendChild(styleSheet);

// Обработчик для открытия модального окна
function openModal() {
    const modal = document.getElementById('myModal');

    modal.style.display = 'flex';
    modal.classList.add('show');


    // Назначаем обработчики только один раз
    const confirmBtn = document.getElementById('confirmBtn');
    const cancelBtn = document.getElementById('cancelBtn');

    // Очистка предыдущих обработчиков
    confirmBtn.onclick = null;
    cancelBtn.onclick = null;

    // Обработчик подтверждения
    confirmBtn.onclick = () => {
        const selectedStatus = document.getElementById('statusSelect').value;

        closeModal();
        resolveStatus(selectedStatus);
    };

    // Обработчик отмены
    cancelBtn.onclick = () => {
        closeModal();
        resolveStatus(null);
    };
}

// Функция для закрытия модального окна
function closeModal() {
    document.getElementById('myModal').style.display = 'none';
     // modal.classList.remove('show');
}

// Объявляем переменную для хранения промиса
let statusPromiseResolve;

// Функция для получения статуса через промис
function askStatus() {
    return new Promise((resolve) => {
        statusPromiseResolve = resolve;
        openModal();
    });
}

// Внутренний вызов для разрешения промиса
function resolveStatus(status) {
    if (statusPromiseResolve) {
        statusPromiseResolve(status);
        statusPromiseResolve = null;
    }
}

// В событии загрузки страницы назначьте обработчик для кнопки загрузки файла
document.addEventListener('DOMContentLoaded', () => {
    const loadBtn = document.getElementById('loadDataBtn');
    if (loadBtn) {
        loadBtn.addEventListener('click', () => {
            const wellNumber = document.getElementById('wellNumberInput').value.trim();
            if (!wellNumber) {
                alert('Пожалуйста, введите номер скважины.');
                return;
            }
            const url = `/wells_repair_router/find_repair_filter_by_number?well_number=${encodeURIComponent(wellNumber)}`;
            fetch(url)
                .then(response => response.json())
                .then(data => displayData(data))
                .catch(error => alert('Произошла ошибка при загрузке данных.'));
        });
    }
});


// Функция для отображения данных в виде таблицы
function displayData(data) {
    const container = document.getElementById('tableContainer');
    container.innerHTML = '';

    if (!data || data.length === 0) {
        container.innerHTML = '<p>Нет данных для отображения.</p>';
        return;
    }

    const table = document.createElement('table');
    table.id = 'dataTable';

    // Заголовки таблицы
    const headers = Object.keys(data[0]);
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    headers.forEach(key => {
        const th = document.createElement('th');
        th.textContent = key;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Тело таблицы
    const tbody = document.createElement('tbody');

    data.forEach(item => {
        const row = document.createElement('tr');
        row.setAttribute('data-id', item.id);

        headers.forEach(key => {
            const td = document.createElement('td');

            if (key === 'Номер скважины') {
                const link = document.createElement('a');
                link.href = '#';
                link.textContent = item[key];
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    findWellById(item['id']);
                });
                td.appendChild(link);
            } else if (key === 'план работ') {
                // Обработка столбца "план работ"
                const planValue = item[key];

                // Добавляем класс всегда
                td.className = 'file-link';

                if (!planValue) {
                    // Нет файла, показываем кнопку для загрузки файла
                    td.innerHTML = `<input type="file" accept=".png,.jpeg,.jpg,.pdf" onchange="uploadFilePlan('${item.id}', this.files)">`;
                } else {
                    // Есть файл, показываем ссылку "Открыть" и кнопку "Удалить"
                    td.innerHTML = `
                        <a href="${planValue}" target="_blank">Открыть план</a>
                        <button class="delete-file-btn" data-id="${item.id}" onclick="deleteFile('${item.id}')">Удалить</button>
                    `;
                }
            } else if (key === 'Статус подписания') {
                let statusValue = item[key];
                if (!statusValue) {
                    statusValue = 'не подписан';
                }
                td.textContent = statusValue;
            } else {
                // Остальные поля
                td.textContent = item[key];
            }

            row.appendChild(td);
        });

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}


// Функция для перехода по ID скважины
function findWellById(wellId) {
    window.location.href = `/pages/plan_work?id=${wellId}`;
}


async function uploadFilePlan(itemId, files) {
    if (!files || files.length === 0) return;
    const token = localStorage.getItem('access_token');
    const file = files[0];
    const formData = new FormData();
    // Вызов модального окна и ожидание выбора статуса
    const statusWorkPlan = await askStatus();

    // Проверка, если пользователь отменил выбор (statusWorkPlan === null)
    if (statusWorkPlan === "") {
        alert('Загрузка отменена: не выбран статус.');
        return;
    }
    formData.append('file', file);
    formData.append('itemId', itemId);
    formData.append('status', statusWorkPlan)


    try {
        const response = await fetch('/files/upload_plan', {
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
                        <a href="${result.fileUrl}" target="_blank">Открыть план</a>
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

async function deleteFile(itemId) {
    const token = localStorage.getItem('access_token');

    if (!confirm('Вы уверены, что хотите удалить файл?')) return;

    try {
        const response = await fetch('/files/delete_plan', {
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
                    <input type="file" accept=".png,.jpeg,.jpg,.pdf" onchange="uploadFilePlan('${itemId}', this.files)">
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


async function askStatus() {
    return new Promise((resolve) => {
        openModal();

// Обработчик подтверждения
        confirmBtn.onclick = () => {
            const selectedStatus = document.getElementById('statusSelect').value;
            closeModal();
            resolve(selectedStatus);
        };

// Обработчик отмены
        cancelBtn.onclick = () => {
            closeModal();
            resolve(null);
        };
    });
}

window.askStatus = askStatus