window.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelectorAll(".flash");
    if (!flashes.length) return;

    window.setTimeout(() => {
        flashes.forEach((flash) => {
            flash.style.transition = "opacity 220ms ease, transform 220ms ease";
            flash.style.opacity = "0";
            flash.style.transform = "translateY(-4px)";
            window.setTimeout(() => flash.remove(), 260);
        });
    }, 4200);
});
