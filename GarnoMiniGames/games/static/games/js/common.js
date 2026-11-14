'use strict';

globalThis.GameCommon = (() => {
  const REDIRECT_SECONDS = 5;
  const HOME_URL = '/';

  function setupCopyButton(roomName) {
    const button = document.getElementById('copy-room-code');

    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(roomName);
        button.textContent = 'Copié !';
      } catch {
        button.textContent = 'Erreur';
      }
      setTimeout(() => {
        button.textContent = 'Copier';
      }, 1500);
    });
  }

  /**
   * @param {string} path      segment d'URL du jeu (ex: 'connect-4')
   * @param {Function} onEvent (data, game) => void, événements propres au jeu
   * @param {Function} onAbort () => void, masquer plateau/bouton quand la partie s'arrête
   */
  function start({ path, onEvent, onAbort }) {
    const roomName = document.getElementById('room-code').dataset.roomName;
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(
      `${protocol}://${window.location.host}/ws/games/${path}/${roomName}/`,
    );

    const statusEl = document.getElementById('game-status');
    const resultEl = document.getElementById('game-result');
    const resultTitleEl = document.getElementById('result-title');
    const countdownEl = document.getElementById('countdown');

    let over = false;
    let redirectTimer = null;

    const game = {
      statusEl,

      isOver: () => over,

      send(payload) {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify(payload));
        }
      },

      // Fin de partie : affiche le résultat puis redirige vers l'accueil
      end(title) {
        over = true;
        clearInterval(redirectTimer);

        resultTitleEl.textContent = title;
        countdownEl.textContent = REDIRECT_SECONDS;
        resultEl.classList.remove('d-none');

        let remaining = REDIRECT_SECONDS;
        redirectTimer = setInterval(() => {
          remaining--;
          if (remaining > 0) {
            countdownEl.textContent = remaining;
          } else {
            clearInterval(redirectTimer);
            window.location.href = HOME_URL;
          }
        }, 1000);
      },
    };

    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);

      switch (data.event) {
        case 'player_joined':
          if (data.count >= 2) globalThis.setRoomFull?.(true);
          statusEl.textContent =
            data.count < 2
              ? "En attente d'un adversaire..."
              : `${data.count}/2 joueurs connectés...`;
          return;

        case 'rejected':
          over = true;
          onAbort?.();
          statusEl.textContent =
            data.message || 'Impossible de rejoindre la partie.';
          statusEl.classList.add('text-danger');
          return;

        case 'opponent_left':
          onAbort?.();
          statusEl.classList.remove('text-success');
          game.end('Ton adversaire a quitté la partie.');
          return;
      }

      onEvent(data, game);
    };

    socket.onclose = () => {
      if (over) return;
      statusEl.textContent =
        'Connexion fermée (salle pleine ou serveur indisponible).';
      onAbort?.();
    };

    // Déconnexion propre quand le joueur quitte la page
    window.addEventListener('pagehide', () => {
      over = true;
      clearInterval(redirectTimer);
      socket.close(1000);
    });

    window.addEventListener('pageshow', (e) => {
      if (e.persisted) window.location.reload();
    });

    setupCopyButton(roomName);

    return game;
  }

  return { start };
})();
