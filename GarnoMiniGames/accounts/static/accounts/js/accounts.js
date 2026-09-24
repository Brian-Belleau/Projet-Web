'use strict'

const preview = document.getElementById("avatar-preview");
const photoInput = document.getElementById("id_photo");
const clearCheckbox = document.getElementById("photo-clear_id");

/**
 * Affiche une image dans l'aperçu de l'avatar.
 * @param {string} src - URL de l'image (photo choisie ou photo d'origine).
 */
function renderImage(src) {
    preview.innerHTML = `<img src="${src}" alt="Aperçu de la photo de profil" class="avatar avatar-lg">`;
}

/**
 * Affiche l'initiale du pseudonyme dans l'aperçu quand il n'y a pas de photo.
 */
function renderPlaceholder() {
    let initial = "?";
    if (preview.dataset.initial) {
        initial = preview.dataset.initial;
    }
    preview.innerHTML = `<span class="avatar avatar-lg" aria-hidden="true">${initial}</span>`;
}

/**
 * Gère le choix d'un fichier : décoche « effacer » et affiche la nouvelle photo.
 */
function onPhotoChange() {
    const file = photoInput.files[0];
    if (file) {
        if (clearCheckbox) {
            clearCheckbox.checked = false;
        }
        renderImage(URL.createObjectURL(file));
    }
}

/**
 * Gère la checkbox « effacer » : si elle est cochée, vide le fichier choisi
 * et affiche l'initiale, sinon remet la photo d'origine.
 */
function onClearChange() {
    const originalSrc = preview.dataset.originalSrc;
    if (clearCheckbox.checked) {
        photoInput.value = "";
        renderPlaceholder();
    } else if (originalSrc) {
        renderImage(originalSrc);
    }
}

if (preview && photoInput) {
    photoInput.addEventListener("change", onPhotoChange);
    if (clearCheckbox) {
        clearCheckbox.addEventListener("change", onClearChange);
    }
}