// JavaScript для бургер-меню (Уровень 1)
document.querySelector('.burger').addEventListener('click', () => {
    document.querySelector('.nav.html-links').classList.toggle('nav.html-active');
    document.querySelector('.burger i').classList.toggle('fa-bars');
    document.querySelector('.burger i').classList.toggle('fa-times');
});