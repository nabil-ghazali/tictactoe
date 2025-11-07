
# from dotenv import load_dotenv # Récuperer variables d'environnement
import os
import requests
import httpx
import json
from typing import List, Dict
from Back.game_logic import format_grid_for_llm 
import requests
from fastapi import HTTPException

ollama_url = "http://localhost:11434"
model_name = "gemma3:1b"

# Variables dynamiques de test — à remplacer en fonction de ta logique métier
last_player_id = 1
active_player_id = 2
current_mark = "o"


OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

class LLMClient:
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    async def get_llm_move(self, grid: List[List[int]], active_player_id: int) -> Dict[str, int]:
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

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(OLLAMA_API_URL, json=json_payload)
                
                # Attrape les erreurs 4xx/5xx du serveur Ollama
                response.raise_for_status() 
                
                ollama_response = response.json()
                json_string = ollama_response.get("response", None)
                
                if json_string is None:
                    # Cas où Ollama ne renvoie même pas la clé 'response' (très rare)
                    raise ValueError("La réponse Ollama est vide ou mal formatée.")
                
                coup_joue = json.loads(json_string)

                # Validation de la réponse JSON du LLM (Row/Col)
                if isinstance(coup_joue, dict) and 'row' in coup_joue and 'col' in coup_joue:
                    return coup_joue
                # Gestion du cas "pass" (si le LLM le renvoie correctement)
                elif coup_joue == "pass":
                    return {"pass": True}
                else:
                    raise ValueError("Réponse JSON du LLM incomplète ou invalide (clés manquantes).")
        
        except httpx.ConnectError:
            # 1. Erreur de connexion (même si le test marche, une interruption est possible)
            raise HTTPException(status_code=503, detail="Ollama n'est pas joignable ou le port est incorrect.")
        
        except httpx.HTTPStatusError as e:
            # 2. Erreur HTTP du serveur Ollama (ex: 404, 500)
            raise HTTPException(status_code=502, detail=f"Erreur du serveur Ollama: {e.response.text}")
        
        except (json.JSONDecodeError, ValueError) as e:
            # 3. Erreur de parsing ou de validation (le LLM a mal répondu)
            print(f"Erreur LLM/Parsing: {e}. Chaîne reçue: {json_string}")
            raise HTTPException(status_code=500, detail=f"LLM a répondu de manière non-JSON ou invalide : {e}")            

