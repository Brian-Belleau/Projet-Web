'use strict';

const boardEl = document.getElementById('board');
const infoEl = document.getElementById('game-info');
const cells = boardEl.querySelectorAll('.ttt-cell');

let mySymbol = null;
let currentTurn = null;

function renderBoard(board) {
  cells.forEach((cell, i) => {
    cell.textContent = board[i];
    cell.classList.toggle('ttt-x', board[i] === 'X');
    cell.classList.toggle('ttt-o', board[i] === 'O');
    cell.disabled =
      game.isOver() || board[i] !== '' || currentTurn !== mySymbol;
  });
}

function updateTurnStatus() {
  const myTurn = currentTurn === mySymbol;
  game.statusEl.textContent = myTurn
    ? "C'est ton tour !"
    : "Tour de l'adversaire...";
  game.statusEl.classList.toggle('text-success', myTurn);
}

const GameCommon = window.GameCommon || globalThis.GameCommon;

const game = GameCommon.start({
  path: 'tic-tac-toe',
  onAbort: () => boardEl.classList.add('d-none'),
  onEvent(data) {
    switch (data.event) {
      case 'game_start':
        mySymbol = data.you;
        currentTurn = data.turn;
        boardEl.classList.remove('d-none');
        infoEl.textContent = `Tu joues les ${mySymbol} — ${data.players.X} (X) vs ${data.players.O} (O)`;
        renderBoard(data.board);
        updateTurnStatus();
        break;

      case 'move_made':
        currentTurn = data.turn;
        renderBoard(data.board);
        updateTurnStatus();
        break;

      case 'game_over': {
        const title = data.draw
          ? 'Match nul !'
          : `${data.winner} a gagné la partie !`;

        game.end(title);
        game.statusEl.classList.remove('text-success');
        game.statusEl.textContent = data.draw ? 'Égalité !' : title;
        renderBoard(data.board);
        data.line?.forEach((i) => cells[i].classList.add('ttt-cell-win'));
        break;
      }
    }
  },
});

cells.forEach((cell) => {
  cell.addEventListener('click', () => {
    if (game.isOver() || currentTurn !== mySymbol || cell.textContent !== '')
      return;
    game.send({ action: 'move', index: Number(cell.dataset.index) });
  });
});
