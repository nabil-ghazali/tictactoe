# tictactoe
Création d'un jeu du morpion IA vs IA

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
        M-->>G: (Python) Renvoie la liste [coup1, coup2, coup3]
        
        G->>G: (Interne) Appelle is_move_valid(grid, coup1)
        
        opt Coup 1 est Valide
            G-->>A: Renvoie le coup1
            break
        end
        
        opt Coup 1 est Invalide
            G->>G: (Interne) Appelle is_move_valid(grid, coup2)
            
            opt Coup 2 est Valide
                G-->>A: Renvoie le coup2
                break
            end
            
            opt Coup 2 est Invalide
                G->>G: (Interne) Appelle is_move_valid(grid, coup3)
                
                opt Coup 3 est Valide
                    G-->>A: Renvoie le coup3
                    break
                end
                
                opt Coup 3 est Invalide
                    G->>G: Prépare error_history
                end
            end
        end
    end
    
    A-->>F: (JSON) Renvoie le coup_valide {"row": X, "col": Y}
    
    F->>F: (JS) Met à jour la variable 'grid'
    F->>U: Appelle viewGrid() pour afficher le coup

```

