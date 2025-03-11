function sendPayload() {
    let payload = document.getElementById("payload").value;

    // Удаляем <script> теги, если они есть
    if (payload.startsWith('<script>') && payload.endsWith('</script>')) {
        payload = payload.slice(8, -9);
    }

    fetch("/xss/lvl1", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ payload: payload })
    })
    .then(response => response.json())
    .then(data => {
        if (data.payload) {
            document.getElementById("output").innerHTML = "Ваш комментарий отправлен!";
            setTimeout(executeXSS, 1000); // Запуск через 1 секунду
        } else {
            document.getElementById("output").innerHTML = "Ошибка: " + data.error;
        }
    })
    .catch(error => {
        console.error("Ошибка в sendPayload:", error);
    });
}

function executeXSS() {
    fetch('/xss/lvl1/payload')
    .then(response => response.json())
    .then(data => {
        if (data.payload) {
            console.log("Полученный пейлоад:", data.payload); // Отладка в консоли
            let cleanPayload = data.payload;

            // Удаляем <script> теги, если они есть
            if (cleanPayload.startsWith('<script>') && cleanPayload.endsWith('</script>')) {
                cleanPayload = cleanPayload.slice(8, -9);
            }

            try {
                // Создаём div для нового комментария
                let comments = document.getElementById("comments");
                let newComment = document.createElement("div");
                newComment.classList.add("comment");

                // Создаём script-элемент для исполнения XSS
                let script = document.createElement("script");
                script.textContent = cleanPayload;

                // Отображаем комментарий с XSS
                newComment.innerHTML = `<strong>👤 Аноним:</strong> ${data.payload}`;

                document.body.appendChild(script);
                comments.appendChild(newComment);

                // Логирование успешного выполнения XSS
                fetch("/xss/lvl1/log", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ success: true, payload: data.payload })
                });
            } catch (error) {
                console.error("Ошибка выполнения XSS:", error);
            }
        }
    })
    .catch(error => {
        console.error("Ошибка в executeXSS:", error);
    });
}


function checkCookie() {
    let userInput = document.getElementById("cookie-input").value.trim();
    let correctCookie = "xss_vulnerable=hacked_cookie"; // Правильное значение

    let output = document.getElementById("cookie-output");

    if (userInput === correctCookie) {
        output.innerHTML = "✅ Доступ разрешён! Переход на Level 2...";
        output.style.color = "green";

        // Переход на lvl2 через 2 секунды
        setTimeout(() => {
            window.location.href = "/xss/lvl2";
        }, 2000);
    } else {
        output.innerHTML = "❌ Неверные куки. Попробуйте снова.";
        output.style.color = "red";
    }
}
