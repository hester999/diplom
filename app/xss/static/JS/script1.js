document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('xssForm');
    const messageBox = document.getElementById('message');

    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Останавливаем отправку формы

        const payload = document.getElementById('payload').value;

        fetch('/xss/lvl1', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ payload: payload })
        })
        .then(response => {
            if (response.ok) {
                messageBox.innerText = "XSS payload успешно выполнен!";
                messageBox.style.color = "green";
                setTimeout(() => {
                    window.location.href = "/xss/lvl2"; // Переход на следующий уровень
                }, 2000);
            } else {
                messageBox.innerText = "Попробуйте снова! Это не XSS-инъекция.";
                messageBox.style.color = "red";
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            messageBox.innerText = "Ошибка при отправке запроса.";
            messageBox.style.color = "red";
        });
    });
});
