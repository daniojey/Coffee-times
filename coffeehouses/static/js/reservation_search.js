document.addEventListener('DOMContentLoaded', () => {
    const searchBlock = document.querySelector('.navigation__info-first');
    const searchP = searchBlock.querySelector('p');
    const searchIcon = document.querySelector('.navigation__info-search-img')
    const searchBlockData = searchBlock.dataset.url;
    
    searchBlock.addEventListener('click', () => {
        window.location.href = searchBlockData;
    })

    searchBlock.addEventListener('mouseenter', () => {
        searchP.style.opacity = '1';
        searchIcon.style.transform = 'translate(-50%, -50%) scale(1.3)';
    });

    searchBlock.addEventListener('mouseleave', () => {
        searchP.style.opacity = '0';
        searchIcon.style.transform = 'translate(-50%, -50%) scale(1)';
    });
});