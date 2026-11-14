"use strict";

import { showGameResult, setupRematch } from "./game_result.js";
import { showOpponentLeftResult } from "./game_utils.js";

const gameInfo = document.getElementById("game-info");
const boardElement = document.getElementById("board");
const columnButtons = document.querySelectorAll(".connect4-column-btn");
const cells = document.querySelectorAll(".connect4-cell");

const COLS = 7;

let players = {};
let mySymbol = null;
let myName = null;
let currentTurn = null;

function cellAt(row, col) {
  return cells[row * COLS + col];
}

function updateColumnButtons(board) {
  if (!board) {
    return;
  }

  for (const button of columnButtons) {
    const column = Number(button.dataset.column);
    const columnFull = board[0][column] !== "";

    button.disabled = game.isOver() || currentTurn !== mySymbol || columnFull;
  }
}

function renderBoard(board) {
  for (let row = 0; row < board.length; row++) {
    for (let col = 0; col < board[row].length; col++) {
      const cell = cellAt(row, col);

      cell.classList.remove("connect4-red", "connect4-yellow", "connect4-win");

      if (board[row][col] === "R") {
        cell.classList.add("connect4-red");
      } else if (board[row][col] === "Y") {
        cell.classList.add("connect4-yellow");
      }
    }
  }

  updateColumnButtons(board);
}

function updateTurnStatus(board) {
  if (currentTurn === mySymbol) {
    game.statusEl.textContent = "À ton tour !";
    game.statusEl.classList.add("text-success");
  } else {
    game.statusEl.textContent = "Au tour de l'adversaire...";
    game.statusEl.classList.remove("text-success");
  }

  updateColumnButtons(board);
}

const game = globalThis.GameCommon.start({
  path: "connect-4",

  onAbort: () => boardElement.classList.add("d-none"),

  onEvent(data, game) {
    switch (data.event) {
      case "game_start":
        game.reset();
        players = data.players;
        mySymbol = data.you;
        myName = players[mySymbol];
        currentTurn = data.turn;

        boardElement.classList.remove("d-none");
        game.statusEl.classList.remove("text-danger");

        if (mySymbol === "R") {
          gameInfo.textContent = "Tu joues avec les jetons rouges.";
        } else {
          gameInfo.textContent = "Tu joues avec les jetons jaunes.";
        }

        renderBoard(data.board);
        updateTurnStatus(data.board);
        break;

      case "move_made":
        currentTurn = data.turn;
        renderBoard(data.board);
        updateTurnStatus(data.board);
        break;

      case "game_over": {
        game.finish();
        renderBoard(data.board);
        game.statusEl.classList.remove("text-success");

        const result = {
          playerOneLabel: "Joueur rouge",
          playerOne: players.R || "-",
          playerTwoLabel: "Joueur jaune",
          playerTwo: players.Y || "-",
          winner: data.draw ? "Match nul" : data.winner,
        };

        if (data.line) {
          for (const position of data.line) {
            const cell = cellAt(position[0], position[1]);

            if (cell) {
              cell.classList.add("connect4-win");
            }
          }
        }

        if (data.draw) {
          game.statusEl.textContent = "Match nul !";

          showGameResult(
            "Match nul !",
            "Aucun joueur n'a remporté la partie.",
            null,
            "🤝",
            result,
          );
        } else if (data.winner === myName) {
          game.statusEl.textContent = "Tu as gagné !";

          showGameResult(
            "Victoire !",
            "Félicitations, tu as remporté la partie !",
            data.winner,
            "🏆",
            result,
          );
        } else {
          game.statusEl.textContent = "Tu as perdu !";

          showGameResult(
            "Défaite !",
            `${data.winner} a remporté la partie.`,
            data.winner,
            "😢",
            result,
          );
        }

        break;
      }

      case "opponent_left":
        game.statusEl.classList.remove("text-success");

        showOpponentLeftResult({
          playerOneLabel: "Joueur rouge",
          playerOne: players.R || "-",
          playerTwoLabel: "Joueur jaune",
          playerTwo: players.Y || "-",
          winner: "Adversaire déconnecté",
        });
        break;
    }
  },
});

for (const button of columnButtons) {
  button.addEventListener("click", () => {
    if (game.isOver() || currentTurn !== mySymbol) {
      return;
    }

    game.send({
      action: "move",
      column: Number(button.dataset.column),
    });
  });
}

setupRematch(game);
