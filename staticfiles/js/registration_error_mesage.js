document.addEventListener('DOMContentLoaded', function () {
    // Найти все элементы с ошибками
    const errorMessages = document.querySelectorAll('.error-message');

    errorMessages.forEach(error => {
        const fieldName = error.getAttribute('data-field'); // Получаем имя поля
        const inputField = document.querySelector(`[name="${fieldName}"]`); // Находим соответствующее поле

        if (inputField) {
            inputField.classList.add('error-border'); // Добавляем класс для поля с ошибкой
        }
    });
});