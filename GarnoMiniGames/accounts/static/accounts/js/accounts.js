'use strict'
document.addEventListener("DOMContentLoaded", function () {
    let preview = document.getElementById("avatar-preview");
    if (preview) {
        let photoInput = document.getElementById("id_photo");
        let clearCheckbox = document.getElementById("photo-clear_id");
        let initial = preview.dataset.initial || "?";
        let originalSrc = preview.dataset.originalSrc || "";
        function renderImage(src) {
            preview.innerHTML =
                '<img src="' + src + '" alt="Aperçu de la photo de profil" class="avatar avatar-lg">';
        }
        function renderPlaceholder() {
            preview.innerHTML =
                '<span class="avatar avatar-lg" aria-hidden="true">' + initial + "</span>";
        }
        if (photoInput) {
            photoInput.addEventListener("change", function () {
                let file = photoInput.files && photoInput.files[0];
                if (!file) {
                    return;
                }
                if (clearCheckbox) {
                    clearCheckbox.checked = false;
                }
                let reader = new FileReader();
                reader.onload = function (event) {
                    renderImage(event.target.result);
                };
                reader.readAsDataURL(file);
            });
        }
        if (clearCheckbox) {
            clearCheckbox.addEventListener("change", function () {
                if (clearCheckbox.checked) {
                    if (photoInput) {
                        photoInput.value = "";
                    }
                    renderPlaceholder();
                } else if (originalSrc) {
                    renderImage(originalSrc);
                }
            });
        }
    }
});