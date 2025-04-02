document.addEventListener("DOMContentLoaded", function () {
    const errorsElement = document.getElementById('form-errors');
    if (errorsElement) {
        const errors = JSON.parse(errorsElement.textContent);
        

        if (errors) {
            let delay = 6000; // Начальная задержка для первого сообщения
            let topScale = 10; // Начальная позиция по вертикали
            for (const key in errors) {
                
                errors[key].forEach(error => {
                    const popup = document.createElement('div')
                    popup.classList.add('error-popup');
                    popup.style.top = `${topScale}%`; // Устанавливаем позицию по вертикали
                    popup.innerText = `${key}: ${error}`; // Добавляем ключ ошибки к сообщению
                    document.body.appendChild(popup);
                    topScale += 7; // Увеличиваем позицию для следующего сообщения
                    
                    setTimeout(() => {
                        popup.style.opacity = "0"; // Уменьшаем прозрачность до 0

                        setTimeout(() => {
                            popup.remove(); // Удаляем элемент из DOM после завершения анимации
                        }, 1000); // Время анимации соответствует CSS
                    }, delay);

                    delay += 200; // Увеличиваем задержку для следующего сообщения
                    }
                );
            }        
        }
    }
});