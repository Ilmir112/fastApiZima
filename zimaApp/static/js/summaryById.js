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
    const filters = document.querySelectorAll('.filter-container');

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
                const item_frr = item
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

    // 1. ID
    const idTd = document.createElement('td');
    idTd.textContent = item["id"] || '';
    row.appendChild(idTd);

    // 2. Дата
    const dateTd = document.createElement('td');
    dateTd.textContent = item["Дата"] || '';
    row.appendChild(dateTd);

    // 3. Проведенные работы
    const worksTd = document.createElement('td');
    worksTd.textContent = item["Проведенные работы"] || '';
    row.appendChild(worksTd);

    // 4. Примечание - input с onchange
    const noteTd = document.createElement('td');
    const noteInputId = `note-${item.id}`;
    const noteInput = document.createElement('input');
    noteInput.type = 'text';
    noteInput.id = noteInputId;
    noteInput.value = item["примечание"] || '';
    noteTd.appendChild(noteInput);
    row.appendChild(noteTd);

    // 5. Статус подписания
    const statusTd = document.createElement('td');
    statusTd.textContent = item["статус подписания"] || '';
    row.appendChild(statusTd);

    // 6. Акт - ссылка или кнопка загрузки файла
    const actTd = document.createElement('td');
    actTd.appendChild(generateFileCell(item, 'акт'));
    row.appendChild(actTd);

    // 7. Фото - ссылка или кнопка загрузки файла
    const photoTd = document.createElement('td');
    photoTd.appendChild(generateFileCell(item, 'фото'));
    row.appendChild(photoTd);

    // 8. Видео - ссылка или кнопка загрузки файла
    const videoTd = document.createElement('td');
    videoTd.appendChild(generateFileCell(item, 'видео'));

    row.appendChild(videoTd);



// Добавляем строку в таблицу
tableBody.appendChild(row);


            // Назначение обработчиков для input "примечание"
            document.getElementById(noteInputId).addEventListener('change', () => {
                updateField(item.id, 'примечание', document.getElementById(noteInputId).value).then();
            });
        });

        // Обработчики кнопок удаления файлов
        document.querySelectorAll('.delete-file-btn_act').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const type = btn.dataset.type;
                deleteFileAct(id, type).then();
            });
        });

        // Обработчики кнопок удаления файлов
        document.querySelectorAll('.delete-file-btn_video').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const type = btn.dataset.type;
                deleteFileVideo(id, type).then();
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
                    const linkCell = row.querySelector('.file-link_act');
                    linkCell.innerHTML = `
                    <input type="file" accept=".pdf" onchange="uploadFileAct('${itemId}', this.files)">
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

    if (fileType === 'фото') {
        let linkCell;
        // Создаем контейнер для кнопок
        linkCell = document.createElement('div');
        linkCell.style.display = 'grid';
        linkCell.style.gridTemplateColumns = '1fr 1fr';
        linkCell.style.gap = '5px';
        if (fileUrl && fileUrl.length > 0) {


            // Для каждого файла создаем кнопки
            fileUrl.forEach((path, index) => {
                // Кнопка "Открыть файлы"
                const openBtn = document.createElement('button');
                openBtn.id = `openFilesBtn_${item.id}_${index}`;
                openBtn.textContent = 'Открыть';
                openBtn.style.fontSize = '10px';
                openBtn.style.padding = '3px 4px';

                openBtn.addEventListener('click', () => {

                    const url = path.startsWith('http') ? path : `${path}`;
                      const link = document.createElement('a');
                      link.href = url;
                      link.target = '_blank';
                      link.textContent = 'Открыть ' ;
                      document.body.appendChild(link);
                      link.click();
                      document.body.removeChild(link);
                });

                // Кнопка "Удалить файлы"
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Удалить';
                deleteBtn.style.fontSize = '10px';
                deleteBtn.style.padding = '3px 6px';

                deleteBtn.id = `deleteFilesBtn_${item.id}_${index}`;



                deleteBtn.addEventListener('click', () => {
                    fetch(`/files/delete_photo`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                        },
                        body: JSON.stringify({ itemId: item.id, fileUrl: path }), // Передаем itemId
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            alert('Файл удален');
                            // Обновляем UI
                            linkCell.innerHTML = '';
                        } else {
                            alert('Ошибка при удалении файла');
                        }
                    })
                    .catch(e => {
                        console.error(e);
                        alert('Ошибка сервера при удалении');
                    });
                });

                // Добавляем кнопки в контейнер
                linkCell.appendChild(openBtn);
                linkCell.appendChild(deleteBtn);
            });
        } else {
            const inputFile = document.createElement('input');
            inputFile.type = 'file';
            inputFile.accept = '.jpeg,.png'; // или 'image/jpeg, image/png'
            inputFile.multiple = true; // разрешить выбор нескольких файлов

            // Можно добавить обработчик выбора файлов
            inputFile.addEventListener('change', () => {
                const files = inputFile.files; // это будет FileList с выбранными файлами
                for (let i = 0; i < files.length; i++) {
                    console.log(files[i].name);

                }
                uploadFilePhoto(item.id, files);
            });


            linkCell.appendChild(inputFile)
        }
        return linkCell;}
    else if (fileType === 'акт') {
        const container = document.createElement('div');
        container.className = 'file-link_act';

        if (fileUrl && fileUrl.length > 0) {
            const link = document.createElement('a');
            link.href = fileUrl;
            link.target = '_blank';
            link.textContent = 'Открыть ' + fileType;

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-file-btn_act';
            deleteBtn.dataset.id = item.id;
            deleteBtn.dataset.type = fileType;
            deleteBtn.textContent = 'Удалить';

            // Обработчик удаления
            deleteBtn.addEventListener('click', () => {
                // ваш fetch-запрос
                fetch(`/files/delete_photo`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    },
                    body: JSON.stringify({ paths: [fileUrl] }),
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('Файл удален');
                        // Обновить UI по необходимости
                        container.innerHTML = '';
                    } else {
                        alert('Ошибка при удалении файла');
                    }
                })
                .catch(e => {
                    console.error(e);
                    alert('Ошибка сервера при удалении');
                });
            });

            container.appendChild(link);
            container.appendChild(deleteBtn);
        } else {
            const inputFile = document.createElement('input');
            inputFile.type = 'file';
            inputFile.accept = '.pdf';
            inputFile.onchange = () => uploadFileAct(item.id, inputFile.files);
            container.appendChild(inputFile);
        }

        return container;
    } else if (fileType === 'видео') {
        const container = document.createElement('div');
        container.className = 'file-link_video';

        if (fileUrl && fileUrl.length > 0) {
            const link = document.createElement('a');
            link.href = fileUrl;
            link.target = '_blank';
            link.textContent = 'Открыть ' + fileType;

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-file-btn_video';
            deleteBtn.dataset.id = item.id;
            deleteBtn.dataset.type = fileType;
            deleteBtn.textContent = 'Удалить';

            // Обработчик удаления
            deleteBtn.addEventListener('click', () => {
                fetch(`/files/delete_video`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    },
                    body: JSON.stringify({ paths: [fileUrl] }),
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('Файл удален');
                        container.innerHTML = '';
                    } else {
                        alert('Ошибка при удалении файла');
                    }
                })
                .catch(e => {
                    console.error(e);
                    alert('Ошибка сервера при удалении');
                });
            });

            container.appendChild(link);
            container.appendChild(deleteBtn);
        } else {
            const inputFile = document.createElement('input');
            inputFile.type = 'file';
            inputFile.accept = '.mp4,.3gp';
            inputFile.onchange = () => uploadFile(item.id, inputFile.files);
            container.appendChild(inputFile);
        }

        return container;
    }

    return null;
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

})
;

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
                        <div class="file-link_act">
                            <a href="${result.fileUrl}" target="_blank">Открыть</a>
                            <button class="delete-file-btn_act" data-id="${itemId}" data-type="Акт">Удалить</button>
                </div>
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
                    
                    <button id="openFilesBtn_${itemId}">Открыть фото</button>
                    <button id="deleteFilesBtn_${itemId}">Удалить фото</button>
                `;

                        // Обработчик для открытия файлов
                        document.getElementById(`openFilesBtn_${itemId}`).addEventListener('click', () => {
                            const token = localStorage.getItem('access_token');
                            filePaths.forEach(path => {
                                const url = path.startsWith('http') ? path : `${apiBaseUrl}/${path}`;
                                  const link = document.createElement('a');
                                  link.href = url;
                                  link.target = '_blank';
                                  link.textContent = 'Открыть ' ;
                                  document.body.appendChild(link);
                                  link.click();
                                  document.body.removeChild(link);
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

