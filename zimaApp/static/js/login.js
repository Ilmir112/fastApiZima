// =================== Обработка формы входа ===================
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        loginUser();
    });
}

// =================== Вход пользователя ===================
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
            window.location.href = '/pages/home';
        } else {
            const errorText = await response.text();
            alert('Ошибка входа: ' + errorText);
        }
    } catch (error) {
        alert('Ошибка сети: ' + error);
    }
}

// =================== Выход из системы ===================
function showLogoutButton(show) {
    const logoutItem = document.getElementById('logoutItem');
    if (logoutItem) {
        logoutItem.classList.toggle('d-none', !show);
        if (show && !logoutItem.hasListener) {
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', () => {
                    localStorage.removeItem('access_token');
                    window.location.href = '/pages/login';
                });
                logoutItem.hasListener = true; // чтобы не навешивать повторно
            }
        }
    }
}

// =================== Проверка авторизации ===================
function getToken() {
    return localStorage.getItem('access_token');
}

function removeToken() {
    localStorage.removeItem('access_token');
}

async function checkAuth() {
    const token = getToken();
    if (!token) {
        alert('Пожалуйста, войдите в систему.');
        // window.location.href = '/pages/login';
        return false;
    }

    // Проверка срока действия JWT
    const payloadBase64 = token.split('.')[1];
    if (!payloadBase64) {
        removeToken();
        window.location.href = '/pages/login';
        return false;
    }

    try {
        const payloadJson = atob(payloadBase64);
        const payload = JSON.parse(payloadJson);
        const currentTime = Math.floor(Date.now() / 1000);

        if (payload.exp && payload.exp < currentTime) {
            alert('Время сессии истекло. Пожалуйста, войдите заново.');
            removeToken();
            window.location.href = '/pages/login';
            return false;
        }
    } catch (e) {
        removeToken();
        window.location.href = '/pages/login';
        return false;
    }

    return true;
}

// =================== Навигация по страницам ===================
async function loadPage(path) {
    const token = getToken();

    // Получаем контейнеры
    const loginContainer = document.getElementById('login-container');
    const contentContainer = document.getElementById('content');

    // Обработка для страницы логина
    if (path === '/pages/login') {
        if (await checkAuth()) {
            // Уже авторизован — редирект на домашнюю
            window.location.reload();
            return;
        }
        // Нет токена — показываем форму входа
        if (loginContainer) loginContainer.style.display = 'block';
        if (contentContainer) contentContainer.style.display = 'none';

        showLogoutButton(false);
        return;
    }

    // Для остальных страниц
    showLogoutButton(true);

    if (path === '/pages/home') {
        if (!(await checkAuth())) return;

        try {
            const response = await fetch('/pages/home', {headers: {'Authorization': `Bearer ${token}`}});
            if (response.ok) {
                const htmlContent = await response.text();
                if (contentContainer) {
                    // contentContainer.innerHTML = htmlContent;
                    contentContainer.style.display = 'block';
                }
                if (loginContainer) loginContainer.style.display = 'none';
            } else {
                alert('Пожалуйста, войдите в систему.');
                localStorage.removeItem('access_token');
                window.location.href = '/pages/login';
            }
        } catch (e) {
            alert('Ошибка при загрузке домашней страницы: ' + e);
        }

// Обработка других страниц с ограниченным доступом
    } else if (
        path === '/pages/profile' ||
        path === '/pages/settings' ||
        path === '/pages/login'
        // добавьте сюда нужные пути
    ) {

        if (!(await checkAuth())) return;

        try {
            const response = await fetch(path, {headers: {'Authorization': `Bearer ${token}`}});
            if (response.ok) {
                const htmlContent = await response.text();
                // Можно вставлять контент или делать дополнительные действия
                // Например:
                // contentContainer.innerHTML=htmlContent;
            } else {
                alert('Пожалуйста, войдите в систему.');
                localStorage.removeItem('access_token');
                window.location.href = '/pages/login';
            }
        } catch (e) {
            alert('Ошибка при загрузке страницы: ' + e);
        }

    } else {
        // Обработка других страниц по необходимости
    }
}

// =================== Обработка DOMContentLoaded ===================
document.addEventListener('DOMContentLoaded', () => {

    // Обработка кнопки выхода/аккаунта
    showLogoutButton(true);

    // Загрузка текущей страницы
    loadPage(window.location.pathname);

    // Обработчик для кнопки "Редактировать" профиля
    const editBtnProfile = document.getElementById('editBtn');
    if (editBtnProfile) {
        editBtnProfile.addEventListener('click', () => setEditMode());
    }

    // Обработчик для кнопки "Сохранить" профиля
    const saveBtnProfile = document.getElementById('saveBtn');
    if (saveBtnProfile) {
        saveBtnProfile.addEventListener('click', async () => await saveProfile());
    }

    // Обработчик для открытия модального окна аккаунта
    const showAccountBtn = document.getElementById('showAccountInfo');
    if (showAccountBtn) {
        showAccountBtn.addEventListener('click', showAccountInfo);
    }

    // Обработчик закрытия модального окна
    const closeBtn = document.getElementById('closeAccountModal');
    if (closeBtn) {
        closeBtn.onclick = () => closeAccountModal();
    }

    // Окрытие по клику на overlay
    const overlay = document.getElementById('accountModalOverlay');
    if (overlay) {
        overlay.onclick = () => closeAccountModal();
    }

});

// =================== Модальное окно профиля ===================
const accountModal = document.getElementById("accountModal");
const overlay = document.getElementById("accountModalOverlay");
const closeModalBtn = document.getElementById("closeAccountModal");
const showAccountInfoBtn = document.getElementById("showAccountInfo");

// Поля профиля и их элементы
const fields = [
    {
        displayId: 'userLoginDisplay',
        inputId: 'userLoginInput',
        key: 'login_user'
    },
    {
        displayId: 'userSecondNameDisplay',
        inputId: 'userSecondNameInput',
        key: 'second_name'
    },
    {
        displayId: 'userSurnameDisplay',
        inputId: 'userSurnameInput',
        key: 'surname_user'
    },
    {
        displayId: 'userNameDisplay',
        inputId: 'userNameInput',
        key: 'name_user'
    },
    {
        displayId: 'userPositionDisplay',
        inputId: 'userPositionInput',
        key: 'position_id'
    },
    {
        displayId: 'userCustomerDisplay',
        inputId: 'userCustomerInput',
        key: 'costumer'
    },
    {
        displayId: 'userContractorDisplay',
        inputId: 'userContractorInput',
        key: 'contractor'
    },
    {
        displayId: 'userCtcrsDisplay',
        selectId: 'userCtcrsSelect',
        key: 'ctcrs'
    },
    {
        displayId: 'passwordDisplay',
        inputId: 'passwordInput',
        key: 'password'
    }
];

// Текущие данные пользователя
let currentUserData = {};

// Получение данных пользователя и отображение в модальном окне
async function showAccountInfo() {
    try {
        const response = await fetch('/auth/me');
        if (!response.ok) throw new Error(`Ошибка сети: ${response.status}`);
        currentUserData = await response.json();

        fields.forEach(field => {
            const value = currentUserData[field.key] || '';

            if (field.selectId) {
                const spanElem = document.getElementById(field.displayId);
                const selectElem = document.getElementById(field.selectId);
                spanElem.textContent = value;
                selectElem.value = value;
            } else {
                document.getElementById(field.displayID).textContent = value; // исправлено на displayID
                document.getElementById(field.inputID).value = value;     // исправлено на inputID
            }
        });
        notification.innerText = 'Данные успешно загружены!';
        setViewMode();

        // Показываем окно
        if (accountModal && overlay) {
            accountModal.style.display = 'block';
            overlay.style.display = 'block';
        }

    } catch (e) {
        alert("Не удалось получить данные пользователя.");
        console.error(e);
    }
}

// Установка режима просмотра профиля
function setViewMode() {
    fields.forEach(field => {
            const displayElem = document.getElementById(field.displayId);
            const inputElem = document.getElementById(field.inputId);
            const selectElem = document.getElementById(field.selectId);

            if (!displayElem) return;

            if (field.key === 'password') {
                displayElem.style.display = '';
                if (inputElem) {
                    inputElem.style.display = 'none';
                }
                if (selectElem) {
                    selectElem.style.display = 'none';
                }
            } else if (field.selectId) {
                displayElem.style.display = '';
                if (selectElem) {
                    selectElem.style.display = 'none';
                }
            }
        }
    )
}


// Получение элементов
const modal = document.getElementById('registerModal');
const openBtn = document.getElementById('openRegisterBtn');
const closeBtn = document.getElementById('closeModal');
const organizationSelect = document.getElementById('organization');
const regionLabel = document.getElementById('regionLabel');
const regionSelect = document.getElementById('regionOrExpedition');
const form = document.getElementById('registerForm');

// Открытие модального окна
openBtn.onclick = () => {
    modal.style.display = 'block';
};

// Закрытие модального окна
closeBtn.onclick = () => {
    modal.style.display = 'none';
};

// Закрытие при клике вне окна
window.onclick = (event) => {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};

// Обновление опций региона/экспедиции в зависимости от выбранной организации
organizationSelect.onchange = () => {
    const selectedOrg = organizationSelect.value;

    regionSelect.innerHTML = ''; // очистить текущие опции

    if (selectedOrg === 'ООО Ойл-сервис') {
        // Установка для ЦЕХ
        regionLabel.textContent = 'ЦЕХ:';
        const regions = ['АУП', 'ЦТКРС №1', 'ЦТКРС №2', 'ЦТКРС №3', 'ЦТКРС №4', 'ЦТКРС №5', 'ЦТКРС №6', 'ЦТКРС №7'];
        regions.forEach(r => {
            const option = document.createElement('option');
            option.value = r;
            option.textContent = r;
            regionSelect.appendChild(option);
        });
    } else if (selectedOrg === 'ООО РН-Сервис') {
        // Установка для экспедиций
        regionLabel.textContent = 'Экспедиция:';
        const expeditions = ['АУП','экспедиции №1', 'экспедиции №2', 'экспедиции №3', 'экспедиции №4', 'экспедиции №5', 'экспедиции №6', 'экспедиции №7'];
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
    const loginUser = document.getElementById('loginUser').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const firstName = document.getElementById('firstName').value.trim();
    const secondName = document.getElementById('secondName').value.trim();
    const position = document.getElementById('position').value.trim();
    const organization = document.getElementById('organization').value.trim();
    const consumer = document.getElementById('consumer').value.trim();
    const region = document.getElementById('regionOrExpedition').value.trim();
    const password = document.getElementById('password').value.trim();
    const password2 = document.getElementById('password2').value.trim();

    if (password !== password2) {
        alert("Пароли не совпадают");
        return;
    }

    // Здесь можно отправлять данные на сервер или обрабатывать их далее
    // Например, через fetch:


    const dataToSend = {
        login_user: loginUser,
        name_user: firstName,
        surname_user: lastName,
        second_name: secondName,
        position_id: position + " " + region,
        costumer: consumer,
        contractor: organization,
        ctcrs: region,
        password: password

    };

// Пример отправки данных (замените URL на ваш API)
    fetch('/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dataToSend)
    })
        .then(res => res.json())
        .then(data => {
            if (data) {
                alert("Пользователь успешно зарегистрирован");
                modal.style.display = 'none'; // закрыть окно
            } else if (data.error === 'exists') {
                alert("Данный пользователь уже существует");
            } else {
                alert("Произошла ошибка");
            }
        })
        .catch(() => alert("Ошибка сети"));

// Можно также добавить обработку ошибок и более сложную логику.
};

