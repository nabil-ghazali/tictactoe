const urlAPI = "http://127.0.0.1:8000/play"

const grid = [
    ["","",""],
    ["","",""],
    ["","",""],
]

const gridHTML = document.querySelector("#grid")


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

let joueur = "X"

document.querySelector("#play").addEventListener(
     "click", e => {
        /// envoyer la grid à l'API
        fetch(urlAPI, {
            method: "POST",
            body: JSON.stringify(grid),
            headers: {
                "Content-Type": "application/json"
            }
        }) /// recuperer les coordonée du coup joué
        .then(response => response.json())
        .then(data => {
            console.log(data)
            /// mettre à jour la grid
            grid[data[1]][data[0]] = joueur
            // afficher la grid
            viewGrid()
            if(joueur === "X") {
                joueur = "O"
            }else{ joueur = "X"}
        })
        console.log("salut")
    })