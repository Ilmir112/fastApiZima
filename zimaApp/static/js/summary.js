document.addEventListener('DOMContentLoaded', () => {
    const dataScript = document.getElementById('initial-data');
    let items = [];

    if (dataScript) {
        try {
            items = JSON.parse(dataScript.textContent);
        } catch (e) {
            console.error('Ошибка парсинга данных:', e);
        }
    }

    const tableBody = document.getElementById('tableBody');
    const filters = document.querySelectorAll('.filter-select');

    // Инициализация фильтров
    const initFilters = () => {
        const filterValues = {};

        filters.forEach(filter => {
            filterValues[filter.dataset.column] = new Set();
        });

        // Собираем уникальные значения для фильтров
        items.forEach(item => {
            filters.forEach(filter => {
                const col = filter.dataset.column;
                if (item[col] !== undefined && item[col] !== null && item[col] !== '') {
                    filterValues[col].add(item[col]);
                }
            });
        });

        // Заполняем селекты
        filters.forEach(filter => {
            const col = filter.dataset.column;
            // Очистка существующих опций кроме "Все"
            filter.innerHTML = '<option value="">Все</option>';

            Array.from(filterValues[col]).sort().forEach(val => {
                const option = document.createElement('option');
                option.value = val;
                option.textContent = val;
                filter.appendChild(option);
            });
        });
    };



    // Отрисовка таблицы
    const renderTable = () => {
        let filteredItems = items;

        // Применяем фильтры
        filters.forEach(filter => {
            const val = filter.value;
            if (val) {
                filteredItems = filteredItems.filter(item => String(item[filter.dataset.column]) === val);
            }
        });

        // Очистка таблицы
        tableBody.innerHTML = '';

        // Предположим, у вас есть таблица и tbody
        filteredItems.forEach(item => {
            const row = document.createElement('tr');

            // Создаем ячейку для ID с гиперссылкой
            const tdId = document.createElement('td');
            const link = document.createElement('a');
            link.href = `/pages/get_summary_by_id?summary_id=${item['id']}`; // используйте правильный id
            link.textContent = item['Номер Бригады'] || '';

            link.addEventListener('click', async (e) => {
                e.preventDefault(); // блокируем переход по ссылке
                const summaryId = item['id'];
                console.log('Клик по id:', summaryId);
                try {
                    const response = await fetch(`/pages/get_summary_by_id?summary_id=${summaryId}`);
                    if (!response.ok) {
                        throw new Error(`Error: ${response.status}`);
                    }
                    const result = await response.json();
                    // например, показываем результат в alert или модальном окне
                    alert(JSON.stringify(result));
                    // или вызываем функцию отображения данных
                } catch (err) {
                    console.error('Ошибка при вызове API:', err);
                }
            });

            tdId.appendChild(link);
            row.appendChild(tdId);

            // Остальные ячейки
            row.innerHTML += ` 
            <td>${item['Номер скважины'] || ''}</td>
            <td>${item['Месторождение'] || ''}</td>
            <td>${item['площадь'] || ''}</td>
            <td>${item['Статус ремонта'] || ''}</td>
            <td>${formatDateTime(item['Дата открытия ремонта'])}</td>
            <td>${item['Дата закрытия ремонта'] ? formatDateTime(item['Дата закрытия ремонта']) : ''}</td>
            <td>${calculateDurationHours(item['Дата открытия ремонта'], item['Дата закрытия ремонта'])}</td>
`;

            tableBody.appendChild(row);
        });
    };



    // Обработчики фильтров
    filters.forEach(filter => {
        filter.addEventListener('change', () => {
            renderTable();
        });
    });

    // Инициализация фильтров и таблицы при загрузке
    initFilters();
    renderTable();
});

// Вспомогательная функция для форматирования даты и времени без секунд
function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date)) return '';
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;}

// Вспомогательная функция для вычисления длительности в часах с учетом вычитания дней * 2 часа
function calculateDurationHours(startDateStr, endDateStr) {
    const startDate = new Date(startDateStr);
    let endDate;

    if (endDateStr) {
        endDate = new Date(endDateStr);
        if (isNaN(endDate)) {
            // Если дата некорректна, считаем текущим временем
            endDate = new Date();
        }
    } else {
        // Если дата закрытия отсутствует, используем текущее время
        endDate = new Date();
    }

    let diffMs = endDate - startDate;
    if (diffMs < 0) diffMs = 0; // на всякий случай

    // Переводим миллисекунды в часы
    let totalHours = diffMs / (1000 * 60 * 60);

    // Вычисляем количество полных дней
    const totalDays = Math.floor(totalHours / 24);

    // Вычитаем из общего количества часов по 2 часа за каждый полный день
    let adjustedHours = totalHours - (totalDays * 2);

    // Можно ограничить минимальное значение, например, не меньше нуля
    if (adjustedHours < 0) adjustedHours = 0;

    return adjustedHours.toFixed(2);
}
