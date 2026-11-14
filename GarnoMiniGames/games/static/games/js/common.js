"use strict";

globalThis.GameCommon = (() => {
  function setupCopyButton(roomName) {
    const button = document.getElementById("copy-room-code");

    if (!button) {
      return;
    }

    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(roomName);
        button.textContent = "Copié !";
      } catch {
        button.textContent = "Erreur";
      }
      setTimeout(() => {
        button.textContent = "Copier";
      }, 1500);
    });
  }

  /**
   * @param {string} path      segment d'URL du jeu (ex: 'connect-4')
   * @param {Function} onEvent (data, game) => void, événements propres au jeu
   * @param {Function} onAbort () => void, masquer plateau/bouton quand la partie s'arrête
   */
  function start({ path, onEvent, onAbort }) {
    const roomName = document.getElementById("room-code").dataset.roomName;
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(
      `${protocol}://${window.location.host}/ws/games/${path}/${roomName}/`,
    );

    const statusEl = document.getElementById("game-status");

    let over = false;
    const messageListeners = [];

    const game = {
      statusEl,

      isOver: () => over,

      finish() {
        over = true;
      },

      reset() {
        over = false;
      },

      send(payload) {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify(payload));
        }
      },

      onMessage(callback) {
        messageListeners.push(callback);
      },
    };

    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);

      messageListeners.forEach((callback) => callback(data));

      switch (data.event) {
        case "player_joined":
          if (data.count >= 2) globalThis.setRoomFull?.(true);
          statusEl.textContent =
            data.count < 2
              ? "En attente d'un adversaire..."
              : `${data.count}/2 joueurs connectés...`;
          return;

        case "rejected":
          game.finish();
          onAbort?.();
          statusEl.textContent =
            data.message || "Impossible de rejoindre la partie.";
          statusEl.classList.add("text-danger");
          return;

        case "opponent_left":
          game.finish();
          onAbort?.();
          onEvent(data, game);
          return;
      }

      onEvent(data, game);
    };

    socket.onclose = () => {
      if (over) return;
      statusEl.textContent =
        "Connexion fermée (salle pleine ou serveur indisponible).";
      onAbort?.();
    };

    // Déconnexion propre quand le joueur quitte la page
    window.addEventListener("pagehide", () => {
      game.finish();
      socket.close(1000);
    });

    window.addEventListener("pageshow", (e) => {
      if (e.persisted) window.location.reload();
    });

    setupCopyButton(roomName);

    return game;
  }

  return { start };
})();
