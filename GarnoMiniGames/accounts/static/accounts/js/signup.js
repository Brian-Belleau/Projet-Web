"use strict";

const USERNAME_PATTERN = /^[\w.@+-]+$/;

/**
 * Fonctions de validation explicites (validation côté client, la validation
 * finale est toujours faite par le serveur lors de l'envoi AJAX).
 */
function validateUsername(value) {
    let error = null;
    if (!value.trim()) {
        error = "Ce champ est obligatoire.";
    } else if (value.length > 150) {
        error = "Ce champ ne peut pas dépasser 150 caractères.";
    } else if (!USERNAME_PATTERN.test(value)) {
        error = "Ce champ ne peut contenir que des lettres, chiffres et les caractères . @ + - _.";
    }
    return error;
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

function validatePassword1(value) {
    let error = null;
    if (!value) {
        error = "Ce champ est obligatoire.";
    } else if (value.length < 8) {
        error = "Le mot de passe doit contenir au moins 8 caractères.";
    } else if (/^\d+$/.test(value)) {
        error = "Le mot de passe ne peut pas être entièrement numérique.";
    }
    return error;
}

function validatePassword2(value) {
    const password1Input = document.getElementById("id_password1");
    let error = null;
    if (!value) {
        error = "Ce champ est obligatoire.";
    } else if (password1Input && value !== password1Input.value) {
        error = "Les deux mots de passe ne correspondent pas.";
    }
    return error;
}

/**
 * Configuration des champs sous forme d'objet classique.
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
    "id_password1": {
        validate: validatePassword1
    },
    "id_password2": {
        validate: validatePassword2
    }
};

/**
 * Applique is-valid/is-invalid à un champ et met à jour son message d'erreur.
 */
function setFieldState(input, errorMessage) {
    const feedback = document.querySelector('.invalid-feedback[data-field="' + input.id + '"]');
    input.classList.remove("is-valid", "is-invalid");

    if (errorMessage) {
        input.classList.add("is-invalid");
    } else {
        input.classList.add("is-valid");
    }

    if (feedback) {
        feedback.textContent = errorMessage || "";
    }
}

/**
 * Valide un champ selon sa configuration et met à jour son état visuel.
 */
function validateField(input) {
    const config = FIELD_CONFIGS[input.id];
    if (config) {
        const errorMessage = config.validate(input.value, input);
        setFieldState(input, errorMessage);
        return errorMessage === null;
    }
    return true;
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
                    setFieldState(input, null);
                } else {
                    setFieldState(input, availability.message);
                }
            })
            .catch(function () { });
    }
}

const debouncedCheckAvailability = debounce(checkAvailability, 400);

/**
 * Affiche les erreurs renvoyées par le serveur après un envoi AJAX.
 */
function applyServerErrors(errors) {
    const nonFieldBox = document.getElementById("signup-non-field-errors");
    const fieldIds = Object.keys(FIELD_CONFIGS);

    for (let i = 0; i < fieldIds.length; i++) {
        const input = document.getElementById(fieldIds[i]);
        if (input) {
            setFieldState(input, null);
        }
    }
    if (nonFieldBox) {
        nonFieldBox.innerHTML = "";
        nonFieldBox.classList.add("d-none");
    }

    if (errors) {
        Object.keys(errors).forEach(function (fieldName) {
            const messages = errors[fieldName];
            const message = Array.isArray(messages) ? messages.join(" ") : String(messages);

            if (fieldName === "__all__") {
                if (nonFieldBox) {
                    const p = document.createElement("p");
                    p.className = "mb-0";
                    p.textContent = message;
                    nonFieldBox.appendChild(p);
                    nonFieldBox.classList.remove("d-none");
                }
            } else {
                const input = document.getElementById("id_" + fieldName);
                if (input) {
                    setFieldState(input, message);
                } else if (nonFieldBox) {
                    const p = document.createElement("p");
                    p.className = "mb-0";
                    p.textContent = message;
                    nonFieldBox.appendChild(p);
                    nonFieldBox.classList.remove("d-none");
                }
            }
        });

        const firstInvalid = document.querySelector("#signup-form .is-invalid");
        if (firstInvalid) {
            firstInvalid.focus();
        }
    }
}

/**
 * Active/désactive l'état de chargement du bouton d'envoi.
 */
function setSubmitLoading(isLoading) {
    const button = document.getElementById("signup-submit-btn");
    const spinner = document.getElementById("signup-submit-spinner");
    const label = document.getElementById("signup-submit-label");

    if (button) {
        button.disabled = isLoading;
    }
    if (spinner) {
        spinner.classList.toggle("d-none", !isLoading);
    }
    if (label) {
        label.textContent = isLoading ? "Inscription en cours…" : "S'inscrire";
    }
}

/**
 * Envoie le formulaire d'inscription en AJAX.
 */
function submitSignupForm(form) {
    setSubmitLoading(true);

    fetch(form.action || window.location.href, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        body: new FormData(form),
    })
        .then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, data: data };
            });
        })
        .then(function (result) {
            if (result.ok && result.data.success) {
                window.location.href = result.data.redirect_url || "/";
            } else {
                applyServerErrors(result.data.errors);
                setSubmitLoading(false);
            }
        })
        .catch(function () {
            const nonFieldBox = document.getElementById("signup-non-field-errors");
            if (nonFieldBox) {
                nonFieldBox.textContent = "Une erreur est survenue. Veuillez réessayer.";
                nonFieldBox.classList.remove("d-none");
            }
            setSubmitLoading(false);
        });
}

/**
 * Initialise la validation en direct et l'envoi AJAX du formulaire.
 */
function initSignupFormValidation() {
    const form = document.getElementById("signup-form");
    if (form) {
        if (form.dataset.bound === "true") {
            const feedbacks = form.querySelectorAll(".invalid-feedback[data-field]");
            for (let i = 0; i < feedbacks.length; i++) {
                const feedback = feedbacks[i];
                const input = document.getElementById(feedback.dataset.field);
                if (input) {
                    if (feedback.dataset.serverError === "true") {
                        input.classList.add("is-invalid");
                    } else {
                        input.classList.add("is-valid");
                    }
                }
            }
        }

        const fieldIds = Object.keys(FIELD_CONFIGS);
        for (let j = 0; j < fieldIds.length; j++) {
            const domId = fieldIds[j];
            const input = document.getElementById(domId);
            if (input) {
                const availability = FIELD_CONFIGS[domId].availability;

                input.addEventListener("input", function () {
                    if (validateField(input) && availability) {
                        debouncedCheckAvailability(input);
                    }
                    if (domId === "id_password1") {
                        const password2Input = document.getElementById("id_password2");
                        if (password2Input && password2Input.value) {
                            validateField(password2Input);
                        }
                    }
                });

                input.addEventListener("blur", function () {
                    if (validateField(input) && availability) {
                        checkAvailability(input);
                    }
                });
            }
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();

            let allValid = true;
            for (let k = 0; k < fieldIds.length; k++) {
                const input = document.getElementById(fieldIds[k]);
                if (input) {
                    const isValid = validateField(input);
                    if (!isValid) {
                        allValid = false;
                    }
                }
            }

            if (!allValid) {
                const firstInvalid = form.querySelector(".is-invalid");
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            } else {
                submitSignupForm(form);
            }
        });
    }
}

initSignupFormValidation();