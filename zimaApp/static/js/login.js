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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login_user: loginUserValue, password: password })
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

    } else if (path === '/pages/home' ||
                path.startsWith('/pages/')) {
        // Страница домашней страницы
        if ((await checkAuth())) return;

        try {
            const response = await fetch('/pages/home', {
                headers: { 'Authorization': `Bearer ${token}` }
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

    } else if (
        path === '/pages/profile' ||
        path === '/pages/settings'  // добавьте сюда нужные пути
    ) {
        // Для других страниц с ограниченным доступом
        if (!(await checkAuth())) return;

        // Можно делать дополнительные запросы или показывать контент
        try {
            const response = await fetch(path, {
                headers: { 'Authorization': `Bearer ${token}` }
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