document.addEventListener('DOMContentLoaded', () => {
    const swiper = new Swiper('.swiper', {
        speed: 1200,
        loop: true,
        slidesPerView: 3,
        centeredSlides: true,
        navigation: {
          nextEl: '.swiper-button-next',  // кнопка следующего слайда
          prevEl: '.swiper-button-prev',  // кнопка предыдущего слайда
        },
        breakpoints: {
            // when window width is >= 0px
            0: {
                slidesPerView: 1,
                centeredSlides: false
            },
            // when window width is >= 1000px
            1000: {
                slidesPerView: 3,
                centeredSlides: true
            }
        },
      });


})