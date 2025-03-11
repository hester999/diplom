


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
            let cookieText = item.cookie || "Неизвестно";
            let stolenAt = item.stolen_at || "Неизвестно";

            let cookieDiv = document.createElement("div");
            cookieDiv.classList.add("cookie-item");
            cookieDiv.innerHTML = `
                <span class="cookie-icon">🍪</span> <code>${cookieText}</code> <br>
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
