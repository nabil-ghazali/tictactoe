from typing import List, Dict

from fastapi import FastAPI
from pydantic import BaseModel 
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/play")
def play(grid: List[List[str]]):
    # recupere la grille
    print(grid)
    # envoi au LLM
    ## prompt ingeneering
    # recup la reponse du LLM
    ### print de la réponse
    ## parser la reponse ?
    ## Verifier que c'est valide
    ## sinon je redemande au llm
    # return
    return [6, 2]