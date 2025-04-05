const data = document.getElementById('datahouse');
const coffeeshops = JSON.parse(data.dataset.coffeeshops);
const markers = [];


// Инициализация карты
const map = L.map('map').setView([50.4501, 30.5234], 12); // Киев
            
// Добавляем слой карты (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


// Добавляем маркеры на карту
coffeeshops.forEach(loc => {
    const marker = L.marker([loc.location.lat, loc.location.lng],  { customData: loc }).addTo(map);
    const popupContent = `
    <div class="popup-content">
        <h3>${loc.name}</h3>
        <p>${loc.address}</p>
        <a href="/orders/reservation/?coffeehouse=${loc.id}" class="popup-link">Створити бронь</a>
    </div>
    `
    marker.bindPopup(popupContent);
    markers.push(marker);
})


// Добавляем обработчик события клика на маркеры
document.addEventListener('DOMContentLoaded', () => {

    const recomendedItems = document.querySelectorAll('.recomend-item');
    


    function findById(id) {

        markers.forEach(marker => {
            const customData = marker.options.customData;

            if (customData.id == id) {
                map.flyTo([customData.location.lat, customData.location.lng], 13);
                marker.openPopup();
            } 
        })

    }
    

    recomendedItems.forEach(item => {
        item.addEventListener('click', (e) => {
            findById(e.currentTarget.dataset.id);
        });
    });


    // Функция для обработки времени
    function formatTime(timeString) {
        const [hours, minutes, seconds] = timeString.split(':').map(num => parseInt(num, 10));
      
        // Формируем строку в формате 2ч 00мин
        if (hours > 0) {
          return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;  // Если есть часы, показываем их
        }
      
        return `Помилка`;  // Если нет часов, показываем минуты и секунды
      }
      


    // Добавляем обработчик события клика на маркеры
    const searchResult = document.querySelector('.search-coffeehouses');

    const searchForm = document.getElementById('search-form');
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        searchResult.innerHTML = '';
        searchResult.style.marginBottom = '20px';

        let totalMatches = 0;

        const h3Element = document.createElement('h3');
        h3Element.textContent = 'Результати пошуку:';
        h3Element.style.opacity = '1';
        searchResult.appendChild(h3Element);

        
        const inputdata = searchForm.querySelector('input').value.toLowerCase();

        // Сначала считаем общее количество совпадений
        markers.forEach(marker => {
            const customData = marker.options.customData;
            if (customData.name.toLowerCase().includes(inputdata) || 
            customData.address.toLowerCase().includes(inputdata)) {
                totalMatches++;
            }
        });

        let delay = 0;
        markers.forEach(marker => {
            const customData = marker.options.customData;
            const name = customData.name.toLowerCase();
            const address = customData.address.toLowerCase();

            if (name.includes(inputdata) || address.includes(inputdata)) {
                setTimeout(() => {
                    const searchElement = document.createElement('div');
                    searchElement.innerHTML = `
                    <div class="search-item" data-id="${customData.id}">
                    <div class="recomend-item__img">
                        <img src="${customData.image}" alt="Кав'ярня ${customData.name}" id='coffeehouse-image'>
                    </div>
                    <div class="recomend-item__info">
                        <div class="recomend-item__info__address">
                            <p>Адресса:</p>
                            <p>${address}</p>
                        </div>
                        
                        <p>Графік роботи:  ${formatTime(customData.opening_time)} - ${formatTime(customData.closing_time)}</p>
                        <p>Вихідні: Суббота|Неділя</p>
                    </div>
                    </div>
                    `

                    searchElement.addEventListener('click', (e) => {
                        findById(customData.id);
                    });

                    searchResult.appendChild(searchElement);

                }, delay)

                delay += 100; // Затримка в 100 мс між додаваннями
                
                
                
            }
        });

        // Если нет совпадений сразу
        if (totalMatches === 0) {
            checkResults();
        }

        // Функция проверки результатов
        function checkResults() {
            const items = searchResult.querySelectorAll('.search-item');
            if (items.length === 0) {
                const noResults = document.createElement('div');
                noResults.classList.add('search-no-results');
                noResults.textContent = 'Нічого не знайдено';
                searchResult.appendChild(noResults);
            }
        }
    });


    

});

