// Обработка формы входа
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        loginUser();
    });
}

// Обработчик выхода — навешан внутри функции showLogoutButton при необходимости

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
            // После входа скрываем форму и показываем контент
            const loginContainer = document.getElementById('login-container');
            const contentContainer = document.getElementById('content');

            if (loginContainer && contentContainer) {
                loginContainer.style.display = 'none';
                contentContainer.style.display = 'block';
            }

            // Показываем кнопку выхода
            showLogoutButton(true);

            // Перенаправляем на /home
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
                    window.location.reload();
                });
                logoutItem.hasListener = true; // чтобы не навешивать повторно
            }
        }
    }
}
window.addEventListener('load', async () => {
    const path = window.location.pathname;
    const token = localStorage.getItem('access_token');

    const loginContainer = document.getElementById('login-container');
    const contentContainer = document.getElementById('content');

    if (!token) {
        // Нет токена — показываем форму входа
        if (loginContainer) loginContainer.style.display = 'block';
        // if (contentContainer) contentContainer.style.display = 'none';

        showLogoutButton(false);
        return;
    }

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

            // Показываем кнопку выхода
            showLogoutButton(true);
        } else {
            // Не авторизован или ошибка — редирект на логин
            alert('Пожалуйста, войдите в систему.');
            localStorage.removeItem('access_token');
            window.location.href = '/pages/login';
        }
    } catch (error) {
        alert('Ошибка при загрузке домашней страницы: ' + error);
    }
});
