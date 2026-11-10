"use strict";

const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(
  `${protocol}://${window.location.host}/ws/games/connect-4/${roomName}/`,
);

const gameStatus = document.getElementById("game-status");
const gameInfo = document.getElementById("game-info");
const boardElement = document.getElementById("board");
const cells = document.querySelectorAll(".connect4-cell");
const columnButtons = document.querySelectorAll(".connect4-column-btn");

let players = {};
let mySymbol = null;
let myName = null;
let currentTurn = null;
let gameOver = false;

function renderBoard(board) {
  for (let row = 0; row < board.length; row++) {
    for (let col = 0; col < board[row].length; col++) {
      const cell = document.querySelector(
        `.connect4-cell[data-row="${row}"][data-column="${col}"]`,
      );

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

function updateColumnButtons(board) {
  for (const button of columnButtons) {
    const column = Number(button.dataset.column);
    const columnFull = board[0][column] !== "";

    button.disabled = gameOver || currentTurn !== mySymbol || columnFull;
  }
}

function updateTurnStatus() {
  if (gameOver) {
    return;
  }

  if (currentTurn === mySymbol) {
    gameStatus.textContent = "À ton tour !";
  } else {
    gameStatus.textContent = "Au tour de l'adversaire...";
  }

  updateColumnButtons(
    Array.from({ length: 6 }, (_, row) =>
      Array.from({ length: 7 }, (_, col) => {
        const cell = document.querySelector(
          `.connect4-cell[data-row="${row}"][data-column="${col}"]`,
        );

        if (cell.classList.contains("connect4-red")) {
          return "R";
        }

        if (cell.classList.contains("connect4-yellow")) {
          return "Y";
        }

        return "";
      }),
    ),
  );
}

socket.onopen = () => {
  gameStatus.textContent = "En attente d'un autre joueur...";
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.event) {
    case "player_joined":
      if (data.count < 2) {
        gameStatus.textContent = "En attente d'un autre joueur...";
      } else {
        gameStatus.textContent = "Préparation de la partie...";
      }
      break;

    case "game_start":
      players = data.players;
      mySymbol = data.you;
      myName = players[mySymbol];
      currentTurn = data.turn;
      gameOver = false;

      boardElement.classList.remove("d-none");

      if (mySymbol === "R") {
        gameInfo.textContent = "Tu joues avec les jetons rouges.";
      } else {
        gameInfo.textContent = "Tu joues avec les jetons jaunes.";
      }

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

      const result = {
        playerOneLabel: "Joueur rouge",
        playerOne: players.R || "-",
        playerTwoLabel: "Joueur jaune",
        playerTwo: players.Y || "-",
        winner: data.draw ? "Match nul" : data.winner,
      };

      if (data.draw) {
        gameStatus.textContent = "Match nul !";

        showGameResult(
          "Match nul !",
          "Aucun joueur n'a remporté la partie.",
          null,
          "🤝",
          result,
        );
      } else {
        for (const position of data.line) {
          const cell = document.querySelector(
            `.connect4-cell[data-row="${position[0]}"][data-column="${position[1]}"]`,
          );

          if (cell) {
            cell.classList.add("connect4-win");
          }
        }

        if (data.winner === myName) {
          gameStatus.textContent = "Tu as gagné !";

          showGameResult(
            "Victoire !",
            "Félicitations, tu as remporté la partie !",
            data.winner,
            "🏆",
            result,
          );
        } else {
          gameStatus.textContent = "Tu as perdu !";

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
      gameOver = true;

      showOpponentLeftResult({
        playerOneLabel: "Joueur rouge",
        playerOne: players.R || "-",
        playerTwoLabel: "Joueur jaune",
        playerTwo: players.Y || "-",
        winner: "Adversaire déconnecté",
      });
      break;

    case "rejected":
      gameOver = true;
      gameStatus.textContent =
        data.message || "Impossible de rejoindre la partie.";
      gameStatus.classList.add("text-danger");
      boardElement.classList.add("d-none");
      break;
  }
};

socket.onerror = () => {
  if (!gameOver) {
    gameStatus.textContent = "Erreur de connexion au serveur.";
  }
};

socket.onclose = () => {
  if (
    !gameOver &&
    gameStatus.textContent !== "Erreur de connexion au serveur."
  ) {
    gameStatus.textContent = "Connexion fermée.";
  }
};

for (const button of columnButtons) {
  button.addEventListener("click", () => {
    if (
      gameOver ||
      currentTurn !== mySymbol ||
      socket.readyState !== WebSocket.OPEN
    ) {
      return;
    }

    socket.send(
      JSON.stringify({
        action: "move",
        column: Number(button.dataset.column),
      }),
    );
  });
}

setupRoomCodeCopy(roomName);

window.addEventListener("pagehide", () => {
  gameOver = true;
  socket.close();
});

window.addEventListener("pageshow", (event) => {
  if (event.persisted) {
    window.location.reload();
  }
});
