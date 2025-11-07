from typing import List, Dict
from .game_logic import format_grid_for_llm
from Model.model import LLMClient
from .move_request import MoveRequest
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
import httpx



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_RETRIES = 3 # Nombre de tentatives par coup

@app.post("/play")
async def play(request: MoveRequest):
    
    # 1 - Initialisation du client LLM
    llm_client = LLMClient(model_name=request.model_name)
    error_message_for_llm = ""
    
    # 2 - Utilisation de la méthode get_llm_move
    for attempt in range(MAX_RETRIES):
        try:
            coup_joue = await llm_client.get_llm_move(
                grid=request.grid,
                active_player_id=request.active_player_id,
                error_history=error_message_for_llm
            )
            return coup_joue
        # Cas 1 - Le LLM a joué un coup invalide: La boucle continue jusqu'à arriver au nombre de tentative max.
        except ValueError as e:
            print(f"Tentative {attempt + 1}/{MAX_RETRIES} échouée (Coup invalide) : {e}.")
            error_message_for_llm = f"""
            WARNING: Your previous move has been REJECTED because it was invalid.
            Reason: {e}
            You MUST choose a different cell which is empty for this attempt.
            """
            continue
        # Cas 2 - Erreur critique (Connexion au LLM, parsing JSON)
        except HTTPException as e:
            raise e
        # Cas 3 - Erreur Python interne inattendue
        except Exception as e:
            print(f"Erreur interne non gérée: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur interne lors du traitement du coup: {e}")
    # Si la boucle se termine sans succès, après toutes les tentatives
    raise HTTPException(status_code=400, detail="Le LLM a donné trop de coups invalides consécutifs.")

