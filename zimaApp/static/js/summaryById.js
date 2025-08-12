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

    // Обновление таблицы при фильтрации
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

        filteredItems.forEach(item => {
            const row = document.createElement('tr');
            row.setAttribute('data-id', item.id);

            // Дата
            row.innerHTML += `<td>${item["id"] || ''}</td>`;
            row.innerHTML += `<td>${item["Дата"] || ''}</td>`;

            // Проведенные работы
            row.innerHTML += `<td>${item["Проведенные работы"] || ''}</td>`;

            // Примечание - input с onchange
            const noteInputId = `note-${item.id}`;
            row.innerHTML += `<td><input type="text" id="${noteInputId}" value="${item["примечание"] || ''}"></td>`;

            // Статус акта
            row.innerHTML += `<td>${item["статус подписания"] || ''}</td>`;

            // Акт - ссылка или кнопка загрузки файла
            row.innerHTML += `<td>${generateFileCell(item, 'акт')}</td>`;

            // Фото - ссылка или кнопка загрузки файла
            row.innerHTML += `<td>${generateFileCell(item, 'фото')}</td>`;

            // Видео - ссылка или кнопка загрузки файла
            row.innerHTML += `<td>${generateFileCell(item, 'видео')}</td>`;

            tableBody.appendChild(row);

            // Назначение обработчиков для input "примечание"
            document.getElementById(noteInputId).addEventListener('change', () => {
                updateField(item.id, 'примечание', document.getElementById(noteInputId).value);
            });
        });

        // Обработчики кнопок удаления файлов
        document.querySelectorAll('.delete-file-btn_act').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const type = btn.dataset.type;
                deleteFileAct(id, type);
            });
        });

    // Обработчики кнопок удаления файлов
        document.querySelectorAll('.delete-file-btn_video').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const type = btn.dataset.type;
                deleteFileVideo(id, type);
            });
        });
    };

    async function deleteFileAct(itemId) {
        const token = localStorage.getItem('access_token');

        if (!confirm('Вы уверены, что хотите удалить файл?')) return;

        try {
            const response = await fetch('/files/delete_act', {
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

    async function deleteFileVideo(itemId) {
        const token = localStorage.getItem('access_token');

        if (!confirm('Вы уверены, что хотите удалить файл?')) return;

        try {
            const response = await fetch('/files/delete_video', {
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
                    const linkCell = row.querySelector('.file-link_video');
                    linkCell.innerHTML = `
                    <input type="file" accept=".mp4, .3gp" onchange="uploadFilePlan('${itemId}', this.files)">
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

// Генерация HTML для ячейки файла/ссылки
    function generateFileCell(item, fileType) {
        const fileUrl = item[fileType];
        let acceptTypes;

        if (fileType === 'фото') {
            if (fileUrl) {
                const linkCell = '';
                if (linkCell) {
                    const fileUrl = result; // ваш массив путей
                    if (fileUrl.length > 0) {
                        // Создаем кнопку для открытия всех файлов
                        linkCell.innerHTML = `
                        
                        <button id="openFilesBtn_${itemId}">Открыть файлы</button>
                        <button id="deleteFilesBtn_${itemId}">Удалить файлы</button>
                    `;

                        // Обработчик для открытия файлов
                        document.getElementById(`openFilesBtn_${itemId}`).addEventListener('click', () => {
                            const token = localStorage.getItem('access_token');
                            filePaths.forEach(path => {
                                const url = path.startsWith('http') ? path : `${apiBaseUrl}/${path}`;
                                window.open(url, '_blank');
                            });
                        });

                        // Обработчик для удаления файлов
                        document.getElementById(`deleteFilesBtn_${itemId}`).addEventListener('click', () => {
                            // Тут вызовите API для удаления файлов, например:
                            fetch(`/files/delete_photo`, {
                                method: 'DELETE',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                                },
                                body: JSON.stringify({paths: filePaths}),
                            })
                                .then(res => res.json())
                                .then(data => {
                                    if (data.success) {
                                        alert('Файлы удалены');
                                        // Обновите UI, например, очистите ячейку
                                        linkCell.innerHTML = '';
                                    } else {
                                        alert('Ошибка при удалении файлов');
                                    }
                                })
                                .catch(e => {
                                    console.error(e);
                                    alert('Ошибка сервера при удалении');
                                });
                        });
                    } else {
                        linkCell.innerHTML = 'Нет файлов';
                    }
                }
                const urls = Array.isArray(fileUrl) ? fileUrl : [fileUrl];

                // Создаем HTML для каждого файла
                const linksHtml = `
                    <div class="files-container" style="display: flex; gap: 10px; flex-wrap: wrap;">
                        ${urls.map(url => `
                            <div class="file-link" style="display: flex; align-items: center; gap: 10px;">
                                <a href="${url}" target="_blank">Открыть ${fileType}</a>
                                <button class="delete-file-btn_photo" data-id="${item.id}" data-type="${fileType}">Удалить</button>
                            </div>
                        `).join('')}
                    </div>
                `;
                return linksHtml;
            } else {
                return `
                <div class="file-link">
                    <input type="file" multiple accept=".png,.jpeg,.jpg,.pdf" onchange="uploadFilePhoto('${item.id}', this.files)">
                </div>
            `;
            }


        } else {
            acceptTypes = ".png,.jpeg,.jpg,.pdf";
        }

        if (fileType === 'акт') {
            if (fileUrl.length > 0) {
                // Есть файл — показываем ссылку и кнопку удаления
                return `
            <div class="file-link_act">
                <a href="${fileUrl}" target="_blank">Открыть ${fileType}</a>
                <button class="delete-file-btn_act" data-id="${item.id}" data-type="${fileType}">Удалить</button>
            </div>
        `;
            } else {
                return `
                <div class="file-link_act">
                    <input type="file" accept=".pdf" onchange="uploadFileAct('${item.id}', this.files)">
                </div>
`;

            }
        } else {
            if (fileUrl.length > 0) {
                // Есть файл — показываем ссылку и кнопку удаления
                return `
            <div class="file-link_video">
                <a href="${fileUrl}" target="_blank">Открыть ${fileType}</a>
                <button class="delete-file-btn_video" data-id="${item.id}" data-type="${fileType}">Удалить</button>
            </div>
        `;
            } else {
                return `
                <div class="file-link_video">
                    <input type="file" accept=".mp4, .3gp" onchange="uploadFile('${item.id}', this.files)">
                </div>
`;

            }

        }
    }

    // Инициализация фильтров и таблицы при загрузке
    initFilters();
    renderTable();

    // Обработчики фильтров
    filters.forEach(filter => {
        filter.addEventListener('change', () => {
            renderTable();
        });
    });

});

async function uploadFile(itemId, files) {
    if (!files || files.length === 0) return;
    const token = localStorage.getItem('access_token');
    const file = files[0];
    const formData = new FormData();

    formData.append('file', file);
    formData.append('itemId', itemId);


    try {
        const response = await fetch('/files/upload_video', {
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
            if (row) { // исправлено условие
                const linkCell = row.querySelector('.file-link_video');
                if (linkCell) {
                    linkCell.innerHTML = `
                        <a href="${result.fileUrl}" target="_blank">Открыть видео</a>
                        <button class="delete-file-btn_act" data-id="${itemId}">Удалить</button>
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

async function uploadFileAct(itemId, files) {
    if (!files || files.length === 0) return;
    const token = localStorage.getItem('access_token');
    const file = files[0];
    const formData = new FormData();
    // Вызов модального окна и ожидание выбора статуса
    const statusWorkPlan = await window.askStatus();

    // Проверка, если пользователь отменил выбор (statusWorkPlan === null)
    if (statusWorkPlan === "") {
        alert('Загрузка отменена: не выбран статус.');
        return;
    }
    formData.append('file', file);
    formData.append('itemId', itemId);
    formData.append('status', statusWorkPlan)


    try {
        const response = await fetch('/files/upload_summary_act', {
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
            if (row) { // исправлено условие
                const linkCell = row.querySelector('.file-link_act');
                if (linkCell) {
                    linkCell.innerHTML = `
                        <a href="${result.fileUrl}" target="_blank">Открыть акт</a>
                        <button class="delete-file-btn_video" data-id="${itemId}">Удалить</button>
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


async function uploadFilePhoto(itemId, files) {
    if (!files || files.length === 0) return;
    const token = localStorage.getItem('access_token');
    const formData = new FormData();

    // Добавляем все файлы
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    try {
        const response = await fetch(`/files/upload_images?itemId=${encodeURIComponent(itemId)}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                // Не добавляйте 'Content-Type' — браузер установит его автоматически
            },
            body: formData,
        });
        const result = await response.json();
        if (response.status === 200) {
            const row = document.querySelector(`tr[data-id="${itemId}"]`);
            if (row) {
                const linkCell = row.querySelector('.file-link_photo');
                if (linkCell) {
                    const filePaths = result; // ваш массив путей
                    if (filePaths.length > 0) {
                        // Создаем кнопку для открытия всех файлов
                        linkCell.innerHTML = `
                    
                    <button id="openFilesBtn_${itemId}">Открыть файлы</button>
                    <button id="deleteFilesBtn_${itemId}">Удалить файлы</button>
                `;

                        // Обработчик для открытия файлов
                        document.getElementById(`openFilesBtn_${itemId}`).addEventListener('click', () => {
                            const token = localStorage.getItem('access_token');
                            filePaths.forEach(path => {
                                const url = path.startsWith('http') ? path : `${apiBaseUrl}/${path}`;
                                window.open(url, '_blank');
                            });
                        });

                        // Обработчик для удаления файлов
                        document.getElementById(`deleteFilesBtn_${itemId}`).addEventListener('click', () => {
                            // Тут вызовите API для удаления файлов, например:
                            fetch(`/files/delete_photo`, {
                                method: 'DELETE',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                                },
                                body: JSON.stringify({paths: filePaths}),
                            })
                                .then(res => res.json())
                                .then(data => {
                                    if (data.success) {
                                        alert('Файлы удалены');
                                        // Обновите UI, например, очистите ячейку
                                        linkCell.innerHTML = '';
                                    } else {
                                        alert('Ошибка при удалении файлов');
                                    }
                                })
                                .catch(e => {
                                    console.error(e);
                                    alert('Ошибка сервера при удалении');
                                });
                        });
                    } else {
                        linkCell.innerHTML = 'Нет файлов';
                    }
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

