# test_ollama.py

import httpx
import asyncio
import json

# REMARQUE IMPORTANTE : Vérifiez ce port (11434 ou 11435)
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate" 
MODEL_NAME = "gemma3:1b" # Doit correspondre au modèle chargé dans Ollama

async def test_ollama_connection():
    """
    Tente de se connecter à Ollama et d'obtenir une réponse structurée en JSON.
    """
    print(f"Tentative de connexion à Ollama ({OLLAMA_API_URL}) avec le modèle {MODEL_NAME}...")
    
    # Un prompt minimal pour tester la capacité à répondre en JSON
    test_prompt = "Réponds UNIQUEMENT avec un objet JSON qui contient la clé 'status' et la valeur 'OK'."
    
    json_payload = {
        "model": MODEL_NAME,
        "prompt": test_prompt,
        "format": "json",
        "stream": False 
    }

    try:
        # Utilisation du client asynchrone httpx (nécessite le mot-clé 'async')
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(OLLAMA_API_URL, json=json_payload)
            
            # Lève une erreur si le statut est 4xx ou 5xx (le serveur Ollama a répondu, mais il y a une erreur)
            response.raise_for_status() 
            
            # Extraction et affichage de la réponse brute d'Ollama
            ollama_response = response.json()
            
            # Le texte généré par le LLM se trouve dans la clé 'response'
            json_string = ollama_response.get("response", "Erreur : Clé 'response' manquante.")
            
            # Tentative de parsing
            parsed_json = json.loads(json_string)
            
            print("\n✅ TEST RÉUSSI !")
            print(f"Statut HTTP : {response.status_code}")
            print(f"Réponse JSON parsée : {parsed_json}")
            
    except httpx.ConnectError as e:
        print("\n❌ ERREUR DE CONNEXION")
        print(f"Vérifiez que Ollama est démarré et écoute bien sur le port {OLLAMA_API_URL.split(':')[-1].split('/')[0]}.")
        print(f"Détails : {e}")
        
    except httpx.HTTPStatusError as e:
        print("\n❌ ERREUR DU SERVEUR OLLAMA")
        print(f"Statut : {e.response.status_code}. Le modèle '{MODEL_NAME}' est-il bien chargé ?")
        print(f"Réponse du serveur : {e.response.text}")
        
    except json.JSONDecodeError:
        print("\n❌ ERREUR DE PARSING JSON")
        print("Le modèle a renvoyé un format qui n'est pas du JSON valide.")
        print(f"Réponse brute du LLM : {json_string}")
        
    except Exception as e:
        print(f"\n❌ ERREUR INCONNUE : {e}")


if __name__ == "__main__":
    # Exécuter la fonction asynchrone
    asyncio.run(test_ollama_connection())