// Функция для преобразования времени в формате HH:MM:SS в читаемый формат
function formatTime(timeString) {
    const [hours, minutes, seconds] = timeString.split(':').map(num => parseInt(num, 10));
  
    // Формируем строку в формате 2ч 00мин
    if (hours > 0) {
      return `${hours}ч ${minutes}мин`;  // Если есть часы, показываем их
    }
  
    return `${minutes}мин ${seconds}сек`;  // Если нет часов, показываем минуты и секунды
  }
  
  // Отправка формы через JS при нажатии Enter
  document.getElementById('phone').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();  // Отменить стандартное поведение (отправку формы)
      submitForm();  // Вызвать функцию для отправки данных через fetch
    }
  });
  
  // Обработчик кнопки "Поиск"
  document.getElementById('check-booking').addEventListener('click', function () {
    submitForm();  // Вызов функции отправки формы
  });
  
  // Функция для отправки данных
  function submitForm() {
    const phone = document.getElementById('phone').value;
  
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
      body: JSON.stringify({ phone: phone })  // Отправляем данные в формате JSON
    })
    .then(response => response.json())  // Получаем ответ в формате JSON
    .then(data => {
      const container = document.getElementById('bookings-container');
      container.innerHTML = '';  // Очистка контейнера перед добавлением новых данных
  
      if (data.reservations && data.reservations.length > 0) {
        data.reservations.forEach(reservation => {
          const bookingElement = document.createElement('div');
          bookingElement.classList.add('booking-item');
          
          // Преобразуем время и длительность
          const formattedReservationTime = formatTime(reservation.time);  // Время бронирования
          const formattedDuration = formatTime(reservation.times);  // Длительность
  
          bookingElement.innerHTML = `
            <p>Номер стола: ${reservation.table_number}</p>
            <p>Количество мест: ${reservation.seats}</p>
            <p>Дата: ${reservation.date}</p>
            <p>Час бронювання: ${formattedReservationTime}</p>
            <p>Продовжуваність бронювання: ${formattedDuration}</p>
          `;
          container.appendChild(bookingElement);
        });
      } else {
        container.innerHTML = '<p>Бронирования не найдены.</p>';
      }
    })
    .catch(error => {
      console.error('Ошибка:', error);
    });
  }