document.addEventListener("DOMContentLoaded", function () {
    const deleteLinks = document.querySelectorAll(".delete-reservation-link");
    const modal = document.getElementById("deleteModal");
    const deleteForm = document.getElementById("deleteForm");
    const cancelBtn = modal.querySelector(".cancel-btn");

    deleteLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const reservationId = this.dataset.reservationId;
            const deleteUrl = `/user/delete-reservation/${reservationId}/`;
            deleteForm.action = deleteUrl;

            // Получаем координаты клика
            const rect = this.getBoundingClientRect();
            const clickX = rect.left + rect.width / 2;
            const clickY = rect.top + rect.height / 2;

            // Устанавливаем начальные позиции всплывашки
            modal.style.transformOrigin = `${clickX}px ${clickY}px`;
            modal.style.display = "flex";
            setTimeout(() => {
                modal.classList.add("show");
            }, 10); // Даем время для применения начальных стилей
        });
    });

    cancelBtn.addEventListener("click", function () {
        modal.classList.remove("show");
        setTimeout(() => {
            modal.style.display = "none";
        }, 300); // Ждем окончания анимации
    });

    window.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.classList.remove("show");
            setTimeout(() => {
                modal.style.display = "none";
            }, 300);
        }
    });
});