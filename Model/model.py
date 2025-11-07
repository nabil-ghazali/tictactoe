
# from dotenv import load_dotenv # Récuperer variables d'environnement
import os
import requests
import httpx
import json
from typing import List, Dict
from Back.game_logic import format_grid_for_llm  # Ta fonction pour formater la grille

# Charger les variables du fichier .env
# load_dotenv()

# Accéder aux variables
api_key = os.getenv("API_KEY") # récupérer la clé APi à partir d'Azure foundry
debug = os.getenv("DEBUG") == "True" # os.getenv("DEBUG") lit la variable d’environnement DEBUG (ex. "True").Elle compare le résultat à la chaîne "True".Si c'est égal, la variable debug devient le booléen True.

import requests

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
            

