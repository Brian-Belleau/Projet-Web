"use strict";

function showGameResult(
  title,
  description,
  winner = null,
  icon = "🤝",
  result = null,
) {
  const resultEl = document.getElementById("game-result");
  const resultIconEl = document.getElementById("result-icon");
  const resultTitleEl = document.getElementById("result-title");
  const resultDescriptionEl = document.getElementById("result-description");
  const resultPlayerOneEl = document.getElementById("result-player-one");
  const resultPlayerTwoEl = document.getElementById("result-player-two");
  const resultPlayerOneLabelEl = document.getElementById(
    "result-player-one-label",
  );
  const resultPlayerTwoLabelEl = document.getElementById(
    "result-player-two-label",
  );
  const resultWinnerEl = document.getElementById("result-winner");

  resultTitleEl.textContent = title;
  resultDescriptionEl.textContent = description;
  resultIconEl.textContent = icon;

  if (result) {
    resultPlayerOneLabelEl.textContent = result.playerOneLabel;
    resultPlayerOneEl.textContent = result.playerOne;
    resultPlayerTwoLabelEl.textContent = result.playerTwoLabel;
    resultPlayerTwoEl.textContent = result.playerTwo;
    resultWinnerEl.textContent = result.winner;
  } else {
    resultWinnerEl.textContent = winner || "Match nul";
  }

  resultEl.classList.remove("d-none");
}
