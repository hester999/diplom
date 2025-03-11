// Очистка при обновлении страницы
window.onload = function() {
    const commentsDiv = document.getElementById('comments');
    commentsDiv.innerHTML = ''; // Очищаем блок при загрузке
};

// Очистка через определённое время (например, каждые 10 секунд)
setInterval(function() {
    const commentsDiv = document.getElementById('comments');
    commentsDiv.innerHTML = ''; // Очищаем блок каждые 10 секунд
}, 10000); // 10000 мс = 10 секунд