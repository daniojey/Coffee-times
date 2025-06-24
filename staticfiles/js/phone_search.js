// Функция для преобразования времени в формате HH:MM:SS в читаемый формат
function formatTime(timeString) {
    const [hours, minutes, seconds] = timeString.split(':').map(num => parseInt(num, 10));
  
    // Формируем строку в формате 2ч 00мин
    if (hours > 0) {
      return `${hours}г ${minutes}хв`;  // Если есть часы, показываем их
    }
  
    return `${minutes}хв ${seconds}сек`;  // Если нет часов, показываем минуты и секунды
  }
  
  // Отправка формы через JS при нажатии Enter
  document.getElementById('phone').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();  // Отменить стандартное поведение (отправку формы)
      submitForm();  // Вызвать функцию для отправки данных через fetch
    }
  });
  
  // Обработчик кнопки "Поиск"
  const button = document.getElementById('search-button')
  button.addEventListener('click', function () {
    submitForm();  // Вызов функции отправки формы
  });
  
  // Функция для отправки данных
function submitForm() {
    const phone = document.getElementById('phone').value;
    const actual = document.getElementById('checkbox').checked;  // Получаем состояние чекбокса (true или false)
    console.log(actual)  // Получаем значение поля "actual"
  
    // Проверим, что номер телефона введён
    if (!phone) {
      alert("Пожалуйста, введите номер телефона.");
      return;
    }
  
    // Отправляем запрос на сервер
    fetch('/search-reservation/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value  // CSRF токен для защиты от CSRF атак
      },
      body: JSON.stringify({ phone: phone, actual: actual})  // Отправляем данные в формате JSON
    })
    .then(response => response.json())  // Получаем ответ в формате JSON
    .then(data => {
      const container = document.getElementById('reservation-block');
      container.innerHTML = '';  // Очистка контейнера перед добавлением новых данных
  
      if (data.reservations && data.reservations.length > 0) {
        const baseElement = document.querySelector('.search-base-container');
        baseElement.style.height = '88%';
        baseElement.style.boxSizing = 'border-box';
        baseElement.style.width = '92%';

        const searchBlock = document.querySelector('.search-block');
        searchBlock.style.marginBottom = '30px';

        let delay = 0;  // Начальная задержка

        data.reservations.forEach(reservation => {
          setTimeout(() => {
            const bookingElement = document.createElement('div');
          bookingElement.classList.add('reservation-item');
          
          // Преобразуем время и длительность
          const formattedReservationTime = formatTime(reservation.time);  // Время бронирования
          const formattedDuration = formatTime(reservation.times);  // Длительность
  
          bookingElement.innerHTML = `
            <div class="reservation-container">
                <p>Дата: ${reservation.date}</p>
                <p>Номер столика: ${reservation.table_number}</p>
                <p>Кількість місць: ${reservation.seats}</p>
                <p>Час бронювання: ${formattedReservationTime}</p>
                <p>Продовжуваність: ${formattedDuration}</p>
            </div>
          `;
          container.appendChild(bookingElement);
          }, delay)
          
          delay += 100;  // Увеличиваем задержку на 1 секунду для каждого элемента
        });
      } else {
        const baseElement = document.querySelector('.search-base-container');
        baseElement.style.height = '88%';
        baseElement.style.boxSizing = 'border-box';
        baseElement.style.width = '92%';
        container.innerHTML = `
        <div class="no-results-container">
          <p>Бронювання не знайдені.</p>
        </div>
        `;
      }
    })
    .catch(error => {
      console.error('Ошибка:', error);
    });
  }