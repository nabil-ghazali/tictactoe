from typing import List, Dict
from Model.model import LLMClient


# Fonction de vérification de la validité des coups
def is_move_valid(grid: List[List[int]], row: int, col: int) -> bool:
    """
    Vérifie la validité d'un coup joué par le modèle 
    """
    GRID_SIZE = 10
    
    # 1 - Vérification des types
    if not isinstance(row, int) or not isinstance(col, int):
        return False
    # 2 - Vérification des limites (si ça joue dans les limites de la grille)
    if not (0 <= row < GRID_SIZE and  0 <= col < GRID_SIZE):
        return False
    # 3 - Vérification de la case vide
    if grid[row][col] != 0:
        return False
    return True

# Fonction de gestion des tours du LLM
async def process_llm_turn(
    grid: List[List[int]],
    active_player_id: int,
    model_name: str,
    max_retries: int
) -> Dict[str, int]:
    """
    Gère l'intégralité d'un tour de LLM, y compris les tentatives. 
    """
    llm_client = LLMClient(model_name=model_name)
    error_message_for_llm = ""
    for attempt in range(max_retries):
        try:
            # 1. Obtenir la liste des suggestions
            suggested_moves = await llm_client.get_llm_move_suggestions(
                grid=grid,
                active_player_id=active_player_id,
                error_history=error_message_for_llm
            )
            
            # 2. Itérer sur les suggestions et trouver la première valide
            for move in suggested_moves:
                row = move.get("row")
                col = move.get("col")
                
                # Vérification par l'arbitre (notre code Python)
                if is_move_valid(grid, row, col):
                    print(f"Tentative {attempt + 1}: Coup valide trouvé {move}")
                    return move # On a trouvé un coup valide
            
            # 3. Si aucun coup valide n'est trouvé dans les suggestions
            raise ValueError("Toutes les suggestions du LLM étaient des coups invalides (occupés ou hors grille).")

        except ValueError as e:
            # Cas : Le LLM a donné 3 coups invalides
            print(f"Tentative {attempt + 1}/{max_retries} échouée : {e}.")
            error_message_for_llm = f"""
            WARNING: All of your previous move suggestions were REJECTED because they were invalid.
            Reason: {e}
            You MUST choose different cells which are empty for this attempt.
            """
            # On continue la boucle 'for attempt' pour réessayer
            continue
    
    # Si la boucle se termine sans succès
    raise ValueError("Le LLM a donné trop de coups invalides consécutifs.")