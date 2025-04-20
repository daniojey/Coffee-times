document.addEventListener("DOMContentLoaded", function() {
    console.log("Animation script loaded");
    const products = document.querySelectorAll('.product');
    let delay = 0;

    products.forEach((product, index) => {
        product.style.animationDelay = `${delay}s`;
        delay += 0.2; // Increase delay for each product
    })
})