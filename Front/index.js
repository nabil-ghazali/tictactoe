const urlAPI = "http://127.0.0.1:8000/play"

// Variables liés à la grille de jeu
const GRID_SIZE = 10;
const grid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(0));
// Variable lié au joueur
let activePlayerId = 1 // 1 pour 'X'
// Variable de sélection de la balise dans le DOM
const gridHTML = document.querySelector("#grid")
// Variable de sélection du modèle
const llmModelName = "gemma3:1b"

// Fonction d'affichage de la grille dans la page
function viewGrid() {
    gridHTML.innerHTML = ""
    for (let ligne of grid) {
        for (let cell of ligne) {
            const cellHTML = document.createElement("div")
            cellHTML.classList.add("cell")
            cellHTML.textContent = cell
            gridHTML.appendChild(cellHTML)
        }
    }
}

// Interaction bouton Play
document.querySelector("#play").addEventListener(
     "click", e => {
        const requestData = {
            grid: grid,
            active_player_id: activePlayerId,
            model_name: llmModelName
        };
        /// envoyer la grid à l'API
        fetch(urlAPI, {
            method: "POST",
            body: JSON.stringify(requestData),
            headers: {
                "Content-Type": "application/json"
            }
        }) /// recuperer les coordonée du coup joué
        .then(response => response.json())
        .then(data => {
            console.log(data)
            /// mettre à jour la grid
            const coup_ligne = data.row
            const coup_col = data.col
            grid[coup_ligne][coup_col] = activePlayerId
            // afficher la grid
            viewGrid()
            activePlayerId = activePlayerId === 1 ? 2 : 1;
         });
        console.log("salut")
    })


    