// Обработка формы входа
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        loginUser();
    });
}

// Функция для входа пользователя
async function loginUser() {
    const loginInput = document.getElementById('login_user');
    const passwordInput = document.getElementById('password');

    if (!loginInput || !passwordInput) {
        alert('Элементы формы не найдены.');
        return;
    }

    const loginUserValue = loginInput.value;
    const password = passwordInput.value;

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({login_user: loginUserValue, password: password})
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            // После входа — редирект на домашнюю страницу
            window.location.href = '/pages/home';
        } else {
            const errorText = await response.text();
            alert('Ошибка входа: ' + errorText);
        }
    } catch (error) {
        alert('Ошибка сети: ' + error);
    }
}

// Функция для показа/скрытия кнопки выхода
function showLogoutButton(show) {
    const logoutItem = document.getElementById('logoutItem');
    if (logoutItem) {
        logoutItem.classList.toggle('d-none', !show);
        // Навешиваем обработчик один раз при показе
        if (show && !logoutItem.hasListener) {
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', () => {
                    localStorage.removeItem('access_token');
                    // Можно перезагрузить страницу или редиректить
                    window.location.href = '/pages/login';
                });
                logoutItem.hasListener = true; // чтобы не навешивать повторно
            }
        }
    }
}

// Обработка загрузки страницы
window.addEventListener('load', async () => {
    const path = window.location.pathname;
    const token = localStorage.getItem('access_token');

    // Получаем общие элементы
    const loginContainer = document.getElementById('login-container');
    const contentContainer = document.getElementById('content');

    showLogoutButton(true);
    if (loginContainer) loginContainer.style.display = 'none';

    // Функция для проверки авторизации
    async function checkAuth() {
        if (!token) {
            // Нет токена — перенаправляем или показываем логин
            alert('Пожалуйста, войдите в систему.');
            window.location.href = '/pages/login';
            return false;
        }
        // Можно дополнительно проверить валидность токена на сервере, если нужно
        return true;
    }

    if (path === '/pages/login') {

        // Страница логина
        if (token) {
            // Уже есть токен — редирект на домашнюю страницу
            window.location.href = '/pages/home';
            return;
        }
        // Нет токена — показываем форму входа
        if (loginContainer) loginContainer.style.display = 'block';
        if (contentContainer) contentContainer.style.display = 'none';

        showLogoutButton(false);

    } else if (path === '/pages/home' || path.startsWith('/pages/')) {
        // Страница домашней страницы
        if ((await checkAuth())) return;

        try {
            const response = await fetch('/pages/home', {
                headers: {'Authorization': `Bearer ${token}`}
            });

            if (response.ok) {
                const htmlContent = await response.text();
                if (contentContainer) {
                    contentContainer.innerHTML = htmlContent;
                    contentContainer.style.display = 'block';
                }
                showLogoutButton(true);
                if (loginContainer) loginContainer.style.display = 'none';

            } else {
                alert('Пожалуйста, войдите в систему.');
                localStorage.removeItem('access_token');
                window.location.href = '/pages/login';
            }
        } catch (error) {
            alert('Ошибка при загрузке домашней страницы: ' + error);
        }

    } else if (path === '/pages/profile' || path === '/pages/settings'  // добавьте сюда нужные пути
    ) {
        // Для других страниц с ограниченным доступом
        if (!(await checkAuth())) return;

        // Можно делать дополнительные запросы или показывать контент
        try {
            const response = await fetch(path, {
                headers: {'Authorization': `Bearer ${token}`}
            });
            if (response.ok) {
                const htmlContent = await response.text();
                if (contentContainer) {
                    // contentContainer.innerHTML = htmlContent;
                    // contentContainer.style.display = 'block';
                }
                showLogoutButton(true);
                if (loginContainer) loginContainer.style.display = 'none';
            } else {
                alert('Пожалуйста, войдите в систему.');
                localStorage.removeItem('access_token');
                window.location.href = '/pages/login';
            }
        } catch (error) {
            alert('Ошибка при загрузке страницы: ' + error);
        }

    } else {
        // Для остальных страниц — можно оставить как есть или добавить обработку по необходимости
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const accountModal = document.getElementById('accountModal');
    const overlay = document.getElementById('accountModalOverlay');
    const closeBtn = document.getElementById('closeAccountModal');
    const showAccountBtn = document.getElementById('showAccountInfo');


    // Кнопки редактирования и сохранения
    const editBtn = document.getElementById('editBtn');
    const saveBtn = document.getElementById('saveBtn');
    const passwordSection = document.getElementById('passwordSection');
    const notification = document.getElementById('notification');

    editBtn.addEventListener('click', () => {
        // Показываем поля для пароля
        passwordSection.style.display = 'flex';
        // Меняем кнопки
        editBtn.style.display = 'none';
        saveBtn.style.display = 'inline-block';
        // Очистка уведомлений
        notification.innerText = '';
    });

    saveBtn.addEventListener('click', () => {
        const password = document.getElementById('passwordInput').value;
        const confirmPassword = document.getElementById('confirmPasswordInput').value;

        if (password !== confirmPassword) {
            notification.innerText = 'Пароли не совпадают!';
            return;
        }

        // Если пароли совпадают, можно продолжить сохранение данных
        // Например, скрыть секцию и вернуть кнопки в исходное состояние
        passwordSection.style.display = 'none';
        editBtn.style.display = 'inline-block';
        saveBtn.style.display = 'none';


        // Можно добавить сюда логику сохранения данных


    });

    // Поля отображения и ввода
    const fields = [{
        displayId: 'userLoginDisplay',
        inputId: 'userLoginInput',
        key: 'login_user'
    }, {
        displayId: 'userSecondNameDisplay',
        inputId: 'userSecondNameInput',
        key: 'second_name'
    }, {
        displayId: 'userSurnameDisplay',
        inputId: 'userSurnameInput',
        key: 'surname_user'
    }, {displayId: 'userNameDisplay', inputId: 'userNameInput', key: 'name_user'}, {
        displayId: 'userPositionDisplay',
        inputId: 'userPositionInput',
        key: 'position_id'
    }, {
        displayId: 'userCustomerDisplay',
        inputId: 'userCustomerInput',
        key: 'costumer'
    }, {
        displayId: 'userContractorDisplay',
        inputId: 'userContractorInput',
        key: 'contractor'
    }, {displayId: 'userCtcrsDisplay', selectId: 'userCtcrsSelect', key: 'ctcrs'}, {
        displayId: 'passwordInput',
        inputId: 'passwordInput',
        key: 'password'
    }
        // добавьте остальные поля по необходимости
    ];

    let currentUserData = {}; // хранит текущие данные пользователя

    async function showAccountInfo() {
        try {
            const response = await fetch('/auth/me');
            if (!response.ok) throw new Error(`Ошибка сети: ${response.status}`);
            currentUserData = await response.json();

            // Заполняем поля
            fields.forEach(field => {
                const value = currentUserData[field.key] || '';
                if (field.selectId) {
                    const spanElem = document.getElementById(field.displayId);
                    const selectElem = document.getElementById(field.selectId);
                    spanElem.textContent = value;
                    selectElem.value = value;
                } else {
                    document.getElementById(field.displayId).textContent = value;
                    document.getElementById(field.inputId).value = value;
                }
            });
            notification.innerText = 'Данные успешно сохранены!';
            // Переключение в режим просмотра
            setViewMode();

            // Показываем окно
            if (accountModal && overlay) {
                accountModal.style.display = 'block';
                overlay.style.display = 'block';
            }
        } catch (error) {
            alert('Не удалось получить данные пользователя.');
            console.error(error);
        }
    }

    function setViewMode() {
        fields.forEach(field => {
            // Обеспечиваем, что DOM-элементы существуют
            const displayElem = document.getElementById(field.displayId);
            const inputElem = document.getElementById(field.inputId);
            const selectElem = document.getElementById(field.selectId);

            if (!displayElem) return; // пропускаем, если элемента нет

            if (field.key === 'password') {
                // В режиме просмотра скрываем поле ввода пароля
                displayElem.style.display = '';
                if (inputElem) inputElem.style.display = 'none';
            } else if (field.selectId) {
                // Для полей с select: показываем display, скрываем select и input
                displayElem.style.display = '';
                if (selectElem) selectElem.style.display = 'none';
                if (inputElem) inputElem.style.display = 'none';
            } else if (field.displayId) {
                // Для других полей: показываем display, скрываем input
                displayElem.style.display = '';
                if (inputElem) inputElem.style.display = 'none';
            }
        });

        // Обновляем кнопки
        document.getElementById('editBtn').style.display = '';
        document.getElementById('saveBtn').style.display = 'none';
    }

    function setEditMode() {
        fields.forEach(field => {
            if (field.selectId) {
                // Для ctcrs показываем select, скрываем span
                document.getElementById(field.displayId).style.display = 'none';
                document.getElementById(field.selectId).style.display = '';
            } else {
                document.getElementById(field.displayId).style.display = 'none';
                document.getElementById(field.inputId).style.display = '';
            }
        });
        document.getElementById('editBtn').style.display = 'none';
        document.getElementById('saveBtn').style.display = '';
    }

// Обработчик кнопки "Редактировать"
    document.getElementById('editBtn').addEventListener('click', () => {
        setEditMode();
    });

// Обработчик кнопки "Сохранить"
    document.getElementById('saveBtn').addEventListener('click', async () => {
        const updatedData = {};
        const token = localStorage.getItem('access_token');
        fields.forEach(field => {
            if (field.selectId) {
                // Значение из select
                updatedData[field.key] = document.getElementById(field.selectId).value;
            } else {
                updatedData[field.key] = document.getElementById(field.inputId).value;
            }
        });

        try {
            const response = await fetch('/auth/update', { // предполагаемый API для обновления
                method: 'POST', headers: {
                    'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`
                }, body: JSON.stringify(updatedData)
            });
            if (!response.ok) throw new Error(`Ошибка при сохранении: ${response.status}`);

            // Обновляем отображение после успешного сохранения
            Object.assign(currentUserData, updatedData);
            fields.forEach(field => {
                if (field.selectId) {
                    document.getElementById(field.displayId).textContent = updatedData[field.key];
                } else {
                    document.getElementById(field.displayId).textContent = updatedData[field.key];
                }
            });
            setViewMode();
            alert('Данные успешно сохранены.');
        } catch (error) {
            alert('Ошибка при сохранении данных.');
            console.error(error);
        }
    });
// Остальной код по открытию/закрытию окна
    if (showAccountBtn) {
        showAccountBtn.addEventListener('click', showAccountInfo);
    }

    if (closeBtn) {
        closeBtn.onclick = () => {
            if (accountModal && overlay) {
                accountModal.style.display = 'none';
                overlay.style.display = 'none';
            }
        };
    }

    if (overlay) {
        overlay.onclick = () => {
            if (accountModal && overlay) {
                accountModal.style.display = 'none';
                overlay.style.display = 'none';
            }
        };
    }
});


document.addEventListener('DOMContentLoaded', () => {
    // Получение элементов
    const modalRegistration = document.getElementById('registerModal');
    modalRegistration.style.position = 'fixed'; // или 'absolute', если нужно
    modalRegistration.style.zIndex = '9999';
    const openBtn = document.getElementById('openRegisterBtn');
    const closeBtn = document.getElementById('closeModal');
    const organizationSelect = document.getElementById('organization');
    const regionLabel = document.getElementById('regionLabel');
    const regionSelect = document.getElementById('regionOrExpedition');
    const form = document.getElementById('registerForm');
    const loginContainer = document.getElementById('login-container');
    loginContainer.style.display= 'none';



    // Открытие модального окна
    openBtn.onclick = () => {
        modalRegistration.style.display = 'block';
    };

    // Закрытие модального окна
    closeBtn.onclick = () => {
        modalRegistration.style.display = 'none';
    };

    // Закрытие при клике вне окна
    window.onclick = (event) => {
        if (event.target == modalRegistration) {
            modalRegistration.style.display = 'none';
        }
    };

    // Обновление опций региона/экспедиции в зависимости от выбранной организации
    organizationSelect.onchange = () => {
        const selectedOrg = organizationSelect.value;

        regionSelect.innerHTML = ''; // очистить текущие опции

        if (selectedOrg === 'ООО Ойл-сервис') {
            // Установка для ЦЕХ
            regionLabel.textContent = 'ЦЕХ:';
            const regions = ['ЦТКРС №1', 'ЦТКРС №2', 'ЦТКРС №3', 'ЦТКРС №4', 'ЦТКРС №5', 'ЦТКРС №6', 'ЦТКРС №7'];
            regions.forEach(r => {
                const option = document.createElement('option');
                option.value = r;
                option.textContent = r;
                regionSelect.appendChild(option);
            });
        } else if (selectedOrg === 'ООО РН-Сервис') {
            // Установка для экспедиций
            regionLabel.textContent = 'Экспедиция:';
            const expeditions = ['экспедиции №1', 'экспедиции №2', 'экспедиции №3', 'экспедиции №4', 'экспедиции №5', 'экспедиции №6', 'экспедиции №7'];
            expeditions.forEach(e => {
                const option = document.createElement('option');
                option.value = e;
                option.textContent = e;
                regionSelect.appendChild(option);
            });
        } else {
            // Если ничего не выбрано
            const option = document.createElement('option');
            option.value = '';
            option.textContent = '--Выберите--';
            regionSelect.appendChild(option);
        }
    };

    // Обработка отправки формы
    form.onsubmit = (e) => {
        e.preventDefault();

        // Получение данных формы
        const loginUser = document.getElementById("loginUser").value.trim();
        const lastName = document.getElementById('lastName').value.trim();
        const firstName = document.getElementById('firstName').value.trim();
        const secondName = document.getElementById('secondName').value.trim();
        const position = document.getElementById('position').value.trim();
        const organization = document.getElementById('organization').value.trim();
        const consumer = document.getElementById('consumer').value.trim();
        const region = document.getElementById('regionOrExpedition').value.trim();
        const password1 = document.getElementById('password_1').value.trim();
        const password2 = document.getElementById('password2').value.trim();


        if (password1 !== password2) {
            alert("Пароли не совпадают");
            return;
        }

        // Здесь можно отправлять данные на сервер или обрабатывать их далее
        // Например, через fetch:
        // login_user, name_user, surname_user, second_name, position_id, costumer,
        const dataToSend = {
            login_user: loginUser,
            surname_user: lastName,
            name_user: firstName,
            second_name: secondName,
            position_id: position + " " + region,
            contractor: organization,
            costumer: consumer,
            password: password1,
            ctcrs: region
        };

        fetch('/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(dataToSend)
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    // modalRegistration.style.display = 'none'; // закрыть окно
                    // Можно добавить очистку формы или других действий
                } else if (data.status === 409) {
                    alert("Данный пользователь уже существует");
                } else {
                    alert("Произошла ошибка: " + (data.message || 'Неизвестная ошибка'));
                }
            })
            .catch(() => alert("Ошибка сети"));

        // Можно также добавить обработку ошибок и более сложную логику.
    };

})

// Открытие окна регистрации
document.getElementById('openRegisterBtn').addEventListener('click', () => {
    document.getElementById('registerModal').style.display = 'flex';
    document.getElementById('loginForm').style.display = 'none';


});

// Закрытие окна регистрации
document.getElementById('closeModal').addEventListener('click', () => {
    document.getElementById('registerModal').style.display = 'none';
    document.getElementById('loginForm').style.display = 'flex';
    window.location.reload();
});