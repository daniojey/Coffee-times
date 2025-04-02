document.addEventListener('DOMContentLoaded', function () {
    const baseLinkData = document.getElementById('base-links').dataset;
    console.log(baseLinkData)
    console.log(baseLinkData.activelink)
    
    const link = document.getElementById(baseLinkData.activelink);
    console.log(link)

    setTimeout(() => {
        link.classList.add('active-link');
    }, 50)
});
