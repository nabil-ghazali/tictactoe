# tictactoe
Création d'un jeu du morpion IA vs IA

# Objectif du projet

Faire affronter des LLM dans un jeu du morpion dans une grille 10x10. Le système gère l'alternance des tours, la validité des coups des LLM et l'affichage dynamique de la partie.

## Schématisation des responsabilités

### Front/index.js

- Affiche la grille ```viewGrid```
- Envoie la requête HTTP ```fetch``` quand on clique

### Back/api.py

- Gère le HTTP
- Reçoit la requête JSON, la valide grâce ```MoveRequest``` et délègue immédiatement le travail
- Il gère les erreurs finales (HTTP 500, 400...)

### Back/game_logic.py

- Contient la boucle de tentative ```process_llm_turn```
- Contient la logique de vérification des coups```is_move_valid```
- Prochainement implémentation de la condition de victoire

### Model/model.py

- Construit les prompts (utilisation de ```format_grid_for_llm```)
- Appelle le modèle (pour l'instant de Ollama, httpx pour les requêtes)
- Parse la réponse JSON du LLM

## Schéma - Diagramme de séquence
```mermaid
sequenceDiagram
    participant U as Utilisateur (Navigateur)
    participant F as Front/index.js
    participant A as Back/api.py (Contrôleur)
    participant G as Back/game_logic.py (Cerveau)
    participant M as Model/model.py (Client LLM)
    participant O as Ollama (Serveur IA)

    U->>F: Clic sur "Play"
    F->>A: fetch("/play", JSON_Grid)
    A->>G: Appelle process_llm_turn(grid, ...)

    loop Tentatives (MAX_RETRIES)
        G->>M: Appelle get_llm_move_suggestions(...)
        M-->>G: (Python) Renvoie [coup1, coup2, coup3]
        
        G->>G: Vérifie is_move_valid(coup1)
        alt Coup 1 valide
            G-->>A: Renvoie coup1
        else Coup 1 invalide
            G->>G: Vérifie is_move_valid(coup2)
            alt Coup 2 valide
                G-->>A: Renvoie coup2
            else Coup 2 invalide
                G->>G: Vérifie is_move_valid(coup3)
                alt Coup 3 valide
                    G-->>A: Renvoie coup3
                else Coup 3 invalide
                    G->>G: Prépare error_history
                end
            end
        end
    end
    
    A-->>F: Renvoie {"row": X, "col": Y}
    
    F->>F: Met à jour la variable grid
    F->>U: Affiche le coup via viewGrid()

```

