document.addEventListener('DOMContentLoaded', function () {
    const baseLinkData = document.getElementById('base-links').dataset;
    
    const link = document.getElementById(baseLinkData.activelink);

    setTimeout(() => {
        link.classList.add('active-link');
    }, 50)
});
