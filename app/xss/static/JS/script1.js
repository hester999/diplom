function sendPayload() {
    let payload = document.getElementById("payload").value;

    if (payload.startsWith('<script>') && payload.endsWith('</script>')) {
        payload = payload.slice(8, -9);
    }

    payload = `${payload}; logSuccess();`;

    fetch("/xss/lvl1", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ payload: payload })
    })
    .then(response => response.json())
    .then(data => {
        if (data.payload) {
            document.getElementById("output").innerHTML = "Ваш комментарий отправлен!";
            setTimeout(executeXSS, 1000);
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
            console.log("Полученный пейлоад:", data.payload);
            let cleanPayload = data.payload;

            if (cleanPayload.startsWith('<script>') && cleanPayload.endsWith('</script>')) {
                cleanPayload = cleanPayload.slice(8, -9);
            }

            try {
                let comments = document.getElementById("comments");
                let newComment = document.createElement("div");
                newComment.classList.add("comment");

                let script = document.createElement("script");
                script.textContent = cleanPayload;

                newComment.innerHTML = `<strong>👤 Аноним:</strong> ${data.payload}`;

                document.body.appendChild(script);
                comments.appendChild(newComment);

                // Логирование уже будет вызвано через logSuccess
                window.lastPayload = data.payload; // Сохраняем для logSuccess
            } catch (error) {
                console.error("Ошибка выполнения XSS:", error);
            }
        }
    })
    .catch(error => {
        console.error("Ошибка в executeXSS:", error);
    });
}

function logSuccess() {
    fetch("/xss/lvl1/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ success: true, payload: window.lastPayload })
    }).catch(error => console.error("Ошибка логирования успеха:", error));
}

window.lastPayload = "";