"use strict";

/**
 * Structure d'un résultat de recherche de joueur.
 * @typedef {Object} SearchResult
 * @property {string} pseudonym - Le pseudonyme du joueur.
 * @property {string} profile_url - L'URL du profil du joueur.
 * @property {string} add_url - L'URL de l'API pour envoyer une demande d'ami.
 * @property {'friends'|'sent'|'received'|string} status - Le statut d'amitié avec ce joueur.
 * @property {string} [photo_url] - URL de la photo de profil (optionnel).
 * @property {string} [initial] - Initiale à afficher si la photo est absente.
 */

/**
 * Champ de saisie pour la recherche d'amis.
 * @type {HTMLInputElement|null}
 */
const searchInput = document.getElementById("friend-search");

/**
 * Conteneur d'affichage des suggestions de recherche.
 * @type {HTMLElement|null}
 */
const suggestionsBox = document.getElementById("friend-suggestions");

/**
 * Zone d'affichage des messages de statut de la recherche.
 * @type {HTMLElement|null}
 */
const statusBox = document.getElementById("friend-search-status");

/**
 * Panneau pliable contenant l'interface d'ajout d'amis.
 * @type {HTMLElement|null}
 */
const addFriendPanel = document.getElementById("add-friend-panel");

/**
 * Délai d'attente (en ms) avant le déclenchement de la recherche (anti-rebond).
 * @type {number}
 */
const SEARCH_DELAY = 300;

/**
 * Contrôleur permettant d'annuler les requêtes HTTP en cours.
 * @type {AbortController|null}
 */
let searchController = null;

/**
 * Limite les appels d'une fonction à une seule exécution après un délai d'inactivité.
 *
 * @param {Function} fn - La fonction à exécuter après le délai.
 * @param {number} delay - Le délai d'attente en millisecondes.
 * @returns {Function} La fonction enveloppée avec la logique de debounce.
 */
function debounce(fn, delay) {
  let timer = null;
  return function () {
    const context = this;
    const args = arguments;
    clearTimeout(timer);
    timer = setTimeout(function () {
      fn.apply(context, args);
    }, delay);
  };
}

/**
 * Lit le jeton CSRF placé dans la page par le tag Django {% csrf_token %}.
 *
 * @returns {string} Le jeton CSRF ou une chaîne vide si absent.
 */
function getCsrfToken() {
  const field = document.querySelector("[name=csrfmiddlewaretoken]");
  return field ? field.value : "";
}

/**
 * Affiche un message sous le champ de recherche (vide le message si le texte est vide).
 *
 * @param {string} text - Le texte du message à afficher.
 */
function setStatusMessage(text) {
  statusBox.textContent = text;
}

/**
 * Crée l'élément d'avatar d'un joueur (image de photo ou élément conteneur d'initiale).
 *
 * @param {SearchResult} result - Le joueur dont on extrait l'avatar.
 * @returns {HTMLElement} L'élément HTML `<img>` ou `<span>` représentant l'avatar.
 */
function buildAvatar(result) {
  let avatar;
  if (result.photo_url) {
    avatar = document.createElement("img");
    avatar.src = result.photo_url;
    avatar.alt = "Photo de " + result.pseudonym;
  } else {
    avatar = document.createElement("span");
    avatar.textContent = result.initial;
    avatar.setAttribute("aria-hidden", "true");
  }
  avatar.className = "avatar avatar-sm flex-shrink-0";
  return avatar;
}

/**
 * Crée un badge Bootstrap indiquant un statut.
 *
 * @param {string} text - Libellé du badge.
 * @param {string} colorClass - Classe CSS Bootstrap définissant la couleur (ex: 'text-bg-success').
 * @returns {HTMLSpanElement} L'élément badge créé.
 */
function buildBadge(text, colorClass) {
  const badge = document.createElement("span");
  badge.className = "badge " + colorClass;
  badge.textContent = text;
  return badge;
}

/**
 * Crée le composant d'action d'un résultat (bouton « Ajouter », lien ou badge de statut).
 *
 * @param {SearchResult} result - Les données du joueur concerné.
 * @returns {HTMLElement} L'élément HTML d'action approprié.
 */
function buildAction(result) {
  if (result.status === "friends") {
    return buildBadge("Déjà amis", "text-bg-success");
  }
  if (result.status === "sent") {
    return buildBadge("Demande envoyée", "text-bg-secondary");
  }
  if (result.status === "received") {
    const link = document.createElement("a");
    link.href = "#friend-requests";
    link.className = "btn btn-outline-primary btn-sm";
    link.textContent = "Voir sa demande";
    return link;
  }

  const button = document.createElement("button");
  button.type = "button";
  button.className = "btn btn-primary btn-sm";
  button.innerHTML = '<i class="bi bi-person-plus me-1"></i>Ajouter';
  button.addEventListener("click", function () {
    sendFriendRequest(result, button);
  });
  return button;
}

/**
 * Crée la ligne représentant un joueur dans la liste de suggestions.
 *
 * @param {SearchResult} result - Le joueur à afficher.
 * @returns {HTMLDivElement} Le conteneur HTML de la ligne.
 */
function buildSuggestion(result) {
  const row = document.createElement("div");
  row.className = "stat-tile d-flex align-items-center gap-3 text-start";

  const link = document.createElement("a");
  link.href = result.profile_url;
  link.className = "fw-semibold text-decoration-none text-body flex-grow-1";
  link.textContent = result.pseudonym;

  const action = document.createElement("div");
  action.appendChild(buildAction(result));

  row.appendChild(buildAvatar(result));
  row.appendChild(link);
  row.appendChild(action);
  return row;
}

/**
 * Affiche la liste des joueurs trouvés dans le conteneur de suggestions.
 *
 * @param {SearchResult[]} results - Tableau des résultats de recherche.
 */
function renderSuggestions(results) {
  suggestionsBox.replaceChildren();
  if (results.length === 0) {
    setStatusMessage("Aucun joueur trouvé.");
  } else {
    setStatusMessage("");
    for (let i = 0; i < results.length; i++) {
      suggestionsBox.appendChild(buildSuggestion(results[i]));
    }
  }
}

/**
 * Interroge le serveur en AJAX pour obtenir et afficher les suggestions selon la saisie utilisateur.
 */
function searchPlayers() {
  const query = searchInput.value.trim();

  if (searchController) {
    searchController.abort();
  }

  if (query === "") {
    suggestionsBox.replaceChildren();
    setStatusMessage("");
  } else {
    searchController = new AbortController();
    const url =
      searchInput.dataset.searchUrl + "?q=" + encodeURIComponent(query);

    fetch(url, {
      signal: searchController.signal,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Réponse réseau invalide");
        }
        return response.json();
      })
      .then(function (data) {
        renderSuggestions(data.results);
      })
      .catch(function (error) {
        if (error.name !== "AbortError") {
          setStatusMessage(
            "Impossible de rechercher les joueurs pour le moment.",
          );
        }
      });
  }
}

/**
 * Envoie une demande d'ami via une requête AJAX POST et met à jour l'affichage de la ligne.
 *
 * @param {SearchResult} result - Les données du joueur à ajouter.
 * @param {HTMLButtonElement} button - Le bouton sur lequel l'utilisateur a cliqué.
 */
function sendFriendRequest(result, button) {
  button.disabled = true;

  fetch(result.add_url, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCsrfToken(),
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      setStatusMessage(data.message);
      if (data.success) {
        result.status = data.status;
        button.parentElement.replaceChildren(buildAction(result));
      } else {
        button.disabled = false;
      }
    })
    .catch(function () {
      setStatusMessage("L'envoi de la demande a échoué. Veuillez réessayer.");
      button.disabled = false;
    });
}

if (searchInput && suggestionsBox && statusBox) {
  searchInput.addEventListener("input", debounce(searchPlayers, SEARCH_DELAY));

  if (addFriendPanel) {
    addFriendPanel.addEventListener("shown.bs.collapse", function () {
      searchInput.focus();
    });
  }
}

/**
 * Fenêtre modale de confirmation pour le retrait d'un ami.
 * @type {HTMLElement|null}
 */
const removeModal = document.getElementById("remove-friend-modal");

if (removeModal) {
  removeModal.addEventListener("show.bs.modal", function (event) {
    const trigger = event.relatedTarget;
    removeModal.querySelector("form").action = trigger.dataset.removeUrl;
    removeModal.querySelector("[name=next]").value = trigger.dataset.next || "";
    document.getElementById("remove-friend-name").textContent =
      trigger.dataset.pseudonym;
  });
}
