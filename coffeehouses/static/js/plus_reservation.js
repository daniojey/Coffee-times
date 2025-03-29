document.addEventListener("DOMContentLoaded", function () {
    const plusBlock = document.querySelector(".navigation__info-second");
    const plusText = plusBlock.querySelector("p");
    const plusIcon = document.querySelector('.navigation__info-plus-img')
    const plusBlockData = plusBlock.dataset.url;

    plusBlock.addEventListener('click', function () {
        window.location.href = plusBlockData;
    });

    plusBlock.addEventListener('mouseenter', function () {
        plusText.style.opacity = '1';
        plusIcon.style.transform = "translate(-50%, -50%) scale(1.3)";
    });

    plusBlock.addEventListener('mouseleave', function () {
        plusText.style.opacity = '0';
        plusIcon.style.transform = "translate(-50%, -50%) scale(1)";
    });
});