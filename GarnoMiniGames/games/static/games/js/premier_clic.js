'use strict'

const roomName = "TEST123";
const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(
  `${protocol}://${window.location.host}/ws/games/premier-clic/${roomName}/`
);

const statusEl = document.getElementById("game-status");
const scoreEl = document.getElementById("game-score");
const btn = document.getElementById("click-btn");
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
      btn.style.display = "block";
      break;
    case "round_result":
      btn.style.display = "none";
      statusEl.textContent = `${data.winner} a gagné la manche !`;
      scoreEl.textContent = Object.entries(data.scores)
        .map(([name, s]) => `${name}: ${s}`)
        .join(" — ");
      if (data.game_over) {
        statusEl.textContent = `🏆 ${data.winner} a gagné la partie !`;
        gameOver = true;
      }
      break;
    case "opponent_left":
      statusEl.textContent = "Ton adversaire a quitté la partie.";
      btn.style.display = "none";
      break;
  }
};

socket.onclose = () => {
  if (gameOver) return;
  statusEl.textContent = "Connexion fermée (salle pleine ou serveur indisponible).";
  btn.style.display = "none";
};

btn.addEventListener("click", () => {
  btn.style.display = "none";
  socket.send(JSON.stringify({ action: "click" }));
});