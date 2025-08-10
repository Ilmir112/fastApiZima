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
                <td>${formatDateTime(item['Дата закрытия ремонта'])}</td>
              `;

            tableBody.appendChild(row);
        });
    };

    // Форматирование даты
    function formatDateTime(dateStr) {
        if (!dateStr) return '';
        const dateObj = new Date(dateStr);
        if (isNaN(dateObj)) return '';
        return dateObj.toLocaleString(); // или другой формат
    }

    // Расчет длительности
    function getDuration(startStr, endStr) {
        if (!startStr || !endStr) return 'В процессе';
        const startDate = new Date(startStr);
        const endDate = new Date(endStr);

        if (isNaN(startDate) || isNaN(endDate)) return 'В процессе';

        const diffMs = endDate - startDate;
        const diffHrs = diffMs / (1000 * 60 * 60);

        if (diffHrs <= 0) return '0 суток';

        const days = Math.floor(diffHrs / 24);

        return `${days} суток`;
    }

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