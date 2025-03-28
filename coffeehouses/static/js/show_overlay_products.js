document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.slide-item');

    cards.forEach(card => {
        card.addEventListener("mouseenter", (e) => {
            if (card.parentElement.classList.contains('swiper-slide-active')) {
                document.querySelectorAll('#productId').forEach(product => {
                    product.style.opacity = '0';
                })
                
                const productOverlay = card.querySelector('#productId');
                productOverlay.style.opacity = '1';
            }
        });

        card.addEventListener("mouseleave", (e) => {
            if (card.parentElement.classList.contains('swiper-slide-active')) {
                const productOverlay = card.querySelector('#productId');
                productOverlay.style.opacity = '0';
            }
        });
    });

});

