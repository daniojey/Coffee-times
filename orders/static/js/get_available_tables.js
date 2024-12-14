let previousData = {
    coffeehouse: '',
    reservation_date: '',
    reservation_time: '',
    booking_duration: ''
};

let isTableContainerVisible = false; // Флаг для отслеживания состояния видимости контейнера

document.getElementById('reservation-form').addEventListener('change', function (event) {
    const tableSelections = document.getElementById('available-tables-container');
    const tableSelectField = document.getElementById('available_tables');

    // Если изменяется выбор столика, игнорируем дальнейшую обработку
    if (event.target.id === 'available_tables') {
        console.log("Table selection changed, skipping form update logic.");
        return;
    }

    // Скрываем блок с доступными столиками до обновления
    if (!['available_tables'].includes(event.target.id)) {
        tableSelections.classList.add('hidden');
        isTableContainerVisible = false;
    }

    // Получаем значения полей формы
    const coffeehouse = document.getElementById('coffeehouse').value;
    const reservation_date = document.getElementById('reservation_date').value;
    const reservation_time = document.getElementById('reservation_time').value;
    const booking_duration = document.getElementById('booking_duration').value;

    console.log("Form data:", {
        coffeehouse: coffeehouse,
        reservation_date: reservation_date,
        reservation_time: reservation_time,
        booking_duration: booking_duration
    });

    // Проверяем, изменилось ли хотя бы одно из ключевых полей
    if (
        coffeehouse !== previousData.coffeehouse ||
        reservation_date !== previousData.reservation_date ||
        reservation_time !== previousData.reservation_time ||
        booking_duration !== previousData.booking_duration
    ) {
        // Обновляем предыдущее состояние данных формы
        previousData = {
            coffeehouse: coffeehouse,
            reservation_date: reservation_date,
            reservation_time: reservation_time,
            booking_duration: booking_duration
        };

        // Проверяем, заполнены ли все поля
        if (coffeehouse && reservation_date && reservation_time && booking_duration) {
            console.log("All fields filled, sending AJAX request...");

            // Отправляем AJAX-запрос
            fetch('get_tables/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    coffeehouse: coffeehouse,
                    reservation_date: reservation_date,
                    reservation_time: reservation_time,
                    booking_duration: booking_duration
                })
            })
            .then(response => {
                console.log("Response status:", response.status);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log("Data received from server:", data);

                // Очищаем текущие варианты выбора столиков
                tableSelectField.innerHTML = '';

                // Добавляем новые варианты
                data.tables.forEach(table => {
                    const option = document.createElement('option');
                    option.value = table.id;
                    option.textContent = table.name;
                    tableSelectField.appendChild(option);
                });

                // Показываем блок с доступными столиками, если есть данные
                if (data.tables.length > 0) {
                    tableSelections.classList.remove('hidden');
                    isTableContainerVisible = true;
                } else {
                    console.log("No tables available.");
                }
            })
            .catch(error => {
                console.error("Ошибка:", error);
            });
        } else {
            console.log("Not all fields are filled, skipping AJAX request.");
        }
    } else {
        console.log("No changes detected, skipping AJAX request.");
    }
});