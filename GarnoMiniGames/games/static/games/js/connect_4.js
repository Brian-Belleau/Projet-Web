'use strict';

const boardEl = document.getElementById('board');
const infoEl = document.getElementById('game-info');
const columnButtons = document.querySelectorAll('.connect4-column-btn');
const cells = document.querySelectorAll('.connect4-cell');

const COLS = 7;
const cellAt = (row, col) => cells[row * COLS + col];

let mySymbol = null;
let myName = null;
let currentTurn = null;
let lastBoard = null;

function updateColumnButtons() {
  if (!lastBoard) return;
  for (const button of columnButtons) {
    const column = Number(button.dataset.column);
    button.disabled =
      game.isOver() || currentTurn !== mySymbol || lastBoard[0][column] !== '';
  }
}

function renderBoard(board) {
  lastBoard = board;
  board.forEach((rowValues, row) => {
    rowValues.forEach((value, col) => {
      const cell = cellAt(row, col);
      cell.classList.remove('connect4-red', 'connect4-yellow', 'connect4-win');
      if (value === 'R') cell.classList.add('connect4-red');
      else if (value === 'Y') cell.classList.add('connect4-yellow');
    });
  });
  updateColumnButtons();
}

function updateTurnStatus() {
  game.statusEl.textContent =
    currentTurn === mySymbol ? 'À ton tour !' : "Au tour de l'adversaire...";
  updateColumnButtons();
}

const game = window.GameCommon.start({
  path: 'connect-4',
  onAbort: () => boardEl.classList.add('d-none'),
  onEvent(data) {
    switch (data.event) {
      case 'game_start':
        mySymbol = data.you;
        myName = data.players[mySymbol];
        currentTurn = data.turn;
        boardEl.classList.remove('d-none');
        infoEl.textContent =
          mySymbol === 'R'
            ? 'Tu joues avec les jetons rouges.'
            : 'Tu joues avec les jetons jaunes.';
        renderBoard(data.board);
        updateTurnStatus();
        break;

      case 'move_made':
        currentTurn = data.turn;
        renderBoard(data.board);
        updateTurnStatus();
        break;

      case 'game_over': {
        let title = 'Match nul !';
        if (!data.draw) {
          title = data.winner === myName ? 'Tu as gagné !' : 'Tu as perdu !';
        }

        game.end(title);
        renderBoard(data.board);
        data.line?.forEach(([row, col]) =>
          cellAt(row, col)?.classList.add('connect4-win'),
        );
        break;
      }
    }
  },
});

for (const button of columnButtons) {
  button.addEventListener('click', () => {
    if (game.isOver() || currentTurn !== mySymbol) return;
    game.send({ action: 'move', column: Number(button.dataset.column) });
  });
}
