"use strict";

// Configure le bouton pour copier le code de la partie.
function setupRoomCodeCopy(roomName) {
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
function showOpponentLeftResult(result) {
  showGameResult(
    "Partie interrompue",
    "Ton adversaire a quitté la partie.",
    null,
    "⚠️",
    result,
  );
}
