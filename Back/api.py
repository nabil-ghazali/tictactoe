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

@app.post("/play")
async def play(request: MoveRequest):
    
    # 1 - Initialisation du client LLM
    llm_client = LLMClient(model_name=request.model_name)
    
    # 2 - Utilisation de la méthode get_llm_move
    
    try:
        coup_joue = await llm_client.get_llm_move(
            grid=request.grid,
            active_player_id=request.active_player_id
        )
        return coup_joue
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erreur interne non gérée: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne lors du traitement du coup: {e}")

