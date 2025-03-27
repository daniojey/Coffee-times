const usernameInput = document.getElementById('username');
const passInput = document.getElementById('password');
let formContainer = document.querySelector('.form-container');
console.log(formContainer);

usernameInput.addEventListener('input', function(event) {
    formContainer.style.transition = 'background-color 0.3s ease';
    const usernameLength = usernameInput.value.length;
    const blueValue = Math.min(255, usernameLength * 10); // Ограничиваем максимум 255
    const newColor = `rgb(${blueValue}, 71, 21)`;
    
    formContainer.style.backgroundColor = newColor;
});