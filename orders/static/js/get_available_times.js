console.log('Скрипт загружен');

// Функция для обновления доступного времени резервации
function updateAvailableTimes() {
    const dateInput = document.getElementById('reservation_date');
    const timeSelect = document.getElementById('reservation_time');
    const coffeehouse = document.getElementById('coffeehouse'); // Элемент кофейни
    const noAvailableMessage = document.getElementById('no-available-times-message'); // Сообщение об отсутствии времени

    const selectedDate = dateInput.value;
    const selectedCoffeehouse = coffeehouse.value; // Получаем значение кофейни

    // Проверяем, заполнены ли оба поля
    if (!selectedDate || !selectedCoffeehouse) {
        console.log("Дата или кофейня не выбраны.");
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

                // После успешного обновления времени вызываем обновление длительности бронирования
                updateBookingDuration();
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

// Функция для отправки данных на сервер и обновления поля booking_duration
function updateBookingDuration() {
    const reservationTime = document.getElementById('reservation_time').value;
    const reservationDate = document.getElementById('reservation_date').value;
    const coffeehouse = document.getElementById('coffeehouse').value;

    // Проверяем, что все поля заполнены
    if (!reservationTime || !reservationDate || !coffeehouse) {
        console.log("Кофейня или дата не выбраны, запрос времени не отправляется.");
        return;
    }

    // Отправляем запрос на сервер
    fetch('get-booking-duration/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            coffeehouse: coffeehouse,
            reservation_date: reservationDate,
            reservation_time: reservationTime
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log("Data received from server:", data);

        // Получаем поле для длительности бронирования
        const bookingDurationField = document.getElementById('booking_duration');

        // Очищаем старые данные
        bookingDurationField.innerHTML = '';

        // Заполняем новые данные
        if (data.data && data.data.length > 0) {
            data.data.forEach(time => {
                const option = document.createElement('option');
                option.value = time;
                option.textContent = time;
                bookingDurationField.appendChild(option);
            });

            // Показываем блок с доступными вариантами, если есть данные
            bookingDurationField.classList.remove('hidden');
        } else {
            console.log("Нет доступных временных интервалов.");
        }
    })
    .catch(error => {
        console.error("Ошибка:", error);
    });
}

// Привязываем функцию обновления времени к изменениям в полях
document.getElementById('reservation_date').addEventListener('change', updateAvailableTimes);
document.getElementById('coffeehouse').addEventListener('change', updateAvailableTimes);

// Привязываем функцию обновления длительности к изменению времени резервации
document.getElementById('reservation_time').addEventListener('change', updateBookingDuration);

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', updateAvailableTimes);
