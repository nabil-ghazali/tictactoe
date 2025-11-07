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

    U->>F: 1. Clic sur "Play"
    
    F->>A: 2. fetch("/play", JSON_Grid)
    
    A->>G: 3. Appelle process_llm_turn(grid, ...)
    
    loop Tentatives (MAX_RETRIES)
        G->>M: 4. Appelle get_llm_move_suggestions(...)
        
        M->>M: 5. (Interne) Appelle format_grid_for_llm(grid)
        M->>O: 6. (httpx) Envoie Prompt (avec "Top 3 moves")
        O-->>M: 7. (JSON) Réponse {"moves": [...]}
        M-->>G: 8. (Python) Renvoie la liste [coup1, coup2, coup3]
        
        G->>G: 9. (Interne) Appelle is_move_valid(grid, coup1)
        
        alt Coup 1 est Valide
            G-->>A: 10. Renvoie le coup1
            break
        
        else Coup 1 Invalide
            G->>G: 11. (Interne) Appelle is_move_valid(grid, coup2)
            
            alt Coup 2 est Valide
                G-->>A: 12. Renvoie le coup2
                break
            
            else Coup 2 Invalide
                G->>G: 13. (Interne) Appelle is_move_valid(grid, coup3)
                
                alt Coup 3 est Valide
                    G-->>A: 14. Renvoie le coup3
                    break
                
                else Tous les coups Invalides
                    G->>G: 15. Prépare error_history
                end
            end
        end
    end
    
    A-->>F: 16. (JSON) Renvoie le coup_valide {"row": X, "col": Y}
    
    F->>F: 17. (JS) Met à jour la variable 'grid'
    F->>U: 18. Appelle viewGrid() pour afficher le coup

```

