document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.input-form');
    const messageBox = document.getElementById('message');
    const adminForm = document.querySelector('.answer-form');

    form.addEventListener('submit', function (event) {
        event.preventDefault();  // Останавливаем отправку формы для демонстрации

        const login = document.getElementById('login').value;
        const password = document.getElementById('password').value;

        // Проверка инъекции (если пароль похож на типичную инъекцию)
        if (password.includes("' OR 1=1 --")) {
            messageBox.textContent = "Поздравляем! Вы успешно провели SQL инъекцию.";
            messageBox.classList.remove('error'); // Убираем класс ошибки
            messageBox.classList.add('success'); // Добавляем класс успеха
            messageBox.style.display = 'block'; // Показываем сообщение
        } else {
            messageBox.textContent = "Попробуйте ввести правильную SQL инъекцию.";
            messageBox.classList.remove('success'); // Убираем класс успеха
            messageBox.classList.add('error'); // Добавляем класс ошибки
            messageBox.style.display = 'block'; // Показываем сообщение
        }
    });

    adminForm.addEventListener('submit', function (event) {
        event.preventDefault();  // Останавливаем отправку формы для проверки

        const adminLogin = document.getElementById('admin_login').value;
        const adminPassword = document.getElementById('admin_password').value;

        // Простейшая проверка логина и пароля администратора
        if (adminLogin === "admin" && adminPassword === "admin123") {
            alert("Администратор авторизован! Продолжаем.");
            window.location.href = '/sql-injection/lvl2';  // Переход на второй уровень
        } else {
            alert("Неверный логин или пароль администратора!");
        }
    });
});
