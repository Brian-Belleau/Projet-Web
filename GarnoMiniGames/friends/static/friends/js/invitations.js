'use strict';

/**
 * Affiche les invitations de jeu reçues sous forme de notifications Bootstrap.
 */
(function () {
  const container = document.getElementById('invitation-toasts');
  if (container) {
    const DISMISSED_KEY = 'dismissedInvitations';

    /**
     * Charge la liste des identifiants d'invitations rejetées depuis le stockage de session.
     *
     * @returns {string[]} Tableau des clés d'invitations rejetées
     */
    function loadDismissed() {
      try {
        return JSON.parse(sessionStorage.getItem(DISMISSED_KEY)) || [];
      } catch (error) {
        console.warn('Impossible de charger les invitations rejetées :', error);
        return [];
      }
    }

    /**
     * Sauvegarde la liste des identifiants d'invitations rejetées dans le stockage de session.
     *
     * @param {string[]} ids - Tableau des clés d'invitations à enregistrer
     */
    function saveDismissed(ids) {
      try {
        sessionStorage.setItem(DISMISSED_KEY, JSON.stringify(ids));
      } catch (e) {
        console.warn('sessionStorage indisponible :', e);
      }
    }

    /**
     * Génère une clé unique pour une invitation en combinant son identifiant et son horodatage d'envoi.
     *
     * @param {Object} invitation - L'objet représentant l'invitation
     * @param {number|string} invitation.id - L'identifiant de l'invitation
     * @param {string|number} invitation.sent_at - L'horodatage d'envoi de l'invitation
     * @returns {string} La clé unique de l'invitation
     */
    function invitationKey(invitation) {
      return invitation.id + ':' + invitation.sent_at;
    }

    /**
     * Construit et retourne l'élément DOM représentant un toast de notification d'invitation.
     *
     * @param {Object} invitation - L'objet représentant l'invitation
     * @param {number|string} invitation.id - L'identifiant de l'invitation
     * @param {string} invitation.from - Le nom de l'expéditeur de l'invitation
     * @param {string} invitation.game - Le nom du jeu concerné
     * @param {string} invitation.join_url - L'URL pour rejoindre la partie
     * @returns {HTMLElement} L'élément DOM du toast créé
     */
    function buildToast(invitation) {
      const toast = document.createElement('div');
      toast.className = 'toast';
      toast.setAttribute('role', 'alert');
      toast.setAttribute('aria-live', 'assertive');
      toast.setAttribute('aria-atomic', 'true');
      toast.setAttribute('data-bs-theme', 'dark');
      toast.dataset.invitationId = invitation.id;
      toast.dataset.invitationKey = invitationKey(invitation);

      const header = document.createElement('div');
      header.className = 'toast-header';
      const title = document.createElement('strong');
      title.className = 'me-auto';
      title.textContent = 'Invitation à jouer';
      const close = document.createElement('button');
      close.type = 'button';
      close.className = 'btn-close';
      close.setAttribute('data-bs-dismiss', 'toast');
      close.setAttribute('aria-label', 'Fermer');
      header.append(title, close);

      const body = document.createElement('div');
      body.className = 'toast-body';
      const text = document.createElement('p');
      text.className = 'mb-2';
      text.textContent =
        invitation.from + " t'invite à jouer à " + invitation.game + '.';
      const join = document.createElement('a');
      join.className = 'btn btn-primary btn-sm';
      join.href = invitation.join_url;
      join.textContent = 'Rejoindre la partie';
      body.append(text, join);

      toast.append(header, body);

      toast.addEventListener('hidden.bs.toast', function () {
        const dismissed = loadDismissed();
        const key = toast.dataset.invitationKey;
        if (!dismissed.includes(key)) {
          dismissed.push(key);
          saveDismissed(dismissed);
        }
        toast.remove();
      });

      return toast;
    }

    /**
     * Met à jour les notifications affichées selon la liste reçue du serveur.
     *
     * @param {Array<{id:number, from:string, game:string, join_url:string, sent_at:string|number}>} invitations - La liste des invitations actuelles
     */
    window.renderInvitations = function (invitations) {
      const dismissed = loadDismissed();
      const wanted = invitations.filter(function (i) {
        return !dismissed.includes(invitationKey(i));
      });

      container.querySelectorAll('[data-invitation-id]').forEach(function (el) {
        const stillWanted = wanted.some(function (i) {
          return String(i.id) === el.dataset.invitationId;
        });
        if (!stillWanted) el.remove();
      });

      wanted.forEach(function (invitation) {
        const exists = container.querySelector(
          '[data-invitation-id="' + invitation.id + '"]',
        );
        if (!exists) {
          const toast = buildToast(invitation);
          container.appendChild(toast);
          new window.bootstrap.Toast(toast, { autohide: false }).show();
        }
      });
    };
  }
})();
