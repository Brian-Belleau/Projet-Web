"use strict";

const preview = document.getElementById("avatar-preview");
const photoInput = document.getElementById("id_photo");
const clearCheckbox = document.getElementById("photo-clear_id");

/**
 * Affiche une image dans l'aperçu de l'avatar.
 * @param {string} src - URL de l'image (photo choisie ou photo d'origine).
 */
function renderImage(src) {
    preview.innerHTML = '<img src="' + src + '" alt="Aperçu de la photo de profil" class="avatar avatar-lg">';
}

/**
 * Affiche l'initiale du pseudonyme dans l'aperçu quand il n'y a pas de photo.
 */
function renderPlaceholder() {
    let initial = "?";
    if (preview.dataset.initial) {
        initial = preview.dataset.initial;
    }
    preview.innerHTML = '<span class="avatar avatar-lg" aria-hidden="true">' + initial + '</span>';
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

const MAX_PHOTO_SIZE = 5 * 1024 * 1024;
const USERNAME_PATTERN = /^[\w.@+-]+$/;
const PSEUDONYM_PATTERN = /^[\w.@+-]+$/;
const NAME_PATTERN = /^[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[ '’-][A-Za-zÀ-ÖØ-öø-ÿ]+)*$/;

/**
 * Fonctions de validation explicites
 */
function validateUsername(value) {
    if (!value.trim()) {
        return "Ce champ est obligatoire.";
    }
    if (value.length > 150) {
        return "Ce champ ne peut pas dépasser 150 caractères.";
    }
    if (!USERNAME_PATTERN.test(value.trim())) {
        return "Ce champ ne peut contenir que des lettres, chiffres et les caractères . @ + - _.";
    }
    return null;
}
const EMAIL_PATTERN = /^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*\.[A-Za-z]{2,63}$/;

function validateEmail(value, input) {
    const email = value.trim();
    if (!email) {
        return "Ce champ est obligatoire.";
    }
    if (input.validity.typeMismatch || !EMAIL_PATTERN.test(email)) {
        return "Saisissez une adresse e-mail valide.";
    }
    return null;
}

function validatePseudonym(value) {
    if (!value.trim()) {
        return "Ce champ est obligatoire.";
    }
    if (value.trim().length < 3) {
        return "Le pseudonyme doit contenir au moins 3 caractères.";
    }
    if (value.length > 30) {
        return "Le pseudonyme ne peut pas dépasser 30 caractères.";
    }
    if (!PSEUDONYM_PATTERN.test(value)) {
        return "Le pseudonyme ne peut contenir que des lettres, chiffres et les caractères . @ + - _ (sans espace).";
    }
    return null;
}

function validateName(value) {
    if (value.trim() === "") {
        return null;
    }
    if (value.trim().length > 150) {
        return "Ce champ ne peut pas dépasser 150 caractères.";
    }
    if (!NAME_PATTERN.test(value.trim())) {
        return "Ce champ ne doit contenir que des lettres, espaces, traits d'union ou apostrophes (pas de chiffres ni de caractères spéciaux).";
    }
    return null;
}

function validateBio(value) {
    if (value.length > 160) {
        return "La biographie ne peut pas dépasser 160 caractères.";
    }
    return null;
}

/**
 * Configuration des champs sous forme d'objet classique
 */
const FIELD_CONFIGS = {
    "id_username": {
        validate: validateUsername,
        availability: {
            url: "/accounts/api/verifier-nom-utilisateur/",
            param: "username",
            message: "Ce nom d'utilisateur est déjà utilisé."
        }
    },
    "id_email": {
        validate: validateEmail,
        availability: {
            url: "/accounts/api/verifier-courriel/",
            param: "email",
            message: "Cette adresse courriel est déjà utilisée."
        }
    },
    "id_pseudonym": {
        validate: validatePseudonym,
        availability: {
            url: "/accounts/api/verifier-pseudonyme/",
            param: "pseudonym",
            message: "Ce pseudonyme est déjà utilisé."
        }
    },
    "id_first_name": {
        validate: validateName
    },
    "id_last_name": {
        validate: validateName
    },
    "id_bio": {
        validate: validateBio
    }
};

/**
 * Applique is-valid/is-invalid à un champ texte et met à jour son message d'erreur.
 */
function setTextFieldState(input, errorMessage) {
    const feedback = document.querySelector('.invalid-feedback[data-field="' + input.id + '"]');
    input.classList.remove("is-valid", "is-invalid");

    if (errorMessage) {
        input.classList.add("is-invalid");
    } else {
        input.classList.add("is-valid");
    }

    if (feedback) {
        if (errorMessage) {
            feedback.textContent = errorMessage;
        } else {
            feedback.textContent = "";
        }
    }
}

/**
 * Valide un champ texte selon sa configuration et met à jour son état visuel.
 */
function validateTextField(input) {
    const config = FIELD_CONFIGS[input.id];
    if (config) {
        const errorMessage = config.validate(input.value, input);
        setTextFieldState(input, errorMessage);
        return errorMessage === null;
    }
    return true;
}

/**
 * Valide le champ photo.
 */
function validatePhotoField(input) {
    const feedback = document.getElementById("photo-error");
    const file = input.files[0];
    input.classList.remove("is-valid", "is-invalid");

    if (!file) {
        if (feedback) {
            feedback.textContent = "";
            feedback.classList.add("d-none");
        }
        return true;
    }

    let errorMessage = null;
    if (!file.type.startsWith("image/")) {
        errorMessage = "Le fichier doit être une image.";
    } else if (file.size > MAX_PHOTO_SIZE) {
        errorMessage = "La photo est trop volumineuse (5 Mo maximum).";
    }

    if (errorMessage) {
        input.classList.add("is-invalid");
        if (feedback) {
            feedback.textContent = errorMessage;
            feedback.classList.remove("d-none");
        }
    } else {
        input.classList.add("is-valid");
        if (feedback) {
            feedback.textContent = "";
            feedback.classList.add("d-none");
        }
    }
    return errorMessage === null;
}

const availabilityControllers = {};

/**
 * Limite les appels d'une fonction à une seule exécution après un délai d'inactivité.
 */
function debounce(fn, delay) {
    let timer = null;
    return function () {
        const context = this;
        const args = arguments;
        clearTimeout(timer);
        timer = setTimeout(function () {
            fn.apply(context, args);
        }, delay);
    };
}

/**
 * Vérifie en AJAX si la valeur d'un champ est déjà utilisée.
 */
function checkAvailability(input) {
    const config = FIELD_CONFIGS[input.id];
    let availability = null;
    if (config && config.availability) {
        availability = config.availability;
    }

    if (availability && !input.classList.contains("is-invalid")) {
        if (availabilityControllers[input.id]) {
            availabilityControllers[input.id].abort();
        }

        const controller = new AbortController();
        availabilityControllers[input.id] = controller;

        const value = input.value.trim();
        const url = availability.url + "?" + availability.param + "=" + encodeURIComponent(value);

        fetch(url, { signal: controller.signal })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Réponse réseau invalide");
                }
                return response.json();
            })
            .then(function (data) {
                if (data.available) {
                    setTextFieldState(input, null);
                } else {
                    setTextFieldState(input, availability.message);
                }
            })
            .catch(function () { });
    }
}

const debouncedCheckAvailability = debounce(checkAvailability, 400);

/**
 * Initialise la validation en direct du formulaire.
 */
function initProfileFormValidation() {
    const form = document.getElementById("profile-edit-form");
    if (form) {
        if (form.dataset.bound === "true") {
            const feedbacks = form.querySelectorAll(".invalid-feedback[data-field]");
            for (let i = 0; i < feedbacks.length; i++) {
                const feedback = feedbacks[i];
                const input = document.getElementById(feedback.dataset.field);
                if (input) {
                    if (feedback.dataset.serverError === "true") {
                        input.classList.add("is-invalid");
                    } else if (input.id !== "id_photo" && input.value.trim() !== "") {
                        input.classList.add("is-valid");
                    }
                }
            }
        }

        const fieldIds = Object.keys(FIELD_CONFIGS);
        for (let i = 0; i < fieldIds.length; i++) {
            const input = document.getElementById(fieldIds[i]);
            if (input && input.value.trim() !== "" && !input.classList.contains("is-invalid")) {
                validateTextField(input);
            }
        }

        for (let j = 0; j < fieldIds.length; j++) {
            const domId = fieldIds[j];
            const input = document.getElementById(domId);
            if (input) {
                const availability = FIELD_CONFIGS[domId].availability;

                input.addEventListener("input", function () {
                    if (validateTextField(input) && availability) {
                        debouncedCheckAvailability(input);
                    }
                });

                input.addEventListener("blur", function () {
                    if (validateTextField(input) && availability) {
                        checkAvailability(input);
                    }
                });
            }
        }

        if (photoInput) {
            photoInput.addEventListener("change", function () {
                validatePhotoField(photoInput);
            });
        }

        form.addEventListener("submit", function (event) {
            let textFieldsValid = true;

            for (let k = 0; k < fieldIds.length; k++) {
                const input = document.getElementById(fieldIds[k]);
                if (input) {
                    const isValid = validateTextField(input);
                    if (!isValid) {
                        textFieldsValid = false;
                    }
                }
            }

            let photoValid = true;
            if (photoInput) {
                photoValid = validatePhotoField(photoInput);
            }

            if (!textFieldsValid || !photoValid) {
                event.preventDefault();
                const firstInvalid = form.querySelector(".is-invalid");
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
        });
    }
}

initProfileFormValidation();