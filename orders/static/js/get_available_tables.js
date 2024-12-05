document.getElementById('reservation-form').addEventListener('change', function () {
    // Логируем начало события изменения
    console.log("Form changed, starting to gather data...");

    // Получаем значения из формы
    const coffeehouse = document.getElementById('coffeehouse').value;
    const reservation_date = document.getElementById('reservation_date').value;
    const reservation_time = document.getElementById('reservation_time').value;
    const booking_duration = document.getElementById('booking_duration').value;

    // Логируем данные формы
    console.log("Form data:", {
        coffeehouse: coffeehouse,
        reservation_date: reservation_date,
        reservation_time: reservation_time,
        booking_duration: booking_duration
    });

    // Проверяем, все ли поля заполнены
    if (coffeehouse && reservation_date && reservation_time && booking_duration) {
        console.log("All fields filled, sending AJAX request...");

        // Отправляем AJAX запрос
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
            // Логируем статус ответа
            console.log("Response status:", response.status);

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            return response.json();
        })
        .then(data => {
            // Логируем полученные данные
            console.log("Data received from server:", data);

            // Обновляем список доступных столиков
            const tableSelect = document.getElementById('available_tables');
            tableSelect.innerHTML = '';  // очищаем текущие варианты

            // Логируем процесс обновления списка столиков
            console.log("Updating table options...");
            data.tables.forEach(table => {
                const option = document.createElement('option');
                option.value = table.id;
                option.textContent = table.name;
                tableSelect.appendChild(option);
            });
        })
        .catch(error => {
            // Логируем ошибку
            console.error("Ошибка:", error);
        });
    } else {
        console.log("Not all fields are filled, skipping AJAX request.");
    }
});
