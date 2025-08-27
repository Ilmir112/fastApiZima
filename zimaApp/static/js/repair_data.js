document.addEventListener('DOMContentLoaded', () => {
  const loadingEl = document.getElementById('loading');
  const errorEl = document.getElementById('error-message');
  const tableBody = document.getElementById('tableBody');

  let allData = [];
  let filteredData = [];

  // Получение начальных данных из embedded JSON
  const initialDataScript = document.getElementById('initial-data');
  if (initialDataScript) {
    try {
      allData = JSON.parse(initialDataScript.textContent);
      filteredData = [...allData];
      renderTable(filteredData);
      populateFilters(allData);
    } catch (e) {
      console.error('Ошибка парсинга начальных данных:', e);
    }
  } else {
    // Если данных нет, можно сделать запрос к API
    fetchData();
  }

  // Функция для загрузки данных с сервера
  async function fetchData() {
    const token = localStorage.getItem('access_token');
    try {
      showLoading(true);
      const response = await fetch('/pages/repair_data', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
         body: formData,

        });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json();
      if (result.status === 'success') {
        allData = result.data;
        filteredData = [...allData];
        renderTable(filteredData);
        populateFilters(allData);
      } else {
        showError('Ошибка получения данных');
      }
    } catch (err) {
      showError(`Ошибка загрузки данных: ${err.message}`);
    } finally {
      showLoading(false);
    }
  }

  function showLoading(show) {
    loadingEl.style.display = show ? 'block' : 'none';
  }

  function showError(message) {
    errorEl.textContent = message;
    errorEl.style.display = message ? 'block' : 'none';
  }

  // Функция для отображения таблицы
  function renderTable(data) {
    tableBody.innerHTML = '';
    data.forEach(item => {
      const row = document.createElement('tr');

      row.innerHTML = `
        <td>${item.contractor || ''}</td>
        <td>${item.brigade_number || ''}</td>
        <td>${item.well_area || ''}</td>
        <td>${item.well_number || ''}</td>
        <td>${formatDateTime(item.begin_time)}</td>
        <td>${formatDateTime(item.finish_time)}</td>
        <td>${item.category_repair || ''}</td>
        <td>${item.repair_code || ''}</td>
        <td>${item.type_repair || ''}</td>
        <td>${calculateDurationHours(item.begin_time, item.finish_time)}</td>
        <td>${item.kust || ''}</td>
      `;
      tableBody.appendChild(row);
    });
  }

  function formatDateTime(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString(); // Можно форматировать по необходимости
  }

  function calculateDurationHours(startStr, endStr) {
    if (!startStr || !endStr) return '';
    const start = new Date(startStr);
    const end = new Date(endStr);
    const diffMs = end - start;
    return (diffMs / (1000 * 60 * 60)).toFixed(2); // часы с двумя знаками
  }

  // Заполнение фильтров уникальными значениями
  function populateFilters(data) {
    const filterColumns = [
      { key: 'contractor', selectId: null },
      { key: 'brigade_number', selectId: null },
      { key: 'well_area', selectId: null },
      { key: 'well_number', selectId: null },
      { key: 'category_repair', selectId: null },
      { key: 'type_repair', selectId: null },
      { key: 'kust', selectId: null }
    ];

    filterColumns.forEach(col => {
      const optionsSet = new Set();
      data.forEach(item => optionsSet.add(item[col.key]));

      // Находим соответствующий селект
      const selectEl = document.querySelector(`.filter-select[data-column="${col.key}"]`) ||
                       document.querySelector(`.filter-input[data-column="${col.key}"]`);

      if (selectEl && selectEl.tagName.toLowerCase() === 'select') {
        optionsSet.forEach(val => {
          if (val !== null && val !== undefined && val !== '') {
            const option = document.createElement('option');
            option.value = val;
            option.textContent = val;
            selectEl.appendChild(option);
          }
        });
      }

      // Для input фильтров можно оставить как есть или добавить обработчики
    });
  }

  // Обработчики фильтров
  document.querySelectorAll('.filter-select').forEach(select => {
    select.addEventListener('change', applyFilters);
  });

  document.querySelectorAll('.filter-input').forEach(input => {
    input.addEventListener('input', applyFilters);
  });

  function applyFilters() {
    let filtered = [...allData];

    document.querySelectorAll('.filter-select').forEach(select => {
      const colKey = select.dataset.column;
      const val = select.value;

      if (val) {
        filtered = filtered.filter(item => item[colKey] === val);
      }
    });

    document.querySelectorAll('.filter-input').forEach(input => {
      const colKey = input.dataset.column;
      const val = input.value.trim().toLowerCase();

      if (val) {
        filtered = filtered.filter(item =>
          (item[colKey] || '').toString().toLowerCase().includes(val)
        );
      }
    });

    renderTable(filtered);
  }
});