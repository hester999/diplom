document.addEventListener("DOMContentLoaded", function () {
    const adminForm = document.querySelector('.answer-form'); // Ищем форму по классу .answer-form

    // Добавляем обработчик события для отправки формы
    adminForm.addEventListener('submit', function (event) {
        event.preventDefault();  // Останавливаем отправку формы, чтобы выполнить проверку

        // Получаем значения логина и пароля из формы
        const adminLogin = document.getElementById('admin_login').value;
        const adminPassword = document.getElementById('admin_password').value;

        // Формируем объект данных для отправки в формате JSON
        const data = {
            admin_login: adminLogin,
            admin_password: adminPassword
        };

        // Отправляем данные на сервер с помощью fetch
        fetch('/sql-injection/lvl1/answer', {
            method: 'POST',  // Указываем, что отправляем данные методом POST
            headers: {
                'Content-Type': 'application/json'  // Устанавливаем тип контента как JSON
            },
            body: JSON.stringify(data)  // Преобразуем объект данных в строку JSON
        })
        .then(response => {
            // Если сервер вернул статус 200 (успешно)
            if (response.ok) {
                // Переходим на второй уровень
                window.location.href = '/sql-injection/lvl2';
            } else {
                // Если ошибка, показываем сообщение об ошибке
                response.json().then(data => {
                    alert(data.error || "Произошла ошибка при авторизации.");
                });
            }
        })
        .catch(error => {
            // В случае ошибок при запросе
            console.error('Error:', error);
            alert("Произошла ошибка при отправке запроса.");
        });
    });
});
