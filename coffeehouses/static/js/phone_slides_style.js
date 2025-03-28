const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

if (isTouchDevice) {
  console.log('Это сенсорное устройство');
  // Убираем hover-эффекты или заменяем их
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
    const slide = mutation.target;
    if (slide.classList.contains('swiper-slide-active')) {
        const product =  slide.querySelector('#productId');
        product.style.opacity = "1";
    } else {
        const product =  slide.querySelector('#productId');
        product.style.opacity = "0";
    }
    });
    });

    // Подключаем наблюдение только к слайдам
    document.querySelectorAll('.swiper-slide').forEach((slide) => {
        observer.observe(slide, {
        attributes: true,
        attributeFilter: ['class']
        });
    });
}


        
