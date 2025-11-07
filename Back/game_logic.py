from typing import List

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

def check_win():
    pass
