
import httpx
import json
from typing import List, Dict
from Back.game_logic import format_grid_for_llm 
from fastapi import HTTPException

ollama_url = "http://localhost:11434"
model_name = "gemma3:1b"


OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

class LLMClient:
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    async def get_llm_move(self, grid: List[List[int]], active_player_id: int, error_history: str="") -> Dict[str, int]:
        # Formatte la grille
        formatted_grid = format_grid_for_llm(grid)
        current_mark = "X" if active_player_id == 1 else "O"
        print(f"Envoi de la requête au joueur {active_player_id}...")
        # Construction du prompt
        prompt = f"""
                You are playing a 10x10 Tic-Tac-Toe game.
                Current game state (' ' means EMPTY cell, 'X' or 'O' means OCCUPIED):
                {formatted_grid}

                It is now Player {active_player_id}'s turn, who plays as '{current_mark}'.
                
                {error_history}

                CRUCIAL: Analyze the board and choose a position (row, col) that is currently **EMPTY (' ')**. 
                DO NOT select an occupied position. An occupied position is a cell with a symbol 'X' (1) or 'O'. 
                The coordinates are 0-based indices from the row and column headers shown in the grid.
        """
                
        json_payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "system": """You are a highly efficient and strict Tic-Tac-Toe AI player on a 10x10 board.
                            Your ONLY goal is to win by aligning exactly 5 marks.

                            STRICT INSTRUCTION: Your move MUST be an empty cell, represented by ' ' (a space) in the current game state. If you select an occupied cell ('X' or 'O'), your move will be rejected. 
                            Respond ONLY with a single JSON object: {"row": R, "col": C}.""",
                "options": {
                "temperature": 0.1
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
                    # Cas où Ollama ne renvoie même pas la clé 'response'
                    raise ValueError("La réponse Ollama est vide ou mal formatée.")
                
                coup_joue = json.loads(json_string)

                # Validation de la réponse JSON du LLM (Row/Col)
                if isinstance(coup_joue, dict) and 'row' in coup_joue and 'col' in coup_joue:
                    # Vérifie si le coup_joue n'est pas sur une case déjà remplie
                    row, col = coup_joue["row"], coup_joue["col"]
                    if grid[row][col] != 0:
                        raise ValueError(f"Case déjà occupée à la position ({row}, {col}).")
                    print(f"Coup joué par le joueur {active_player_id} : {coup_joue} ")
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
        
        except (json.JSONDecodeError) as e:
            # 3. Erreur de parsing ou de validation (le LLM a mal répondu)
            print(f"Erreur LLM/Parsing: {e}. Chaîne reçue: {json_string}")
            raise HTTPException(status_code=500, detail=f"LLM a répondu de manière non-JSON ou invalide : {e}")            

