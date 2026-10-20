"use strict";

const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(
  `${protocol}://${window.location.host}/ws/games/premier-clic/${roomName}/`,
);

const statusEl = document.getElementById("game-status");
const scoreEl = document.getElementById("game-score");
const btn = document.getElementById("click-btn");
const resultEl = document.getElementById("game-result");
const resultTitleEl = document.getElementById("result-title");
const countdownEl = document.getElementById("countdown");
let gameOver = false;

btn.style.display = "none";
statusEl.textContent = "Connexion...";

socket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  switch (data.event) {
    case "player_joined":
      statusEl.textContent =
        data.count < 2
          ? "En attente d'un adversaire..."
          : `${data.count}/2 joueurs connectés...`;
      break;
    case "waiting":
      statusEl.textContent = "Prépare-toi...";
      btn.style.display = "none";
      break;
    case "show_button":
      statusEl.textContent = "CLIQUE MAINTENANT !";
      btn.style.display = "inline-block";
      break;
    case "round_result": {
      btn.style.display = "none";
      statusEl.textContent = `${data.winner} a gagné la manche !`;
      scoreEl.textContent = Object.entries(data.scores)
        .map(([name, s]) => `${name}: ${s}`)
        .join(" — ");

      if (data.game_over) {
        gameOver = true;
        resultTitleEl.textContent = `${data.winner} a gagné la partie !`;
        countdownEl.textContent = "5";
        resultEl.classList.remove("d-none");

        let countdown = 5;

        const redirectInterval = setInterval(() => {
          countdown--;

          if (countdown > 0) {
            countdownEl.textContent = countdown;
          } else {
            clearInterval(redirectInterval);
            window.location.href = "/";
          }
        }, 1000);
      }

      break;
    }
    case "rejected":
      gameOver = true;
      btn.style.display = "none";
      statusEl.textContent = data.message;
      statusEl.classList.add("text-danger");
      break;
    case "opponent_left": {
      btn.style.display = "none";
      gameOver = true;

      resultTitleEl.textContent = "Ton adversaire a quitté la partie.";
      countdownEl.textContent = "5";
      resultEl.classList.remove("d-none");

      let countdown = 5;

      const redirectInterval = setInterval(() => {
        countdown--;

        if (countdown > 0) {
          countdownEl.textContent = countdown;
        } else {
          clearInterval(redirectInterval);
          window.location.href = "/";
        }
      }, 1000);

      break;
    }
  }
};

socket.onclose = () => {
  if (gameOver) return;
  statusEl.textContent =
    "Connexion fermée (salle pleine ou serveur indisponible).";
  btn.style.display = "none";
};

btn.addEventListener("click", () => {
  btn.style.display = "none";
  socket.send(JSON.stringify({ action: "click" }));
});

// Permet la déconnexion lorsque le joueur quitte la page
window.addEventListener("pagehide", () => {
  gameOver = true;
  socket.close(1000);
});

window.addEventListener("pageshow", (e) => {
  if (e.persisted) window.location.reload();
});

const copyButton = document.getElementById("copy-room-code");

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(roomName);
    copyButton.textContent = "Copié !";

    setTimeout(() => {
      copyButton.textContent = "Copier";
    }, 1500);
  } catch {
    copyButton.textContent = "Erreur";

    setTimeout(() => {
      copyButton.textContent = "Copier";
    }, 1500);
  }
});
