let noClickCount = 0;
const maxNoClicks = 4;

const yesBtn = document.getElementById('yes-btn');
const noBtn = document.getElementById('no-btn');
const mainPhoto = document.getElementById('main-photo');
const fallingHearts = document.getElementById('falling-hearts');
const yesMessage = document.getElementById('yes-message');

// Обработчик нажатия на "Нет"
noBtn.addEventListener('click', () => {
    noClickCount++;
    
    if (noClickCount < maxNoClicks) {
        // Увеличиваем "Да" и меняем текст
        const currentYesSize = parseFloat(window.getComputedStyle(yesBtn).fontSize);
        yesBtn.style.fontSize = (currentYesSize * 1.3) + 'px';
        yesBtn.style.padding = (parseFloat(window.getComputedStyle(yesBtn).paddingTop) * 1.3) + 'px ' + 
                                (parseFloat(window.getComputedStyle(yesBtn).paddingRight) * 1.3) + 'px';
        
        if (noClickCount === 1) {
            yesBtn.textContent = 'Может да';
        } else if (noClickCount === 2) {
            yesBtn.textContent = 'Ну пожалуйста 🥺';
        }
        
        // Уменьшаем "Нет"
        const currentNoSize = parseFloat(window.getComputedStyle(noBtn).fontSize);
        noBtn.style.fontSize = (currentNoSize * 0.7) + 'px';
        noBtn.style.padding = (parseFloat(window.getComputedStyle(noBtn).paddingTop) * 0.7) + 'px ' + 
                              (parseFloat(window.getComputedStyle(noBtn).paddingRight) * 0.7) + 'px';
    } else {
        // После 4 нажатий скрываем "Нет" и меняем текст "Да"
        noBtn.style.display = 'none';
        yesBtn.textContent = 'У тебя уже нет выбора';
        yesBtn.style.fontSize = '28px';
        yesBtn.style.padding = '25px 60px';
    }
});

// Обработчик нажатия на "Да"
yesBtn.addEventListener('click', () => {
    // Меняем фотографию
    mainPhoto.src = 'images/photo2.jpg';
    
    // Показываем падающие сердечки
    fallingHearts.classList.remove('hidden');
    startFallingHearts();
    
    // Показываем текст
    yesMessage.classList.remove('hidden');
    
    // Скрываем кнопки
    yesBtn.style.display = 'none';
    noBtn.style.display = 'none';
});

// Функция для создания падающих сердечек
function startFallingHearts() {
    const hearts = ['💖', '💕', '💗', '💓', '💝', '❤️'];
    
    function createHeart() {
        const heart = document.createElement('div');
        heart.className = 'falling-heart';
        heart.textContent = hearts[Math.floor(Math.random() * hearts.length)];
        heart.style.left = Math.random() * 100 + '%';
        heart.style.animationDuration = (Math.random() * 3 + 3) + 's';
        heart.style.animationDelay = Math.random() * 2 + 's';
        fallingHearts.appendChild(heart);
        
        // Удаляем сердечко после анимации
        setTimeout(() => {
            heart.remove();
        }, 8000);
    }
    
    // Создаем новое сердечко каждые 300мс
    const heartInterval = setInterval(createHeart, 300);
    
    // Создаем начальные сердечки
    for (let i = 0; i < 10; i++) {
        setTimeout(createHeart, i * 100);
    }
}
