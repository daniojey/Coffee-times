const baseLinkData = document.getElementById('base-links').dataset;

const link = document.getElementById(baseLinkData.activelink);
link.classList.add('active-link');