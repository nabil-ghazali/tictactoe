
const urlAPI = "http://127.0.0.1:8000/play"

// Variables liées à la grille de jeu
const GRID_SIZE = 10;
const grid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(0));
// Variable liée au joueur
let activePlayerId = 1; // 1 pour 'X'
// Sélection du conteneur DOM
const gridHTML = document.querySelector("#grid")
// Variable de sélection du modèle
const modelPlayer1 = "o4-mini"
const modelPlayer2 = "gpt-4o"

let gameIsRunning = false;
const playButton = document.querySelector("#play");
const DELAY_MS = 500;
// Fonction d'affichage de la grille dans la page
function viewGrid() {
    gridHTML.innerHTML = ""
    for (let row of grid) {
        for (let cell of row) {
            const cellHTML = document.createElement("div")
            cellHTML.classList.add("cell")
            cellHTML.textContent = cell === 1 ? "X" : cell === 2 ? "O" : ""
            gridHTML.appendChild(cellHTML)
        }
    }
}

// --- La Boucle de Jeu Asynchrone ---
async function runGameTurn() {
    
    if (!gameIsRunning) return; // Sécurité si le jeu a été arrêté

    const modelForThisTurn = (activePlayerId === 1) ? modelPlayer1 : modelPlayer2;

    console.log(`Tour du Joueur ${activePlayerId}, Modèle: ${modelForThisTurn}`);

    const requestData = {
        grid: grid,
        active_player_id: activePlayerId,
        model_name:modelForThisTurn
    };

    try {
        const response = await fetch(urlAPI, {
            method: "POST",
            body: JSON.stringify(requestData),
            headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Erreur API (${response.status}): ${errorData.detail}`);
        }

        const data = await response.json(); // Reçoit {row, col, player_id, is_winner, is_draw}

        // 1. Mettre à jour la grille locale
        grid[data.row][data.col] = data.player_id;
        
        // 2. Afficher la grille (Mise à jour visuelle)
        viewGrid();

        // 3. Vérifier les conditions de fin
        if (data.is_winner) {
            setTimeout(() => alert(`Victoire du Joueur ${data.player_id}!`), 100); // Léger délai pour l'alerte
            gameIsRunning = false;
            playButton.disabled = false;
            return; // Arrête la boucle
        }

        if (data.is_draw) {
            setTimeout(() => alert("Match Nul !"), 100);
            gameIsRunning = false;
            playButton.disabled = false;
            return; // Arrête la boucle
        }

        // 4. Passer au joueur suivant
        activePlayerId = 3 - activePlayerId; 

        // 5. Rappeler cette fonction après un délai (Récursion)
        setTimeout(runGameTurn, DELAY_MS);

    } catch (error) {
        console.error("Erreur critique pendant le tour:", error);
        alert(error.message);
        gameIsRunning = false;
        playButton.disabled = false;
    }
}

// --- Le Déclencheur ---
playButton.addEventListener("click", e => {
    if (gameIsRunning) return; // Ne pas démarrer si déjà en cours

    // (Optionnel) Réinitialiser la grille si le jeu est relancé
    // grid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(0));
    // activePlayerId = 1;
    // viewGrid();
    
    gameIsRunning = true;
    playButton.disabled = true;
    
    // Lance le premier tour
    runGameTurn(); 
});

// Affiche la grille vide au chargement initial
viewGrid();

        // Si LLM passe le tour
        if (data.pass) {
            console.log("Aucun coup possible, tour passé")
            activePlayerId = activePlayerId === 1 ? 2 : 1
            return
        }

        // Vérifier que les coordonnées existent et la case est vide
        if (typeof data.row === "number" && typeof data.col === "number") {
            if (grid[data.row][data.col] === 0) {
                grid[data.row][data.col] = activePlayerId
                viewGrid()
                activePlayerId = activePlayerId === 1 ? 2 : 1
            } else {
                console.error("Le LLM a proposé une case déjà occupée", data)
            }
        } else {
            console.error("Réponse LLM invalide", data)
        }
    })
    .catch(err => console.error("Erreur API:", err))
})
