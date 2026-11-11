"use strict";

import { showGameResult } from "./game_result.js";

// Configure le bouton pour copier le code de la partie.
export function setupRoomCodeCopy(roomName) {
  const copyButton = document.getElementById("copy-room-code");

  copyButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(roomName);
      copyButton.textContent = "Copié !";
    } catch {
      copyButton.textContent = "Erreur";
    }

    setTimeout(() => {
      copyButton.textContent = "Copier";
    }, 1500);
  });
}

// Affiche le résultat lorsque l'adversaire quitte la partie.
export function showOpponentLeftResult(result) {
  showGameResult(
    "Partie interrompue",
    "Ton adversaire a quitté la partie.",
    null,
    "⚠️",
    result,
  );

  const rematchButton = document.getElementById("rematch-button");
  const rematchStatus = document.getElementById("rematch-status");

  if (rematchButton) {
    rematchButton.classList.add("d-none");
  }

  if (rematchStatus) {
    rematchStatus.classList.add("d-none");
  }
}
