import httpx
import os
import json
from typing import List, Dict
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

# OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
AZURE_API_ENDPOINT = os.getenv("URL_O4MINI")
AZURE_API_KEY = os.getenv("KEY_O4MINI")

if not AZURE_API_ENDPOINT or not AZURE_API_KEY:
    raise EnvironmentError("AZURE_API_ENDPOINT ou AZURE_API_KEY non trouvé.")

def format_grid_for_llm(grid: List[List[int]]) -> str:
    """
    Convertit la grille numérique (0, 1, 2) en un format texte
    lisible par le LLM (avec indices de lignes/colonnes).
    """
    SYMBOL_MAP = {0: " ", 1: "X", 2: "O"} # Utilise " " pour vide
    header = "   | " + " | ".join(str(i) for i in range(10)) + " |"
    output = header + "\n" + "-" * len(header) + "\n"
    
    for i, row in enumerate(grid):
        # Conversion de chaque entier de 'row' en son symbole
        symbols = [SYMBOL_MAP[cell] for cell in row]
        # Jointure des symboles
        line_content = " | ".join(symbols)
        # Ajout de l'indice de ligne formaté
        output += f"{i:2} | {line_content} |\n"
        
    return output

class LLMClient:
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.temperature = 1
        self.api_endpoint = AZURE_API_ENDPOINT
        self.api_key = AZURE_API_KEY
    
    # --- 1. Méthode Publique  ---
    
    async def get_llm_move_suggestions(self, grid: List[List[int]], active_player_id: int, error_history: str="") -> List[Dict[str, int]]:
        """
        Orchestre le processus complet pour obtenir les suggestions de coups.
        """
        
        # Étape 1 : Construire les prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(grid, active_player_id, error_history)
        
        # Étape 2 : Construire le payload
        json_payload = self._build_payload(user_prompt, system_prompt)
        
        # Étape 3 : Appeler l'API (gère les erreurs réseau)
        model_response = await self._make_api_call(json_payload)
        
        # Étape 4 : Parser la réponse (gère les erreurs de format)
        suggestions = self._parse_llm_response(model_response)
        
        return suggestions

    # --- 2. Méthodes Privées ---
    def _build_headers(self) -> Dict:
        """
        Construit les en-têtes d'authentification pour Azure
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _build_system_prompt(self) -> str:
        """Génère le prompt système statique."""
        return """
        You are a highly efficient and strict Tic-Tac-Toe AI player on a 10x10 board.
        Your ONLY goal is to win by aligning exactly 5 marks.
        
        STRICT INSTRUCTION: Your move MUST be an empty cell, represented by ' ' (a space).
        You MUST respond ONLY with a JSON object containing a "moves" key, which holds a list of your top 3 preferred moves.
        Example: {"moves": [{"row": 5, "col": 5}, {"row": 4, "col": 5}, {"row": 6, "col": 6}]}
        """

    def _build_user_prompt(self, grid: List[List[int]], active_player_id: int, error_history: str) -> str:
        """Génère le prompt utilisateur dynamique avec l'état du jeu."""
        formatted_grid = format_grid_for_llm(grid)
        current_mark = "X" if active_player_id == 1 else "O"
        
        return f"""
        You are playing a 10x10 Tic-Tac-Toe game.
        Current game state (' ' means EMPTY cell):
        {formatted_grid}

        It is now Player {active_player_id}'s turn ({current_mark}).
        {error_history}

        CRUCIAL: Analyze the board and find the **Top 3 BEST moves** that are currently **EMPTY (' ')**.
        Respond ONLY with the JSON format requested in the system prompt.
        """
    
    def _build_payload(self, user_prompt: str, system_prompt: str) -> Dict:
        """Construit le dictionnaire JSON final pour l'API Ollama."""
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "response_format": {"type": "json_object"}
            
        }

    async def _make_api_call(self, json_payload: Dict) -> Dict:
        """Exécute l'appel HTTP asynchrone et gère les erreurs réseau."""
        headers = self._build_headers()
        async with httpx.AsyncClient(timeout=None) as client:
                    response = await client.post(
                        self.api_endpoint,
                        json=json_payload,
                        headers=headers)
                    
                    try:
                        response.raise_for_status() 
                    except httpx.HTTPStatusError as e:
                        # --- AJOUT TEMPORAIRE POUR DÉBOGAGE ---
                        print("\n--- ERREUR AZURE REÇUE ---")
                        print(f"Statut Reçu: {e.response.status_code}")
                        # Affiche le corps de la réponse d'erreur, qui contient le message d'Azure
                        print(f"Corps de l'Erreur: {e.response.text}") 
                        print("-----------------------------\n")
                        # --- FIN DE L'AJOUT TEMPORAIRE ---
                        if e.response.status_code == 401:
                            raise HTTPException(status_code=401, detail="Clé API Azure invalide ou expirée.")
                        raise HTTPException(status_code=502, detail=f"Erreur du serveur Azure: {e.response.text}")
                    
                    return response.json()

    def _parse_llm_response(self, api_response: Dict) -> List[Dict[str, int]]:
        """Parse la réponse JSON du modèle et valide la structure attendue."""
        json_string = None # Initialisé pour le bloc except
        try:
            json_string = api_response["choices"][0]["message"]["content"]
            if json_string is None:
                raise ValueError("La réponse du modèle est vide (clé 'response' manquante).")
            
            parsed_data = json.loads(json_string)

            # Valide la structure {"moves": [...]}
            if isinstance(parsed_data, dict) and "moves" in parsed_data and isinstance(parsed_data["moves"], list):
                return parsed_data["moves"]
            else:
                raise ValueError("Réponse JSON du LLM incomplète (clé 'moves' manquante ou n'est pas une liste).")
        
        except (json.JSONDecodeError, ValueError) as e:
            # Gère les erreurs de parsing ou de structure
            print(f"Erreur LLM/Parsing: {e}. Chaîne reçue: {json_string}")
            raise HTTPException(status_code=500, detail=f"LLM a répondu de manière non-JSON ou invalide : {e}")