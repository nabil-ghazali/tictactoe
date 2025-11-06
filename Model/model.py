


r = requests.post(f"{ollama_url}/api/generate", json={
        "model": mon_model,
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
        "format": {
            "type": "array",
            "items": {"type": "number"},
            "minContains": 2,
            "maxContains": 2
        }
    })