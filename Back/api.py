from .game_logic import process_llm_turn, check_win, is_grid_full
from .move_request import MoveRequest
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
import httpx

app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_RETRIES = 3 

@app.post("/play")
async def play(request: MoveRequest):
    """
    Déclenche le jeu automatique. La boucle s'arrête si :
    1. Victoire détectée.
    2. Grille complète (Match Nul).
    3. Erreur irrécupérable du LLM.
    """
        
    try:
        # 1. Obtenir le coup valide
        coup_joue = await process_llm_turn(
            grid=request.grid,
            active_player_id=request.active_player_id,
            model_name=request.model_name,
            max_retries=MAX_RETRIES
        )
        
        row = coup_joue["row"]
        col = coup_joue["col"]

        # 2. Appliquer le coup à une grille temporaire pour la vérification
        temp_grid = [r[:] for r in request.grid]
        temp_grid[row][col] = request.active_player_id
        
        # 3. Vérifier les conditions de fin de jeu
        is_winner = check_win(temp_grid, request.active_player_id, row, col)
        is_draw = False
        if not is_winner:
            is_draw = is_grid_full(temp_grid)
        
        # 4. Retourner le coup et le statut du jeu
        return {
            "row": row,
            "col": col,
            "player_id": request.active_player_id,
            "is_winner": is_winner,
            "is_draw": is_draw
        }

        # --- Gestion des erreurs (inchangée) ---
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Échec du LLM : {e}")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Serveur LLM (Azure) injoignable.")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erreur interne non gérée: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne inattendue : {type(e).__name__}")
    
