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
            // Остальные ячейки
            row.innerHTML += `
                <td>${item['id'] || ''}</td>
                <td>${item["Дата"] || ''}</td>
                <td>${item["Проведенные работы"] || ''}</td>
                <td>${item["примечание"] || ''}</td>
                <td>${item["статус акта"] || ''}</td>
                <td>${item["акт"] || ''}</td>
                <td>${item["фото"] || ''}</td>
                <td>${item["видео"] || ''}</td>
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