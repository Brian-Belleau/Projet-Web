"use strict";

import { showGameResult } from "./game_result.js";

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
