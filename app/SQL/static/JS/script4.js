document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('loginForm');
    const messageBox = document.getElementById('message');
    const answerForm = document.getElementById("answerForm");

    // Отправка SQL-инъекции
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const login = document.getElementById('login').value;
        const password = document.getElementById('password').value;

        const data = {
            login: login,
            password: password
        };

        fetch('/sql-injection/lvl4', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                messageBox.innerText = "Инъекция успешна! Теперь проверьте, была ли запись добавлена.";
                messageBox.style.color = "green";
                answerForm.style.display = "block";
            } else {
                messageBox.innerText = data.error || "Ошибка выполнения инъекции.";
                messageBox.style.color = "red";
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageBox.innerText = "Произошла ошибка при отправке запроса.";
            messageBox.style.color = "red";
        });
    });

    // Проверка успешности инъекции
    answerForm.addEventListener("submit", function(event) {
        event.preventDefault();

        fetch('/sql-injection/lvl4/answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                messageBox.innerText = data.message;
                messageBox.style.color = "green";
                alert("Инъекция успешно выполнена! Переход на следующий уровень.");
                window.location.href = '/';
            } else {
                messageBox.innerText = data.error || "Запись не найдена. Попробуйте снова.";
                messageBox.style.color = "red";
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageBox.innerText = "Ошибка проверки записи.";
            messageBox.style.color = "red";
        });
    });
});
