document.addEventListener("DOMContentLoaded", function() {
    console.log("Scale product script loaded");
    const products = document.querySelectorAll(".product-link");

    products.forEach(link => {
        link.addEventListener('mouseenter', function() {
            link.style.transform = "scale(1.05)";
            link.style.transition = "transform 0.3s ease-in-out";

            const product  = link.querySelector('.product-context');
            if (product) {
                product.style.color = "#f5f5f5"; // Change text color to black on hover
            }
        });

        link.addEventListener('mouseleave', function() {
            link.style.transform = "scale(1)";
            link.style.transition = "transform 0.3s ease-in-out";

            const product  = link.querySelector('.product-context');
            if (product) {
                product.style.color = ""; // Change text color to black on hover
            }
        });

        
    });
});