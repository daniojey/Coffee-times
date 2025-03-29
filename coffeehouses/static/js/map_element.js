document.addEventListener('DOMContentLoaded', () => {
    const map = document.querySelector('.navigation-block__map');
    const markIntro = document.querySelector('.map-intro');
    const markMap = document.querySelector('.mark-map');
    const mapTitle = document.querySelector('.map-title');
    const url = map.dataset.url;

    map.addEventListener('click', () => {
        window.location.href = url;
    })

    map.addEventListener('mouseenter', () => {
        markIntro.style.opacity = '1';
        mapTitle.style.opacity = '1';
        markMap.style.transform = "translate(-50%, -50%) scale(1.3)"
    })


    map.addEventListener('mouseleave', () => {
        markIntro.style.opacity = '0';
        mapTitle.style.opacity = '0';
        markMap.style.transform = "translate(-50%, -50%) scale(1)"
    })
})