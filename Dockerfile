# Dockerfile

# --- Étape 1 : L'Image de Base ---
# Utilise une image Python 3.12 officielle et légère (slim)
FROM python:3.12-slim

# Définit le répertoire de travail à l'intérieur du conteneur
WORKDIR /tictactoe

# --- Étape 2 : Installation de Poetry ---
# Installe Poetry (le gestionnaire de dépendances) dans l'image
RUN pip install poetry

# Configure Poetry pour ne pas créer de venv à l'intérieur du conteneur,
# car le conteneur lui-même EST l'environnement isolé.
RUN poetry config virtualenvs.create false

# --- Étape 3 : Installation des Dépendances (Optimisé pour le Cache) ---
# Copie SEULEMENT les fichiers de dépendances en premier.
# Si ces fichiers ne changent pas, Docker réutilisera le cache pour cette étape.
COPY pyproject.toml poetry.lock ./

# Installe les dépendances de production (sans les dépendances de "dev")
RUN poetry install --no-root --only main --no-interaction --no-ansi

# --- Étape 4 : Copie du Code de l'Application ---
# Copie les dossiers contenant votre code Python.
# (On ne copie PAS le Front/, qui sera servi séparément)
COPY Back/ ./Back/
COPY Model/ ./Model/

# --- Étape 5 : Exposition du Port ---
# Indique à Docker que notre application écoute sur le port 8000
EXPOSE 8000

# --- Étape 6 : Commande d'Exécution ---
# La commande pour démarrer le serveur FastAPI en production.
# "--host 0.0.0.0" est OBLIGATOIRE pour que le serveur soit accessible
# depuis l'extérieur du conteneur.
CMD ["poetry", "run", "uvicorn", "Back.api:app", "--host", "0.0.0.0", "--port", "8000"]