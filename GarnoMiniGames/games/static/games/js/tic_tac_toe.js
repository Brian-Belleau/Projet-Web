"use strict";

import { showGameResult, setupRematch } from "./game_result.js";
import { showOpponentLeftResult } from "./game_utils.js";

const boardEl = document.getElementById("board");
const infoEl = document.getElementById("game-info");
const cells = boardEl.querySelectorAll(".ttt-cell");

let players = {};
let mySymbol = null;
let currentTurn = null;

function renderBoard(board) {
  cells.forEach((cell, i) => {
    cell.textContent = board[i];
    cell.classList.toggle("ttt-x", board[i] === "X");
    cell.classList.toggle("ttt-o", board[i] === "O");
    cell.disabled =
      game.isOver() || board[i] !== "" || currentTurn !== mySymbol;
  });
}

function updateTurnStatus() {
  const myTurn = currentTurn === mySymbol;

  game.statusEl.textContent = myTurn
    ? "C'est ton tour !"
    : "Tour de l'adversaire...";

  game.statusEl.classList.toggle("text-success", myTurn);
}

const game = globalThis.GameCommon.start({
  path: "tic-tac-toe",

  onAbort: () => boardEl.classList.add("d-none"),

  onEvent(data, game) {
    switch (data.event) {
      case "game_start":
        game.reset();
        players = data.players;
        mySymbol = data.you;
        currentTurn = data.turn;

        cells.forEach((cell) => {
          cell.classList.remove("ttt-cell-win");
        });

        boardEl.classList.remove("d-none");
        infoEl.textContent = `Tu joues les ${mySymbol} — ${players.X} (X) vs ${players.O} (O)`;

        renderBoard(data.board);
        updateTurnStatus();
        break;

      case "move_made":
        currentTurn = data.turn;
        renderBoard(data.board);
        updateTurnStatus();
        break;

      case "game_over": {
        game.finish();
        renderBoard(data.board);
        game.statusEl.classList.remove("text-success");

        const result = {
          playerOneLabel: "Joueur X",
          playerOne: players.X || "-",
          playerTwoLabel: "Joueur O",
          playerTwo: players.O || "-",
          winner: data.draw ? "Match nul" : data.winner,
        };

        if (data.line) {
          data.line.forEach((i) => {
            cells[i].classList.add("ttt-cell-win");
          });
        }

        if (data.draw) {
          game.statusEl.textContent = "Égalité !";

          showGameResult(
            "Match nul !",
            "Aucun joueur n'a remporté la partie.",
            null,
            "🤝",
            result,
          );
        } else {
          const isWinner = players[mySymbol] === data.winner;

          if (isWinner) {
            game.statusEl.textContent = "Tu as gagné la partie !";

            showGameResult(
              "Victoire !",
              "Félicitations, tu as remporté la partie !",
              data.winner,
              "🏆",
              result,
            );
          } else {
            game.statusEl.textContent = "Tu as perdu la partie !";

            showGameResult(
              "Défaite !",
              `${data.winner} a remporté la partie.`,
              data.winner,
              "😢",
              result,
            );
          }
        }
        break;
      }

      case "opponent_left":
        game.statusEl.classList.remove("text-success");

        showOpponentLeftResult({
          playerOneLabel: "Joueur X",
          playerOne: players.X || "-",
          playerTwoLabel: "Joueur O",
          playerTwo: players.O || "-",
          winner: "Adversaire déconnecté",
        });
        break;
    }
  },
});

cells.forEach((cell) => {
  cell.addEventListener("click", () => {
    if (game.isOver() || currentTurn !== mySymbol || cell.textContent !== "") {
      return;
    }

    game.send({
      action: "move",
      index: Number(cell.dataset.index),
    });
  });
});

setupRematch(game);
