from typing import List, Dict
<<<<<<< HEAD
import json
from game_logic import format_grid_for_llm
=======
from .game_logic import format_grid_for_llm
from Model.model import LLMClient
from .move_request import MoveRequest
>>>>>>> bd2f999f8ee49526219291477a81faf3e5cf2414
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
import httpx
<<<<<<< HEAD
from move_request import MoveRequest
=======


>>>>>>> bd2f999f8ee49526219291477a81faf3e5cf2414

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class LLMClient:
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    async def get_llm_move(self, grid: List[List[str]], last_player_id: int, active_player_id: int) -> Dict[str, int]:
        # Formatte la grille
        formatted_grid = format_grid_for_llm(grid)
        current_mark = "X" if active_player_id == 1 else "O"
        
        # Construction du prompt
        prompt = f"""
        You are playing a Tic-Tac-Toe game on a 10x10 board. Two players alternate placing their marks: Player 1 uses 'x' and Player 2 uses 'o'. The goal is to align exactly 5 marks consecutively horizontally, vertically, or diagonally.

        Current game state (' ' for empty cells):
        {formatted_grid}

        Players alternate turns to avoid filling entire rows, columns, or diagonals completely.
        The last move was played by Player {last_player_id}, but you should focus on the entire board state.
        It is now Player {active_player_id}'s turn, who plays as '{current_mark}'. Your model's name is '{self.model_name}'.
        Given this board state and rules, select the best move for Player {active_player_id} and respond ONLY with a JSON object containing the keys 'row' and 'col' for your chosen move (1-based indices).

        If no valid moves remain, respond with 'pass'.
        """
                
        json_payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "system": """You are a Tic-Tac-Toe player. In Tic-Tac-Toe,
            two players take turns placing their marks (an 'x' for player 'x' and an 'o' for player 'o')
            on a 10x10 grid. The goal is to get 5 of your marks in a row, either horizontally, vertically,
            or diagonally. If all spaces on the grid are filled and neither player has achieved five in a row,
            the game ends in a draw.""",
                "options": {
                "temperature": 1
                },
            "format": "json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OLLAMA_API_URL, json=json_payload)
            response.raise_for_status()
            
            ollama_response = response.json()
            json_string = ollama_response.get("response", None)
            
            try:
                coup_joue = json.loads(json_string)
                # Vérifie que la réponse contient bien la position de la case jouée
                if isinstance(coup_joue, dict) and 'row' in coup_joue and 'col' in coup_joue:
                    return coup_joue
                elif coup_joue == "pass":
                    return {"pass": True}
                else:
                    raise ValueError("Réponse JSON du LLM incomplète ou invalide.")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Erreur LLM/Parsing: {e}")
                raise RuntimeError("LLM a répondu de manière non conforme ou incomplète.")
            



@app.post("/play")
async def play(request: MoveRequest):
    OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
    # 1 - Initialisation du client LLM
    llm_client = LLMClient(OLLAMA_API_URL=request.model_name)
    
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

