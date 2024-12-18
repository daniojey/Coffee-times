document.addEventListener('DOMContentLoaded', function () {
    const dateInput = document.getElementById('reservation_date');
    const timeSelect = document.getElementById('reservation_time');
    const coffeehouse = document.getElementById('coffeehouse'); // Элемент кофейни

    function updateAvailableTimes() {
        const selectedDate = dateInput.value;
        const selectedCoffeehouse = coffeehouse.value; // Получаем значение кофейни

        // Формируем URL с параметрами date и coffeehouse
        const url = `/orders/reservation/get-available-times/?date=${selectedDate}&coffeehouse=${selectedCoffeehouse}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                timeSelect.innerHTML = '';  // Очищаем старые опции
                data.times.forEach(time => {
                    const option = document.createElement('option');
                    option.value = time;
                    option.textContent = time;
                    timeSelect.appendChild(option);
                });
            });
    }

    // Слушаем изменения даты и кофейни
    dateInput.addEventListener('change', updateAvailableTimes);
    coffeehouse.addEventListener('change', updateAvailableTimes);

    updateAvailableTimes(); // Инициализация при загрузке страницы
});