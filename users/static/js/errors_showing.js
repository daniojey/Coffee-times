document.addEventListener('DOMContentLoaded', function () {
    // Получаем JSON из тега
    const errorsElement = document.getElementById('form-errors');
    if (errorsElement) {
        const errors = JSON.parse(errorsElement.textContent);
        
        // Обработка ошибок
        if (errors) {
            let topScale = 10
            let delay = 6000;
            errors.__all__.forEach(error => {
                const popup = document.createElement('div')
                popup.classList.add('error-popup')
                popup.innerText = error
                popup.style.top = `${topScale}%`
                topScale += 7;
                document.body.appendChild(popup);
                
                setTimeout(() => {
                    popup.style.opacity = "0"; // Уменьшаем прозрачность до 0

                    setTimeout(() => {
                        popup.remove(); // Удаляем элемент из DOM после завершения анимации
                    }, 1000); // Время анимации соответствует CSS
                }, delay);

                delay += 200; // Увеличиваем задержку для следующего сообщения
            });
        }
    }
});

