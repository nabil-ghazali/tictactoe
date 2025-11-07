from .game_logic import process_llm_turn
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

MAX_RETRIES = 3 # Nombre de tentatives par coup

@app.post("/play")
async def play(request: MoveRequest):

    try:
        coup_joue = await process_llm_turn(
            grid=request.grid,
            active_player_id=request.active_player_id,
            model_name=request.model_name,
            max_retries=MAX_RETRIES
        )
        return coup_joue
    except ValueError as e:
        # Erreur levée par process_llm_turn si les 3 tentatives échouent
        raise HTTPException(status_code=400, detail=f"Echec du LLM : {e}")
    except httpx.ConnectError:
        # Erreur si Ollama n'est pas joignable
        raise HTTPException(status_code=503, detail="Ollama injoignable.")
    except Exception as e:
        # Lève les erreur 500/502 par le LLMCLient
        raise e
    except Exception as e:
        # Lève les erreurs internes de Python
        print(f"Erreur interne non gérée: {type(e).__name__}: {e}")
        raise HTTPException(status_code=50, detail=f"Erreur inattendue : {type(e).__name__}")

