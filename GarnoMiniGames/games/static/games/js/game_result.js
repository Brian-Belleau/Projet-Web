"use strict";

export function showGameResult(
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

export function setupRematch(socket) {
  const rematchButton = document.getElementById("rematch-button");
  const rematchStatus = document.getElementById("rematch-status");
  const resultEl = document.getElementById("game-result");

  let countdownInterval = null;

  if (!rematchButton || !rematchStatus || !resultEl) {
    return;
  }

  function startRematchCountdown(requestedByYou) {
    clearInterval(countdownInterval);

    let secondsLeft = 30;

    function updateStatus() {
      if (requestedByYou) {
        rematchStatus.textContent = `En attente de l'adversaire... (${secondsLeft} s)`;
      } else {
        rematchStatus.textContent = `Ton adversaire propose une revanche ! (${secondsLeft} s pour accepter)`;
      }
    }

    updateStatus();

    countdownInterval = setInterval(() => {
      secondsLeft--;
      updateStatus();

      if (secondsLeft <= 0) {
        clearInterval(countdownInterval);
      }
    }, 1000);
  }

  rematchButton.addEventListener("click", () => {
    if (socket.readyState !== WebSocket.OPEN) {
      return;
    }

    socket.send(JSON.stringify({ action: "rematch" }));

    rematchButton.disabled = true;
    rematchStatus.textContent = "En attente de l'adversaire...";
    rematchStatus.classList.remove("d-none");
  });

  socket.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);

    if (data.event === "rematch_waiting") {
      rematchStatus.classList.remove("d-none");
      startRematchCountdown(data.requested_by_you);

      if (data.requested_by_you) {
        rematchButton.disabled = true;
      }
    }

    if (data.event === "rematch_started") {
      clearInterval(countdownInterval);

      resultEl.classList.add("d-none");
      rematchStatus.classList.add("d-none");
      rematchButton.disabled = false;

      const statusEl = document.getElementById("game-status");

      if (statusEl) {
        statusEl.textContent = "Prépare-toi...";
        statusEl.classList.remove("d-none");
      }
    }

    if (data.event === "rematch_expired") {
      clearInterval(countdownInterval);
      rematchStatus.textContent =
        "La demande de revanche a expiré. Vous pouvez réessayer.";
      rematchStatus.classList.remove("d-none");
      rematchButton.disabled = false;
    }
    if (data.event === "opponent_left_after_game") {
      clearInterval(countdownInterval);

      rematchButton.classList.add("d-none");
      rematchStatus.textContent =
        "Ton adversaire a déjà quitté la partie. La revanche n'est plus possible.";
      rematchStatus.classList.remove("d-none");
    }
  });
}
