addEventListener('DOMContentLoaded', () => {
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    if (isTouchDevice) {
        const plusText = document.querySelector(".navigation__info-second").querySelector("p");
        const plusIcon = document.querySelector('.navigation__info-plus-img')

        const searchP = document.querySelector('.navigation__info-first').querySelector('p');
        const searchIcon = document.querySelector('.navigation__info-search-img')

        const markIntro = document.querySelector('.map-intro');
        const markMap = document.querySelector('.mark-map');
        const mapTitle = document.querySelector('.map-title');

        plusText.style.opacity = "1";
        searchP.style.opacity = "1";
        markIntro.style.opacity = '1';
        mapTitle.style.opacity = '1';
    
        plusIcon.style.transform = "translate(-50%, -50%) scale(1.3)"
        searchIcon.style.transform = "translate(-50%, -50%) scale(1.3)"
        markMap.style.transform = "translate(-50%, -50%) scale(1.3)"
    }
   
});