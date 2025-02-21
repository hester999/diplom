document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById('loginForm');
    const answerForm = document.getElementById('answerForm');
    const messageBox = document.getElementById('message');

    // Обработчик для отправки данных логина и пароля
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();  // Останавливаем отправку формы

        const login = document.getElementById('login').value;
        const password = document.getElementById('password').value;

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
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                // Если инъекция успешна, показываем результаты
                messageBox.innerHTML = "Инъекция успешна! Вот результаты: <br>";
                data.result.forEach(item => {
                    messageBox.innerHTML += `
                        <p>Имя пользователя: ${item.username}</p>
                        <p>Пароль: ${item.password}</p>
                        <p>Продукт: ${item.product_name}</p>
                        <p>Цена: ${item.price}</p>
                        <hr>
                    `;
                });

                // Показываем форму для ввода минимальной цены
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

    // Обработчик для отправки ответа
    answerForm.addEventListener("submit", function(event) {
        event.preventDefault();  // Останавливаем отправку формы

        const studentAnswer = document.getElementById('student_answer').value;

        fetch('/sql-injection/lvl2/answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ student_answer: studentAnswer })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                messageBox.innerText = data.message;
                messageBox.style.color = "green";
            } else {
                messageBox.innerText = data.error || "Ответ неверен, попробуйте снова.";
                messageBox.style.color = "red";
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageBox.innerText = "Произошла ошибка при отправке ответа.";
            messageBox.style.color = "red";
        });
    });
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
                if (response.ok){
                    alert("Ответ верный!")
                    window.location.href = '/sql-injection/lvl3';
                }
                if (!response.ok) {
                    throw new Error('Ошибка при отправке ответа');
                }
                return response.json();
            })
            .then(data => {
                // Проверяем правильность ответа
                if (data.message) {
                    messageBox.innerText = data.message;
                    messageBox.style.color = "green";
                } else {
                    messageBox.innerText = data.error || "Ответ неверен, попробуйте снова.";
                    messageBox.style.color = "red";
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
