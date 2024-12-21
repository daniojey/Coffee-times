console.log('Скрипт подгрузки времени загружен')
document.addEventListener('DOMContentLoaded', function () {
    const dateInput = document.getElementById('reservation_date');
    const timeSelect = document.getElementById('reservation_time');
    const coffeehouse = document.getElementById('coffeehouse'); // Элемент кофейни
    const noAvailableMessage = document.getElementById('no-available-times-message'); // Сообщение об отсутствии времени

    function updateAvailableTimes() {
        const selectedDate = dateInput.value;
        const selectedCoffeehouse = coffeehouse.value; // Получаем значение кофейни

        // Проверяем, заполнены ли оба поля
        if (!selectedDate || !selectedCoffeehouse) {
            // Если одно из полей пустое, не отправляем запрос
            return;
        }

        // Формируем URL с параметрами date и coffeehouse
        const url = `/orders/reservation/get-available-times/?date=${selectedDate}&coffeehouse=${selectedCoffeehouse}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                timeSelect.innerHTML = '';  // Очищаем старые опции

                if (data.times.length > 0) {
                    // Если есть доступное время, показываем его
                    data.times.forEach(time => {
                        const option = document.createElement('option');
                        option.value = time;
                        option.textContent = time;
                        timeSelect.appendChild(option);
                    });

                    // Скрываем сообщение об отсутствии времени
                    noAvailableMessage.classList.add('hidden');
                    timeSelect.classList.remove('hidden');
                } else {
                    // Если нет доступного времени, показываем сообщение
                    noAvailableMessage.classList.remove('hidden');
                    timeSelect.classList.add('hidden');
                }
            })
            .catch(error => {
                console.error("Ошибка при получении времени:", error);
            });
    }

    // Слушаем изменения даты и кофейни
    dateInput.addEventListener('change', updateAvailableTimes);
    coffeehouse.addEventListener('change', updateAvailableTimes);

    updateAvailableTimes(); // Инициализация при загрузке страницы
});