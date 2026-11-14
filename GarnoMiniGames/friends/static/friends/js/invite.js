'use strict';

/**
 * Liste des amis de la fenêtre d'invitation.
 * @type {HTMLElement|null}
 */
const inviteList = document.getElementById('invite-friends-list');

/**
 * Zone d'affichage des messages d'erreur sous la liste.
 * @type {HTMLElement|null}
 */
const inviteStatus = document.getElementById('invite-friends-status');

/**
 * Élément de la notification (toast) de confirmation.
 * @type {HTMLElement|null}
 */
const inviteToastEl = document.getElementById('invite-sent-toast');

/**
 * Emplacement du pseudonyme dans la notification.
 * @type {HTMLElement|null}
 */
const inviteToastName = document.getElementById('invite-sent-name');

/**
 * Durée (en ms) pendant laquelle le bouton reste en état « envoyé ».
 * @type {number}
 */
const SENT_STATE_DURATION = 4000;

/**
 * Lit le jeton CSRF placé dans la page par le tag Django {% csrf_token %}.
 *
 * @returns {string} Le jeton CSRF ou une chaîne vide si absent.
 */
function getCsrfToken() {
  const field = document.querySelector('[name=csrfmiddlewaretoken]');
  return field ? field.value : '';
}

/**
 * Affiche un message sous la liste (vide le message si le texte est vide).
 *
 * @param {string} text - Le message à afficher.
 */
function setInviteStatus(text) {
  inviteStatus.textContent = text;
}

/**
 * Affiche la notification de confirmation d'envoi.
 *
 * @param {string} pseudonym - Le pseudonyme de l'ami invité.
 */
function showSentToast(pseudonym) {
  inviteToastName.textContent = pseudonym;
  globalThis.bootstrap.Toast.getOrCreateInstance(inviteToastEl).show();
}

/**
 * Passe le bouton dans l'état « Envoyée » puis le remet à l'état initial.
 *
 * @param {HTMLButtonElement} button - Le bouton d'invitation cliqué.
 * @param {string} originalHtml - Le contenu d'origine du bouton.
 */
function markButtonSent(button, originalHtml) {
  button.dataset.inviteState = 'sent';
  button.innerHTML = '<i class="bi bi-check-lg me-1"></i>Envoyée';
  button.disabled = true;

  setTimeout(function () {
    delete button.dataset.inviteState;
    button.innerHTML = originalHtml;
    button.disabled = button.dataset.online !== 'true';
  }, SENT_STATE_DURATION);
}

/**
 * Passe le bouton dans l'état « erreur » avec la possibilité de réessayer.
 *
 * @param {HTMLButtonElement} button - Le bouton d'invitation cliqué.
 * @param {string} originalHtml - Le contenu d'origine du bouton.
 */
function markButtonError(button, originalHtml) {
  button.dataset.inviteState = 'error';
  button.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Réessayer';
  button.disabled = false;
  button.dataset.originalHtml = originalHtml;
}

/**
 * Envoie l'invitation à l'ami correspondant au bouton cliqué.
 *
 * @param {HTMLButtonElement} button - Le bouton d'invitation cliqué.
 */
function sendInvite(button) {
  const row = button.closest('[data-friend-id]');
  const nameEl = row ? row.querySelector('.fw-semibold') : null;
  const pseudonym = nameEl ? nameEl.textContent.trim() : '';
  const originalHtml = button.dataset.originalHtml || button.innerHTML;

  const body = new URLSearchParams();
  body.set('room_name', inviteList.dataset.roomName || '');
  body.set('game_slug', inviteList.dataset.gameSlug || '');
  setInviteStatus('');
  delete button.dataset.inviteState;
  button.disabled = true;

  fetch(button.dataset.inviteUrl, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCsrfToken(),
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: body,
  })
    .then(function (response) {
      return response
        .json()
        .catch(function () {
          return {};
        })
        .then(function (data) {
          if (!response.ok || data.ok === false) {
            throw new Error(data.error || '');
          }
          markButtonSent(button, originalHtml);
          showSentToast(pseudonym);
        });
    })
    .catch(function (error) {
      markButtonError(button, originalHtml);
      setInviteStatus(
        error.message ||
          "L'invitation n'a pas pu être envoyée. Veuillez réessayer.",
      );
    });
}

if (inviteList && inviteStatus && inviteToastEl && inviteToastName) {
  inviteList.addEventListener('click', function (event) {
    const button = event.target.closest('button[data-invite-url]');
    if (button && !button.disabled) {
      sendInvite(button);
    }
  });
}

/**
 * Appelée par les pages de jeu quand la salle change d'état.
 * Quand la salle est pleine : ferme la fenêtre d'invitation (si ouverte),
 * retire le bouton « Inviter un ami », retire la section « Code de la partie » et rend toute invitation impossible.
 *
 * @param {boolean} full - true si la salle est pleine.
 */
globalThis.setRoomFull = function (full) {
  const openButton = document.getElementById('invite-friends-open');
  const fullNote = document.getElementById('invite-room-full');
  const modalEl = document.getElementById('invite-friends-modal');
  const codeSection = document.getElementById('room-code-section');
  if (full && codeSection) codeSection.remove();
  if (fullNote) fullNote.classList.toggle('d-none', !full);
  if (openButton && modalEl) {
    if (full) {
      globalThis.bootstrap.Modal.getOrCreateInstance(modalEl).hide();
      inviteList
        .querySelectorAll('button[data-invite-url]')
        .forEach(function (button) {
          button.disabled = true;
        });
    }
    openButton.classList.toggle('d-none', full);
    openButton.disabled = full;
  }
};
