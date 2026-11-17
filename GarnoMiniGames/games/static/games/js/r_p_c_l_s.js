"use strict";

import { showGameResult, setupRematch } from "./game_result.js";
import { showOpponentLeftResult } from "./game_utils.js";

const boardEl = document.getElementById("board");
const infoEl = document.getElementById("game-info");
const reasonEl = document.getElementById("rpcls-reason");
const meNameEl = document.getElementById("rpcls-me-name");
const meIconEl = document.getElementById("rpcls-me-icon");
const opponentNameEl = document.getElementById("rpcls-opponent-name");
const opponentIconEl = document.getElementById("rpcls-opponent-icon");
const choiceButtons = boardEl.querySelectorAll(".rpcls-choice");

const ICONS = {
    roche: "🪨",
    papier: "📄",
    ciseaux: "✂️",
    lezard: "🦎",
    spock: "🖖",
};
const UNKNOWN_ICON = "❔";
const GAME_OVER_DELAY_MS = 2000;

let names = { me: "Toi", opponent: "Adversaire" };
let scores = { me: 0, opponent: 0 };
let canChoose = false;
let gameOverTimeout = null;

function renderScore() {
    infoEl.textContent = `${names.me} : ${scores.me} — ${names.opponent} : ${scores.opponent}`;
}

function setChoicesEnabled(enabled) {
    canChoose = enabled;
    choiceButtons.forEach((button) => {
        button.disabled = !enabled;
    });
}

// Remet l'arène à zéro pour une nouvelle manche.
function resetArena() {
    meIconEl.textContent = UNKNOWN_ICON;
    opponentIconEl.textContent = UNKNOWN_ICON;
    meIconEl.classList.remove("rpcls-winner", "rpcls-loser");
    opponentIconEl.classList.remove("rpcls-winner", "rpcls-loser");
    reasonEl.textContent = "";
    choiceButtons.forEach((button) => button.classList.remove("rpcls-selected"));
}

function getResultDetails(winnerLabel) {
    return {
        playerOneLabel: names.me,
        playerOne: `${scores.me} manche${scores.me > 1 ? "s" : ""}`,
        playerTwoLabel: names.opponent,
        playerTwo: `${scores.opponent} manche${scores.opponent > 1 ? "s" : ""}`,
        winner: winnerLabel,
    };
}

const game = globalThis.GameCommon.start({
    path: "r-p-c-l-s",

    onAbort: () => {
        clearTimeout(gameOverTimeout);
        setChoicesEnabled(false);
        boardEl.classList.add("d-none");
    },

    onEvent(data, game) {
        switch (data.event) {
            case "round_start":
                if (data.round === 1) {
                    game.reset();
                    resetArena();
                }
                names = { me: data.you, opponent: data.opponent };
                scores = { me: data.my_score, opponent: data.opponent_score };

                meNameEl.textContent = names.me;
                opponentNameEl.textContent = names.opponent;
                renderScore();

                // Le résultat de la manche précédente reste affiché jusqu'au
                // prochain choix du joueur.
                boardEl.classList.remove("d-none");
                setChoicesEnabled(true);
                game.statusEl.classList.remove("text-success", "text-danger");
                game.statusEl.textContent = `Manche ${data.round} — fais ton choix !`;
                break;

            case "player_chose":
                if (data.by_you) {
                    game.statusEl.textContent =
                        "Choix verrouillé, en attente de l'adversaire...";
                }
                break;

            case "round_result": {
                setChoicesEnabled(false);

                scores = { me: data.my_score, opponent: data.opponent_score };
                renderScore();

                meIconEl.textContent = ICONS[data.my_choice];
                opponentIconEl.textContent = ICONS[data.opponent_choice];
                meIconEl.classList.toggle("rpcls-winner", data.outcome === "win");
                meIconEl.classList.toggle("rpcls-loser", data.outcome === "loss");
                opponentIconEl.classList.toggle("rpcls-winner", data.outcome === "loss");
                opponentIconEl.classList.toggle("rpcls-loser", data.outcome === "win");

                const headline = {
                    win: "Tu gagnes la manche !",
                    loss: "Tu perds la manche...",
                    draw: "Même choix : on rejoue la manche !",
                }[data.outcome];
                reasonEl.textContent = data.reason
                    ? `${headline} ${data.reason}.`
                    : headline;

                if (data.game_over) {
                    game.finish();
                    const iWon = data.outcome === "win";
                    const winnerName = iWon ? names.me : names.opponent;
                    game.statusEl.textContent = headline;

                    // Laisse le temps de voir la dernière manche avant le résumé.
                    gameOverTimeout = setTimeout(() => {
                        showGameResult(
                            iWon ? "Victoire !" : "Défaite !",
                            iWon
                                ? "Félicitations, tu as remporté la partie !"
                                : `${winnerName} a remporté la partie.`,
                            winnerName,
                            iWon ? "🏆" : "😢",
                            getResultDetails(winnerName),
                        );
                    }, GAME_OVER_DELAY_MS);
                }
                break;
            }

            case "rematch_started":
                clearTimeout(gameOverTimeout);
                game.reset();
                scores = { me: 0, opponent: 0 };
                resetArena();
                infoEl.textContent = "";
                break;

            case "opponent_left":
                clearTimeout(gameOverTimeout);
                setChoicesEnabled(false);
                showOpponentLeftResult(getResultDetails("Adversaire déconnecté"));
                break;
        }
    },
});

choiceButtons.forEach((button) => {
    button.addEventListener("click", () => {
        if (game.isOver() || !canChoose) {
            return;
        }

        setChoicesEnabled(false);
        resetArena();
        button.classList.add("rpcls-selected");
        meIconEl.textContent = ICONS[button.dataset.choice];

        game.send({ action: "choose", choice: button.dataset.choice });
    });
});

setupRematch(game);