# Étape 1: Utiliser une image Python officielle comme image de base
FROM python:3.9-slim

# Étape 2: Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3: Copier le fichier des dépendances et les installer
# Copier d'abord ce fichier permet de profiter du cache de Docker si les dépendances ne changent pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 4: Copier le reste des fichiers de l'application
COPY . .

# Étape 5: Exposer le port sur lequel l'application s'exécutera
# Gunicorn par défaut écoute sur le port 8000
EXPOSE 8000

# Étape 6: Définir la commande pour lancer l'application avec Gunicorn
# --bind 0.0.0.0:8000 : Écoute sur toutes les interfaces réseau sur le port 8000
# --workers 3 : Nombre de processus Gunicorn à lancer
# app:app : Indique à Gunicorn de chercher l'objet 'app' dans le fichier 'app.py'
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "app:app"]
