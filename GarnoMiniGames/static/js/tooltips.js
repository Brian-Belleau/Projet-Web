// Active les infobulles Bootstrap (data-bs-toggle="tooltip") sur toutes les pages.
document.addEventListener("DOMContentLoaded", () => {
    document
        .querySelectorAll('[data-bs-toggle="tooltip"]')
        .forEach((el) => new bootstrap.Tooltip(el));
});
