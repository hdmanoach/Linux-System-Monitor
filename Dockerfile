# Étape 1: Utiliser une image Python officielle et légère comme base
FROM python:3.9-slim

# Étape 2: Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3: Copier le fichier des dépendances et les installer
# On copie ce fichier en premier pour profiter de la mise en cache de Docker.
# Si requirements.txt ne change pas, Docker n'aura pas à réinstaller les dépendances.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer Gunicorn, un serveur WSGI de production plus robuste que le serveur de dev de Flask
RUN pip install gunicorn

# Étape 4: Copier le reste du code de l'application dans le conteneur
COPY . .

# Étape 5: Exposer le port sur lequel l'application va tourner
# Gunicorn utilisera par défaut le port 8000
EXPOSE 8000

# Étape 6: Définir la variable d'environnement pour la clé API Gemini
# IMPORTANT: La clé API sera passée lors de la création du conteneur, pas stockée ici.
# Cette ligne indique simplement que la variable d'environnement GEMINI_API_KEY est attendue.
ENV GEMINI_API_KEY=""

# Étape 7: Commande pour lancer l'application avec Gunicorn
# --workers 3 : Nombre de processus pour gérer les requêtes (ajuster si besoin)
# --bind 0.0.0.0:8000 : Écoute sur toutes les interfaces réseau sur le port 8000
# app:app : Indique à Gunicorn de chercher l'objet 'app' dans le fichier 'app.py'
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "app:app"]