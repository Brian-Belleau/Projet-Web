"use strict";

import { showGameResult, setupRematch } from "./game_result.js";
import { showOpponentLeftResult } from "./game_utils.js";

const btn = document.getElementById("click-btn");
const scoreEl = document.getElementById("game-info");

let currentScores = {};

function showButton(visible) {
  btn.classList.toggle("d-none", !visible);
}

// Prépare les informations à afficher dans le résumé.
function getResultDetails(winner) {
  const players = Object.entries(currentScores);

  return {
    playerOneLabel: "Joueur 1",
    playerOne: players[0] ? `${players[0][0]} — ${players[0][1]} points` : "-",
    playerTwoLabel: "Joueur 2",
    playerTwo: players[1] ? `${players[1][0]} — ${players[1][1]} points` : "-",
    winner: winner,
  };
}

const game = globalThis.GameCommon.start({
  path: "premier-clic",

  onAbort: () => showButton(false),

  onEvent(data, game) {
    switch (data.event) {
      case "waiting":
        game.statusEl.textContent = "Prépare-toi...";
        showButton(false);
        break;

      case "game_start":
        currentScores = data.scores;

        scoreEl.textContent = Object.entries(currentScores)
          .map(([name, score]) => `${name}: ${score}`)
          .join(" — ");

        break;

      case "rematch_started":
        game.reset();
        currentScores = {};
        scoreEl.textContent = "";
        showButton(false);
        break;

      case "show_button":
        game.statusEl.textContent = "CLIQUE MAINTENANT !";
        showButton(true);
        break;

      case "round_result": {
        showButton(false);

        game.statusEl.textContent = `${data.winner} a gagné la manche !`;

        currentScores = data.scores;

        scoreEl.textContent = Object.entries(data.scores)
          .map(([name, score]) => `${name}: ${score}`)
          .join(" — ");

        if (data.game_over) {
          game.finish();

          if (data.you_won) {
            showGameResult(
              "Victoire !",
              "Félicitations, tu as remporté la partie !",
              data.winner,
              "🏆",
              getResultDetails(data.winner),
            );
          } else {
            showGameResult(
              "Défaite !",
              `${data.winner} a remporté la partie.`,
              data.winner,
              "😢",
              getResultDetails(data.winner),
            );
          }
        }

        break;
      }

      case "opponent_left":
        showOpponentLeftResult(getResultDetails("Adversaire déconnecté"));
        break;
    }
  },
});

btn.addEventListener("click", () => {
  showButton(false);
  game.send({ action: "click" });
});

setupRematch(game);
