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

            // // 1. ID
            // const idTd = document.createElement('td');
            // idTd.textContent = item["id"] || '';
            // row.appendChild(idTd);

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

        // // Обработчики кнопок удаления файлов
        // document.querySelectorAll('.delete-file-btn_act').forEach(btn => {
        //     btn.addEventListener('click', () => {
        //         const id = btn.dataset.id;
        //         const type = btn.dataset.type;
        //         deleteFileAct(id, type).then();
        //     });
        // });

        // // Обработчики кнопок удаления файлов
        // document.querySelectorAll('.delete-file-btn_video').forEach(btn => {
        //     btn.addEventListener('click', () => {
        //         const id = btn.dataset.id;
        //         const type = btn.dataset.type;
        //         deleteFileVideo(id, type).then();
        //     });
        // });
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
                // Обновляем таблицу: заменяем ссылку на input для загрузки файла
                const row = document.querySelector(`tr[data-id="${itemId}"]`);
                if (row) {
                    const linkCell = row.querySelector('a[href*="act_path"]');
                    if (linkCell) {
                        // Очищаем содержимое ячейки
                        linkCell.innerHTML = '';
                        let deleteBtn = row.querySelector('.delete-file-btn_act');
                        if (deleteBtn) {
                            deleteBtn.style.display = 'none'; // или 'block', если нужно
                        }

                        // Создаем новый input для загрузки файла
                        const inputFile = document.createElement('input');
                        inputFile.type = 'file';
                        inputFile.accept = '.pdf';
                        inputFile.onchange = () => uploadFileAct(itemId, inputFile.files);

                        // Вставляем input в ячейку
                        linkCell.appendChild(inputFile);
                    }
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
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ itemId })
            });

            const result = await response.json();

            if (response.ok) {
        const row = document.querySelector(`tr[data-id="${itemId}"]`);
        if (row) {
            console.log(row.innerHTML);
            // Найти ячейку по классу
            let photoLink = row.querySelector('a[href*="video_path"]');
            if (photoLink) {
                // Скрыть кнопку внутри ссылки
                 const buttonInside = row.querySelector('.delete-file-btn_video');
                if (buttonInside) {
                    buttonInside.style.display = 'none'; // скрываем кнопку
                }

                photoLink.innerHTML = '';
                const inputFile = document.createElement('input');
                inputFile.type = 'file';
                inputFile.className = 'video-cell'
                inputFile.accept = '.mp4';
                inputFile.multiple = true;
                inputFile.onchange = () => uploadFile(itemId, inputFile.files);

                // Вставить ссылку в ячейку
                photoLink.appendChild(inputFile);
            }
            }


        } else {
            alert('Ошибка: ' + result.message);
        }
    } catch (e) {
        console.error(e);
        alert('Ошибка при удалении файла');
    }
}

async function deleteFilePhoto(itemId) {
    const token = localStorage.getItem('access_token');

    if (!confirm('Вы уверены, что хотите удалить файл?')) return;

    try {
        const response = await fetch('/files/delete_photo', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ itemId })
        });

        const result = await response.json();

        if (response.ok) {
            const row = document.querySelector(`tr[data-id="${itemId}"]`);
            if (row) {

                // Найти ячейку по классу
                let photoLink = row.querySelector('a[href*="photo_path"]');
                if (photoLink) {
                    // Скрыть кнопку внутри ссылки
                     const buttonInside = row.querySelector('.delete-file-btn_photo');
                    if (buttonInside) {
                        buttonInside.style.display = 'none'; // скрываем кнопку
                    }

                    photoLink.innerHTML = '';
                    const inputFile = document.createElement('input');
                    inputFile.type = 'file';
                    inputFile.className = 'photo-cell'
                    inputFile.accept = '.jpeg,.png';
                    inputFile.multiple = true;
                    inputFile.onchange = () => uploadFilePhoto(itemId, inputFile.files);

                    // Вставить ссылку в ячейку
                    photoLink.appendChild(inputFile);
                }
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
        const container = document.createElement('div');

        if (fileType === 'акт') {
            // Для 'акт' — ссылка или кнопка загрузки
            if (item[fileType][0]) {
                const link = document.createElement('a');
                link.href = `open_files?files_id=${item.id}&status_file=act_path`;
                link.target = '_blank';
                link.textContent = 'Открыть акт';

                container.appendChild(link);

                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Удалить';
                deleteBtn.className = 'delete-file-btn_act';
                deleteBtn.dataset.id = item.id;
                deleteBtn.dataset.type = 'акт';

                deleteBtn.addEventListener('click', () => {
                    deleteFileAct(item.id);
                });

                container.appendChild(deleteBtn);
            } else {
                const inputFile = document.createElement('input');
                inputFile.type = 'file';
                inputFile.accept = '.pdf';
                inputFile.onchange = () => uploadFileAct(item.id, inputFile.files);
                container.appendChild(inputFile);
            }
        } else if (fileType === 'фото') {
            // Для фото — кнопка для загрузки
            if (item['фото']) {
                const link = document.createElement('a');
                link.href = `open_files?files_id=${item.id}&status_file=photo_path`;
                link.target = '_blank';
                link.textContent = 'Открыть фото';

                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Удалить';
                deleteBtn.className = 'delete-file-btn_photo';
                deleteBtn.dataset.id = item.id;
                deleteBtn.dataset.type = 'фото';

                deleteBtn.addEventListener('click', () => {
                    deleteFilePhoto(item.id);
                });

                container.appendChild(link);
                container.appendChild(deleteBtn)
            } else {
                const inputFile = document.createElement('input');
                inputFile.type = 'file';
                inputFile.className = 'photo-cell'
                inputFile.accept = '.jpeg,.png';
                inputFile.multiple = true;
                inputFile.onchange = () => uploadFilePhoto(item.id, inputFile.files);
                container.appendChild(inputFile);
            }
        } else if (fileType === 'видео') {
            // Для видео — ссылка или кнопка загрузки
            if (item['видео']) {
                const link = document.createElement('a');
                link.href = `open_files?files_id=${item.id}&status_file=video_path`;
                link.target = '_blank';
                link.textContent = 'Открыть видео';

                container.appendChild(link);

                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Удалить';
                deleteBtn.className = 'delete-file-btn_video';
                deleteBtn.dataset.id = item.id;
                deleteBtn.dataset.type = 'видео';

                deleteBtn.addEventListener('click', () => deleteFileVideo(item.id));

                container.appendChild(deleteBtn);
            } else {
                const inputFile = document.createElement('input');
                inputFile.type = 'file';
                inputFile.accept = '.mp4,.3gp';
                inputFile.multiple = true;
                inputFile.onchange = () => uploadFile(item.id, inputFile.files);
                container.appendChild(inputFile);
            }
        }

        return container;
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
            window.location.reload(); // или обновить конкретную ячейку
        } else {
            alert('Ошибка при отправке файла: ' + result.message);
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
            window.location.reload(); // или обновить конкретную ячейку

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
                console.log(row)
                const photoLink = row.querySelector('a[href*="photo_path"]');
                if (photoLink) {
                    // Очищаем содержимое ссылки
                    photoLink.innerHTML = '';

                    // Обновляем href для открытия файла
                    photoLink.href = `open_files?files_id=${itemId}&status_file=photo_path`;
                    photoLink.target = '_blank'; // открыть в новой вкладке
                    photoLink.textContent = 'Открыть фото';

                    // Создаем кнопку удаления, если еще не создана
                    let deleteBtn = row.querySelector('.delete-file-btn_photo');
                    if (deleteBtn) {
                        deleteBtn.style.display = 'flex'; // или 'block', если нужно
                    }

                    // Вставляем кнопку рядом с ссылкой
                    photoLink.parentNode.insertBefore(deleteBtn, photoLink.nextSibling);

                    console.log((photoLink))
                        // row.querySelector('td').appendChild(photoLink);
                } else {
                    // Если ссылки нет, можно создать новую
                    const newLink = document.createElement('a');
                    newLink.href = `open_files?files_id=${itemId}&status_file=photo_path`;
                    newLink.target = '_blank';
                    newLink.textContent = 'Открыть фото';

                    row.querySelector('td').appendChild(newLink);

                    // Создаем кнопку удаления
                    const deleteBtn = document.createElement('button');
                    deleteBtn.className = 'delete-file-btn_photo';
                    deleteBtn.dataset.id = itemId;
                    deleteBtn.dataset.type = 'фото';
                    deleteBtn.textContent = 'Удалить';

                    deleteBtn.addEventListener('click', () => {
                        deleteFilePhoto(itemId);
                    });

                    row.querySelector('td').appendChild(deleteBtn);
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


