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
    const token = localStorage.getItem('access_token');
    console.log('getToken: Возвращает:', token);
    return token;
}

function removeToken() {
    localStorage.removeItem('access_token');
    console.log('removeToken: Токен удален.');
}

async function checkAuth(redirectToLogin = true) {
    const token = getToken();
    console.log('checkAuth: Токен:', token ? 'Присутствует' : 'Отсутствует', ' (redirectToLogin:', redirectToLogin, ')');

    // Если токена нет
    if (!token) {
        console.warn('checkAuth: Токен отсутствует.');
        // Если мы уже на странице логина, не перенаправляем, просто возвращаем false
        if (window.location.pathname === '/pages/login') {
            return false;
        }
        if (redirectToLogin) {
            window.location.href = '/pages/login';
        }
        return false;
    }

    // Проверка срока действия JWT
    const payloadBase64 = token.split('.')[1];
    console.log('checkAuth: payloadBase64:', payloadBase64);

    if (!payloadBase64) {
        console.error('checkAuth: Недействительный формат токена: отсутствует payloadBase64');
        removeToken();
        if (redirectToLogin) {
            window.location.href = '/pages/login';
        }
        return false;
    }

    try {
        const payloadJson = atob(payloadBase64);
        const payload = JSON.parse(payloadJson);
        const currentTime = Math.floor(Date.now() / 1000);

        console.log('checkAuth: payload.exp:', payload.exp);
        console.log('checkAuth: currentTime:', currentTime);

        if (payload.exp && payload.exp < currentTime) {
            console.warn('checkAuth: Токен истек.');
            removeToken();
            if (redirectToLogin) {
                window.location.href = '/pages/login';
            }
            return false;
        }
    } catch (e) {
        console.error('checkAuth: Ошибка при декодировании или парсинге токена:', e);
        removeToken();
        if (redirectToLogin) {
            window.location.href = '/pages/login';
        }
        return false;
    }

    console.log('checkAuth: Токен действителен.');
    return true;
}

// =================== Навигация по страницам ===================
async function loadPage(path) {
    console.log('loadPage: Загрузка страницы:', path);
    // Получаем контейнеры
    const loginContainer = document.getElementById('login-container');
    const contentContainer = document.getElementById('content');

    // Если это не страница логина, проверяем авторизацию с перенаправлением
    if (path !== '/pages/login') {
        console.log('loadPage: Страница не логина, проверка авторизации...');
        if (!(await checkAuth(true))) { // Передаем true, чтобы checkAuth перенаправил
            console.log('loadPage: checkAuth вернул false, остановка загрузки страницы.');
            return;
        }
        // Если авторизация успешна, убедимся, что контейнер входа скрыт
        if (loginContainer) loginContainer.style.display = 'none';
    }

    // Обработка для страницы логина
    if (path === '/pages/login') {
        console.log('loadPage: Страница логина.');
        // На странице логина вызываем checkAuth без перенаправления, чтобы избежать циклов
        if (await checkAuth(false)) { // Передаем false
            console.log('loadPage: Авторизован на странице логина, редирект на домашнюю.');
            window.location.reload(); // или window.location.href = '/pages/home';
            return;
        }
        // Логика отображения формы входа перенесена в DOMContentLoaded
        // if (loginContainer) loginContainer.style.display = 'block';
        // if (contentContainer) contentContainer.style.display = 'none';

        // showLogoutButton(false);
        return;
    }

    // Для остальных страниц (если мы сюда дошли, значит checkAuth была успешна)
    console.log('loadPage: Страница авторизована, продолжение...');
    showLogoutButton(true);
    // loginContainer уже скрыт выше

    if (path === '/pages/home') {
        console.log('loadPage: Загрузка домашней страницы.');
        try {
            const response = await fetch('/pages/home', {headers: {'Authorization': `Bearer ${getToken()}`}});
            if (response.ok) {
                const htmlContent = await response.text();
                if (contentContainer) {
                    // contentContainer.innerHTML = htmlContent;
                    contentContainer.style.display = 'block';
                }
            } else {
                console.warn('loadPage: Ошибка при загрузке домашней страницы, перенаправление на логин.', response.status);
                localStorage.removeItem('access_token');
                window.location.href = '/pages/login';
            }
        } catch (e) {
            console.error('loadPage: Ошибка сети при загрузке домашней страницы:', e);
            localStorage.removeItem('access_token');
            window.location.href = '/pages/login';
        }

// Обработка других страниц с ограниченным доступом
    } else if (
        path === '/pages/profile' ||
        path === '/pages/settings' ||
        path === '/pages/login' // Эта строка, вероятно, лишняя, так как обрабатывается выше
        // добавьте сюда нужные пути
    ) {
        console.log('loadPage: Загрузка страницы с ограниченным доступом:', path);

        try {
            const response = await fetch(path, {headers: {'Authorization': `Bearer ${getToken()}`}});
            if (response.ok) {
                const htmlContent = await response.text();
            } else {
                console.warn('loadPage: Ошибка при загрузке страницы, перенаправление на логин.', response.status);
                localStorage.removeItem('access_token');
                window.location.href = '/pages/login';
            }
        } catch (e) {
            console.error('loadPage: Ошибка сети при загрузке страницы:', e);
            localStorage.removeItem('access_token');
            window.location.href = '/pages/login';
        }

    } else {
        console.log('loadPage: Обработка других страниц.');
        // Обработка других страниц по необходимости
    }
}

// =================== Обработка DOMContentLoaded ===================
document.addEventListener('DOMContentLoaded', async () => {

    console.log('DOMContentLoaded: Событие вызвано.');
    const currentPageIsLogin = window.location.pathname === '/pages/login';
    console.log('DOMContentLoaded: Текущая страница - логин:', currentPageIsLogin);
    
    // Проверяем авторизацию в первую очередь
    if (!(await checkAuth(!currentPageIsLogin))) { // Если не страница логина, то перенаправляем
        console.log('DOMContentLoaded: checkAuth вернул false, остановка дальнейшего выполнения.');
        // Если мы на странице логина и токена нет, показываем форму входа
        if (currentPageIsLogin) {
            const loginContainer = document.getElementById('login-container');
            const contentContainer = document.getElementById('content');
            if (loginContainer) loginContainer.style.display = 'block';
            if (contentContainer) contentContainer.style.display = 'none';
            showLogoutButton(false);
        }
        return;
    }

    console.log('DOMContentLoaded: checkAuth вернул true, продолжение выполнения.');
    // Обработка кнопки выхода/аккаунта
    showLogoutButton(true);

    // Загрузка текущей страницы
    // Если checkAuth() уже перенаправила, эта строка не будет вызвана.
    // Если checkAuth() вернула true, значит токен действителен.
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
const closeBtn = document.getElementById('closeRegisterModal'); // Исправлено на правильный ID
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
        const expeditions = ['АУП', 'экспедиции №1', 'экспедиции №2', 'экспедиции №3', 'экспедиции №4', 'экспедиции №5', 'экспедиции №6', 'экспедиции №7'];
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
// Отправка данных на сервер для регистрации пользователя
    fetch('/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dataToSend)
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert("Пользователь успешно зарегистрирован");
                modal.style.display = 'none'; // закрыть окно
            } else if (data.error === 'exists') {
                alert("Данный пользователь уже существует");
            } else {
                alert("Произошла ошибка: " + (data.message || "Неизвестная ошибка"));
            }
        })
        .catch(() => alert("Ошибка сети"));

// Можно также добавить обработку ошибок и более сложную логику.
};

