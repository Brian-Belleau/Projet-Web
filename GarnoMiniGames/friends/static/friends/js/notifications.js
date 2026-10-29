'use strict';

// Vérifie toutes les 5 s s'il y a du nouveau (demandes d'amis), sans recharger la page.
(function () {
  const pollUrl = document.currentScript.dataset.pollUrl;
  // Zones de la page rafraîchies en AJAX : liste des amis / boutons du profil.
  const LIVE_IDS = ['friends-live', 'friend-actions'];
  let lastSignature = null;

  function refreshFriendsLists() {
    const zones = LIVE_IDS.filter((id) => document.getElementById(id));
    if (zones.length === 0) {
      if (window.onFriendsRefreshed) window.onFriendsRefreshed();
      return;
    }
    fetch(window.location.href, { cache: 'no-store' })
      .then((r) => r.text())
      .then((html) => {
        const doc = new DOMParser().parseFromString(html, 'text/html');
        zones.forEach((id) => {
          const live = document.getElementById(id);
          const fresh = doc.getElementById(id);
          if (live && fresh) live.innerHTML = fresh.innerHTML;
        });
        if (window.onFriendsRefreshed) window.onFriendsRefreshed();
      })
      .catch(() => {});
  }

  // refreshOnChange=false : on met seulement l'empreinte à jour (déjà rafraîchi par l'appelant).
  function poll(refreshOnChange) {
    fetch(pollUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then((r) => {
        if (!r.ok) throw new Error('poll');
        return r.json();
      })
      .then((data) => {
        document.querySelectorAll('[data-friend-badge]').forEach((badge) => {
          badge.textContent = data.pending;
          badge.classList.toggle('d-none', data.pending === 0);
        });
        if (
          refreshOnChange &&
          lastSignature !== null &&
          data.signature !== lastSignature
        ) {
          refreshFriendsLists();
        }
        lastSignature = data.signature;
      })
      .catch(() => {});
  }

  // Utilisé par friends.js après une action AJAX (un seul rafraîchissement).
  window.refreshFriends = function () {
    refreshFriendsLists();
    poll(false);
  };

  poll(true);
  setInterval(function () {
    if (!document.hidden) poll(true);
  }, 5000);
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) poll(true);
  });
})();
