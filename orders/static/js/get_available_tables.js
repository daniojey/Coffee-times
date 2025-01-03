console.log('get_available_tables.js загружен');

// Флаг для отслеживания состояния выполнения запроса времени
let isTimeFetched = false;

// Функция для отправки запроса на получение времени
function getAvailableTimes() {
    const dateInput = document.getElementById('reservation_date');
    const timeSelect = document.getElementById('reservation_time');
    const coffeehouse = document.getElementById('coffeehouse'); // Элемент кофейни

    const selectedDate = dateInput.value;
    const selectedCoffeehouse = coffeehouse.value; // Получаем значение кофейни

    // Проверяем, выбраны ли кофейня и дата
    if (!selectedDate || !selectedCoffeehouse) {
        console.log("Кофейня или дата не выбраны, запрос времени не отправляется.");
        return;
    }

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

            // После получения времени, устанавливаем флаг, что время получено
            isTimeFetched = true;

            // Теперь, если время получено, проверяем, можно ли подсчитать столики
            if (isTimeFetched) {
                getAvailableTables(); // Запускаем подсчёт столиков
            }
        })
        .catch(error => {
            console.error("Ошибка при получении времени:", error);
        });
}

// Функция для отправки запроса на сервер для получения столиков
function getAvailableTables() {
    const coffeehouse = document.getElementById('coffeehouse').value;
    const reservation_date = document.getElementById('reservation_date').value;
    const reservation_time = document.getElementById('reservation_time').value;
    const booking_duration = document.getElementById('booking_duration').value;

    // Проверяем, заполнены ли кофейня, дата, время и длительность бронирования
    if (!coffeehouse || !reservation_date) {
        console.log("Кофейня или дата не выбраны, запрос на столики не отправляется.");
        return;
    }

    if (!reservation_time || !booking_duration) {
        console.log("Время или длительность бронирования не выбраны, запрос на столики не отправляется.");
        return;
    }

    console.log("Все необходимые данные заполнены, отправляем запрос на сервер...");

    // Отправляем AJAX-запрос для получения столиков
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

        const tableSelectField = document.getElementById('available_tables');
        const tableSelections = document.getElementById('available-tables-container');
        const noTablesMessage = document.getElementById('no-available-tibles-message');

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
            noTablesMessage.classList.add('hidden');  // Скрыть сообщение, если есть столики
        } else {
            tableSelections.classList.add('hidden');  // Скрыть контейнер с таблицами
            noTablesMessage.classList.remove('hidden');  // Показать сообщение, если столики отсутствуют
        }
    })
    .catch(error => {
        console.error("Ошибка:", error);
    });
}

// Слушаем изменения в полях времени и длительности бронирования
document.getElementById('reservation_time').addEventListener('change', function() {
    // Если время изменилось, проверяем и обновляем доступные столики
    if (isTimeFetched) {
        getAvailableTables();
    }
});
document.getElementById('booking_duration').addEventListener('change', function() {
    // Если длительность бронирования изменена, проверяем и обновляем доступные столики
    if (isTimeFetched) {
        getAvailableTables();
    }
});

// Слушаем изменения в кофейне и дате, чтобы обновить доступное время
document.getElementById('reservation_date').addEventListener('change', getAvailableTimes);
document.getElementById('coffeehouse').addEventListener('change', getAvailableTimes);

// Инициализация при загрузке страницы
getAvailableTimes();
