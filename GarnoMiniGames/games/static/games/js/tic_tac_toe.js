"use strict";

import { showGameResult, setupRematch } from "./game_result.js";
import { setupRoomCodeCopy, showOpponentLeftResult } from "./game_utils.js";

const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(
  `${protocol}://${window.location.host}/ws/games/tic-tac-toe/${roomName}/`,
);

const statusEl = document.getElementById("game-status");
const infoEl = document.getElementById("game-info");
const boardEl = document.getElementById("board");
const cells = boardEl.querySelectorAll(".ttt-cell");

let players = {};
let gameOver = false;
let mySymbol = null;
let currentTurn = null;

statusEl.textContent = "Connexion...";

function renderBoard(board) {
  cells.forEach((cell, i) => {
    cell.textContent = board[i];
    cell.classList.toggle("ttt-x", board[i] === "X");
    cell.classList.toggle("ttt-o", board[i] === "O");
    cell.disabled = gameOver || board[i] !== "" || currentTurn !== mySymbol;
  });
}

function updateTurnStatus() {
  if (currentTurn === mySymbol) {
    statusEl.textContent = "C'est ton tour !";
    statusEl.classList.add("text-success");
  } else {
    statusEl.textContent = "Tour de l'adversaire...";
    statusEl.classList.remove("text-success");
  }
}

socket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  switch (data.event) {
    case "player_joined":
      statusEl.textContent =
        data.count < 2
          ? "En attente d'un adversaire..."
          : `${data.count}/2 joueurs connectés...`;
      break;

    case "game_start":
      gameOver = false;
      players = data.players;
      mySymbol = data.you;
      currentTurn = data.turn;

      // Retire les anciennes lignes gagnantes.
      cells.forEach((cell) => {
        cell.classList.remove("ttt-cell-win");
      });

      boardEl.classList.remove("d-none");
      infoEl.textContent = `Tu joues les ${mySymbol} — ${data.players.X} (X) vs ${data.players.O} (O)`;
      renderBoard(data.board);
      updateTurnStatus();
      break;

    case "move_made":
      currentTurn = data.turn;
      renderBoard(data.board);
      updateTurnStatus();
      break;

    case "game_over": {
      gameOver = true;
      renderBoard(data.board);
      statusEl.classList.remove("text-success");

      const result = {
        playerOneLabel: "Joueur X",
        playerOne: players.X || "-",
        playerTwoLabel: "Joueur O",
        playerTwo: players.O || "-",
        winner: data.draw ? "Match nul" : data.winner,
      };

      if (data.line) {
        data.line.forEach((i) => cells[i].classList.add("ttt-cell-win"));
      }

      if (data.draw) {
        statusEl.textContent = "Égalité !";

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
          statusEl.textContent = "Tu as gagné la partie !";

          showGameResult(
            "Victoire !",
            "Félicitations, tu as remporté la partie !",
            data.winner,
            "🏆",
            result,
          );
        } else {
          statusEl.textContent = "Tu as perdu la partie !";

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

    case "rejected":
      gameOver = true;
      boardEl.classList.add("d-none");
      statusEl.textContent = data.message;
      statusEl.classList.add("text-danger");
      break;

    case "opponent_left": {
      gameOver = true;
      boardEl.classList.add("d-none");
      statusEl.classList.remove("text-success");

      showOpponentLeftResult({
        playerOneLabel: "Joueur X",
        playerOne: players.X || "-",
        playerTwoLabel: "Joueur O",
        playerTwo: players.O || "-",
        winner: "Adversaire déconnecté",
      });

      break;
    }

    case "opponent_left_after_game":
      break;
  }
};

socket.onclose = () => {
  if (gameOver) return;
  statusEl.textContent =
    "Connexion fermée (salle pleine ou serveur indisponible).";
  boardEl.classList.add("d-none");
};

cells.forEach((cell) => {
  cell.addEventListener("click", () => {
    if (gameOver || currentTurn !== mySymbol || cell.textContent !== "") return;
    socket.send(
      JSON.stringify({ action: "move", index: Number(cell.dataset.index) }),
    );
  });
});

// Permet la déconnexion lorsque le joueur quitte la page
window.addEventListener("pagehide", () => {
  gameOver = true;
  socket.close(1000);
});

window.addEventListener("pageshow", (e) => {
  if (e.persisted) window.location.reload();
});

setupRoomCodeCopy(roomName);

setupRematch(socket);
