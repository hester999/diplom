// Если нужно добавить дополнительные функциональности для главной страницы, например, анимацию при наведении на кнопки, можно использовать такой код:

document.addEventListener('DOMContentLoaded', function() {
    const levelButtons = document.querySelectorAll('.level-btn');

    levelButtons.forEach(button => {
        button.addEventListener('mouseover', function() {
            button.style.transform = 'scale(1.1)';
        });

        button.addEventListener('mouseout', function() {
            button.style.transform = 'scale(1)';
        });
    });
});
