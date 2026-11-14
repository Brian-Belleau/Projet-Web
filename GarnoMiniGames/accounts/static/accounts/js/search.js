'use strict';

const searchForm = document.getElementById('search-form');
const minGamesInput = document.getElementById('search-min-games');
const minGamesError = document.getElementById('search-min-games-error');
const MIN_GAMES_PATTERN = /^\d{1,9}$/;

function validateMinGames(input) {
  const value = input.value.trim();
  if (input.validity.badInput) {
    return 'Entrez un nombre entier positif (0 ou plus).';
  }
  if (value !== '' && !MIN_GAMES_PATTERN.test(value)) {
    return 'Entrez un nombre entier positif (0 ou plus).';
  }
  return null;
}

function showMinGamesError(message) {
  minGamesInput.classList.toggle('is-invalid', message !== null);
  minGamesError.textContent = message ?? '';
}

minGamesInput.addEventListener('keydown', (event) => {
  if (['-', '+', 'e', 'E', '.', ','].includes(event.key)) {
    event.preventDefault();
  }
});

minGamesInput.addEventListener('input', () => {
  showMinGamesError(validateMinGames(minGamesInput));
});

searchForm.addEventListener('submit', (event) => {
  const error = validateMinGames(minGamesInput);
  showMinGamesError(error);
  if (error) {
    event.preventDefault();
    minGamesInput.focus();
  }
});
