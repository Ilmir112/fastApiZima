function generateTableHTML(tableData) {
    const table = document.createElement('table');
    table.style.borderCollapse = 'collapse';

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

            if (occupied[`${r},${col}`]) return;

            const td = document.createElement('td');
            td.innerHTML = content;

            // Применяем стили
            for (const [key, value] of Object.entries(style)) {
                td.style[key] = value;
            }

            // Выравнивание текста
            if (['left', 'center', 'right'].includes(alignment)) {
                td.style.textAlign = alignment;
            }

            // Обработка границ снизу
            if (border && typeof border === 'object') {
                for (const [borderSide, borderStyle] of Object.entries(border)) {
                    let side = borderSide;
                    if (side === 'border') side = 'border';

                    if (borderStyle === 'thin' || borderStyle === 'medium') {
                        td.style['border-' + side] = '1px solid #000';

                    }
                }
            }

            // Объединения ячеек
            if (colSpan > 1) td.colSpan = colSpan;
            if (rowSpan > 1) td.rowSpan = rowSpan;

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

    // Вставляем таблицу в контейнер
    const container = document.getElementById('tableContainer');
    container.innerHTML = '';
    container.appendChild(table);
}

// static/js/scripts.js

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
              .then(response => {
                if (!response.ok) {
                  throw new Error(`HTTP error! статус: ${response.status}`);
                }
                return response.json();
              })
              .then(data => {
                displayData(data);
              })
              .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при загрузке данных.');
              });
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
            } else {
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

