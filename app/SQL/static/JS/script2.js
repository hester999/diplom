document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('.input-form');
    const messageBox = document.getElementById('message');
    const answerForm = document.getElementById("answerForm");
    const tablesResult = document.getElementById("tablesResult");
    const tablesList = document.getElementById("tablesList");

    // Обработчик для отправки данных инъекции
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Останавливаем отправку формы

        const login = document.getElementById('login').value;
        const password = document.getElementById('password').value;

        // Формируем объект данных
        const data = {
            login: login,
            password: password
        };

        fetch('/sql-injection/lvl2', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)  // Преобразуем объект в JSON
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка с сервером');
            }
            return response.json();
        })
        .then(data => {
            // Проверяем успешность инъекции
            if (data.result) {
                // Если инъекция успешна, показываем сообщение и ждем ввода таблиц
                messageBox.innerText = "Инъекция успешна! Пожалуйста, введите список таблиц.";
                messageBox.style.color = "green";

                // Показываем форму для ответа
                answerForm.style.display = "block";

                // Показываем результат работы запроса (список таблиц)
                tablesResult.style.display = "block";
                tablesList.innerText = data.result.join(", ");
            } else {
                // Ошибка инъекции
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

    // Обработчик для отправки ответа
    if (answerForm) {
        answerForm.addEventListener("submit", function(event) {
            event.preventDefault();  // Останавливаем отправку формы

            const studentAnswer = document.getElementById('student_answer').value;

            // Отправляем ответ
            fetch('/sql-injection/lvl2/answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ student_answer: studentAnswer })
            })
            .then(response => {
                if (response.ok) {
                    alert("Ответ верный!")
                    window.location.href = '/sql-injection/lvl3';
                } else {
                    throw new Error('Ошибка при отправке ответа');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                messageBox.innerText = "Произошла ошибка при отправке ответа.";
                messageBox.style.color = "red";
            });
        });
    }
});