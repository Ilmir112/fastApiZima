// Проверка авторизации при загрузке
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        // Нет токена — перенаправляем на страницу входа
        window.location.href = '/pages/login';
        return; // чтобы не выполнять остальной код
    }
    if (token) {
        // Если есть токен, скрываем форму входа
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('content').style.display = 'block';
        document.querySelector('nav').classList.remove('d-none');

        // Показываем кнопку выхода
        showLogoutButton(true);

        // Перенаправление на /home, если нужно
        if (window.location.pathname === '/' || window.location.pathname === '/pages/login') {
            window.location.href = '/pages/home';
        }
    } else {
        // Нет токена
        document.getElementById('login-container').style.display = 'block';
        document.getElementById('content').style.display = 'none';
        showLogoutButton(false);
    }
});

// Обработка формы входа
document.getElementById('loginForm').addEventListener('submit', function (e) {
    e.preventDefault();
    loginUser();
});

// Обработчик выхода
document.getElementById('logoutBtn')?.addEventListener('click', () => {
    localStorage.removeItem('access_token');
    // Перезагружаем страницу или перенаправляем
    window.location.reload();
});

// Функция для отображения кнопки выхода
function showLogoutButton(show) {
    const logoutItem = document.getElementById('logoutItem');
    if (logoutItem) {
        logoutItem.classList.toggle('d-none', !show);
    }
}

async function loginUser() {
    const loginInput = document.getElementById('login_user');
    const passwordInput = document.getElementById('password');
    const loginUserValue = loginInput.value;
    const password = passwordInput.value;

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({login_user: loginUserValue, password: password})
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            // После входа скрываем форму и показываем контент
            document.getElementById('login-container').style.display = 'none';
            document.getElementById('content').style.display = 'block';
            showLogoutButton(true);
            // Загружаем домашнюю страницу или другой контент
            window.location.href = '/pages/home';
        } else {
            const errorText = await response.text();
            alert('Ошибка входа: ' + errorText);
        }
    } catch (error) {
        alert('Ошибка сети: ' + error);
    }
}

// Загрузка домашней страницы
async function loadHomePage() {
    const token = localStorage.getItem('access_token');

    // Проверка наличия токена
    if (!token) {
        alert('Пожалуйста, войдите в систему.');
        window.location.href = '/pages/login';
        return;
    }

    const response = await fetch('/pages/home', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (response.ok) {
        const htmlContent = await response.text();
        document.getElementById('content').innerHTML = htmlContent;
    } else {
        alert('Пожалуйста, войдите в систему.');
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    }
}

// Обработка навигации
window.addEventListener('load', () => {
    const path = window.location.pathname;
    const token = localStorage.getItem('access_token');

    if (!token) {
        // Если нет токена, показываем форму
        document.getElementById('login-container').style.display = 'block';
        document.getElementById('content').style.display = 'none';
        showLogoutButton(false);
        return;
    }

    if (path === '/pages/home' || path === '/') {
        loadHomePage();
    }
    // Можно добавить обработку других URL
});