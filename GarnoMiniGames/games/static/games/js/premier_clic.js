'use strict';

const btn = document.getElementById('click-btn');
const scoreEl = document.getElementById('game-info');

const showButton = (visible) => btn.classList.toggle('d-none', !visible);

const game = window.GameCommon.start({
  path: 'premier-clic',
  onAbort: () => showButton(false),
  onEvent(data) {
    switch (data.event) {
      case 'waiting':
        game.statusEl.textContent = 'Prépare-toi...';
        showButton(false);
        break;

      case 'show_button':
        game.statusEl.textContent = 'CLIQUE MAINTENANT !';
        showButton(true);
        break;

      case 'round_result':
        showButton(false);
        game.statusEl.textContent = `${data.winner} a gagné la manche !`;
        scoreEl.textContent = Object.entries(data.scores)
          .map(([name, s]) => `${name}: ${s}`)
          .join(' — ');
        if (data.game_over) {
          game.end(`${data.winner} a gagné la partie !`);
        }
        break;
    }
  },
});

btn.addEventListener('click', () => {
  showButton(false);
  game.send({ action: 'click' });
});
