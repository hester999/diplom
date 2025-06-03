document.addEventListener('DOMContentLoaded', function() {
    // Анимация для кнопок уровней
    const levelButtons = document.querySelectorAll('.level-btn');

    levelButtons.forEach(button => {
        button.addEventListener('mouseover', function() {
            button.style.transform = 'scale(1.1) rotate(2deg)';
        });

        button.addEventListener('mouseout', function() {
            button.style.transform = 'scale(1)';
        });
    });

    // Устанавливаем --index для категорий (для последовательной анимации)
    const categories = document.querySelectorAll('.category');
    categories.forEach((category, index) => {
        category.style.setProperty('--index', index);
    });

    // Устанавливаем --index для карточек базы знаний
    const knowledgeCards = document.querySelectorAll('.knowledge-card');
    knowledgeCards.forEach((card, index) => {
        card.style.setProperty('--index', index);
    });
});