const urlAPI = "https://tictactoe-nab-get-hrdwbrckhnguhba3.francecentral-01.azurewebsites.net/play";

// Variables liés à la grille de jeu
const GRID_SIZE = 10;
let grid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(0));

// Variable lié au joueur
let activePlayerId = 1; // 1 pour 'X'

// Variables DOM
const gridHTML = document.querySelector("#grid");
const logHTML = document.querySelector("#log");
const playButton = document.querySelector("#play");
const player1HTML = document.querySelector("#player1");
const player2HTML = document.querySelector("#player2");

// Bouton Reset
const resetButton = document.querySelector("#reset");

// Définition des models joueurs
const modelPlayer1 = "o4-mini";
const modelPlayer2 = "gpt-4o";

// Insérer les noms des models dynamiquement
player1HTML.textContent = ` Joueur 1 : ${modelPlayer1}`;
player2HTML.textContent = ` Joueur 2 : ${modelPlayer2}`;

let gameIsRunning = false;
const DELAY_MS = 500;

let gameLoopTimeout = null;

// Variable pour stocker l'ID du setTimeout

// Fonction d'affichage de la grille
function viewGrid() {
  gridHTML.innerHTML = "";
  for (let ligne of grid) {
    for (let cell of ligne) {
      const cellHTML = document.createElement("div");
      cellHTML.classList.add("cell");

      let displayValue;
      if (cell === 1) displayValue = "X";
      else if (cell === 2) displayValue = "O";
      else displayValue = " ";

      cellHTML.textContent = displayValue;
      gridHTML.appendChild(cellHTML);
    }
  }
}

// Fonction de reset
function resetGame() {
  addLog("Réinitialisation de la partie...");
  // 1 - Arrête toute boucle de jeu en attente
  if (gameLoopTimeout) {
    clearTimeout(gameLoopTimeout);
    gameLoopTimeout = null;
  }
  gameIsRunning = false;

  // 2 - Réinitialisation des données du jeu
  grid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(0));
  activePlayerId = 1;
  // 3 - Réinitialisation de l'interface
  viewGrid();
  playButton.disabled = false
  highlightActivePlayer();
}

// Fonction pour ajouter un log
function addLog(message) {
  const entry = document.createElement("div");
  entry.textContent = message;
  logHTML.appendChild(entry);
  logHTML.scrollTop = logHTML.scrollHeight; // Scroll auto
}

// Fonction pour mettre en surbrillance le joueur actif
function highlightActivePlayer() {
  if (activePlayerId === 1) {
    player1HTML.style.fontWeight = "bold";
    player1HTML.style.color = "white";
    player2HTML.style.fontWeight = "normal";
    player2HTML.style.color = "black";

  } else {
    player1HTML.style.color = "black";
    player2HTML.style.color = "white";
    player1HTML.style.fontWeight = "normal";
    player2HTML.style.fontWeight = "bold";

  }
}

// Fonction pour afficher l’alerte
function showAlert(message, duration = 2000) {
  const alertDiv = document.getElementById("custom-alert");
  const alertText = document.getElementById("alert-text");

  alertText.textContent = message;

  // Afficher avec opacity
  alertDiv.style.opacity = 1;
  alertDiv.style.transform = "translate(-50%, -50%) scale(1.05)";

  // Masquer après duration
  setTimeout(() => {
    alertDiv.style.opacity = 0;
    alertDiv.style.transform = "translate(-50%, -50%) scale(1)";
  }, duration);
}


// --- Boucle de Jeu Asynchrone ---
async function runGameTurn() {

  if (!gameIsRunning) return;
  highlightActivePlayer();
  const modelForThisTurn = activePlayerId === 1 ? modelPlayer1 : modelPlayer2;
  addLog(` * Tour du Joueur ${activePlayerId} (${modelForThisTurn})...`);

  const requestData = {
    grid: grid,
    active_player_id: activePlayerId,
    model_name: modelForThisTurn,
  };

  try {
    const response = await fetch(urlAPI, {
      method: "POST",
      body: JSON.stringify(requestData),
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Erreur API (${response.status}): ${errorData.detail}`);
    }

    const data = await response.json(); // {row, col, player_id, is_winner, is_draw}

    // Mise à jour de la grille
    grid[data.row][data.col] = data.player_id;

    // Affichage visuel
    viewGrid();

    addLog(` - Coup joué → Joueur ${data.player_id} : ligne ${data.row + 1}, colonne ${data.col + 1}`);

    // Vérification de fin de partie
    if (data.is_winner) {
      addLog(`🏆 Victoire du Joueur ${data.player_id} !`);
      showAlert(` 🏆 Victoire du Joueur ${data.player_id} !`);
      gameIsRunning = false;
      playButton.disabled = false;
      return;
    }

    if (data.is_draw) {
      addLog("🤝 Match nul !");
      showAlert(" 🤝 Match nul !");
      gameIsRunning = false;
      playButton.disabled = false;
      return;
    }

    // Tour suivant
    activePlayerId = 3 - activePlayerId;
    gameLoopTimeout = setTimeout(runGameTurn, DELAY_MS);
  } catch (error) {
    console.error("Erreur pendant le tour:", error);
    addLog("❌ Erreur: " + error.message);
    gameIsRunning = false;
    playButton.disabled = false;
  }
}

// --- Démarrage du jeu ---
playButton.addEventListener("click", () => {
  if (gameIsRunning) return;
  // Réinitialisation d'une partie
  resetGame();
  // Nettoyage des logs
  logHTML.innerHTML = "";
  addLog("Nouveau match lancé ! ")
  // Lancement d'une partie
  gameIsRunning = true;
  playButton.disabled = true;
  logHTML.innerHTML = "";
  addLog("🎬 Nouveau match lancé !");
  runGameTurn();
});

if (resetButton) {
  resetButton.addEventListener("click", () => {
    addLog("Partie arrêtée par l'utilisateur.");
    resetGame();

  })
}

// Grille initiale
viewGrid();