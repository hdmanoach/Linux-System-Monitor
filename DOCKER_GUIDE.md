# Guide d'Utilisation de Docker pour le Moniteur Système

Ce guide explique comment construire et exécuter l'application Moniteur Système en utilisant Docker.

---

## 1. Fichiers de Configuration Docker

Le projet contient deux fichiers essentiels pour Docker :

### a. `Dockerfile`

Ce fichier est la "recette" pour construire notre image Docker. Voici ce que chaque ligne signifie :

```dockerfile
# Utilise une image Python officielle, légère et optimisée.
FROM python:3.9-slim

# Crée et définit le répertoire de travail à l'intérieur du conteneur.
WORKDIR /app

# Copie d'abord le fichier des dépendances. Docker met en cache cette étape.
# Si le fichier ne change pas, Docker réutilisera le cache, accélérant la construction.
COPY requirements.txt .

# Installe les dépendances Python listées dans requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Copie tous les autres fichiers du projet (app.py, disk_utils.py, templates/, etc.)
COPY . .

# Informe Docker que le conteneur écoutera sur le port 8000.
EXPOSE 8000

# La commande qui sera exécutée au démarrage du conteneur.
# On utilise Gunicorn, un serveur de production WSGI, plus robuste que le serveur de test de Flask.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "app:app"]
```

### b. `.dockerignore`

Ce fichier fonctionne comme un `.gitignore`. Il liste tous les fichiers et dossiers que Docker doit ignorer lors de la construction de l'image. C'est utile pour :
- **Réduire la taille de l'image :** En excluant des dossiers lourds comme `venv/`.
- **Accélérer la construction :** En évitant de copier des fichiers inutiles.
- **Sécurité :** En s'assurant que des fichiers sensibles (comme `.git` ou des fichiers de configuration locaux) ne se retrouvent pas dans l'image.

---

## 2. Construire l'Image Docker

Pour construire l'image, ouvrez un terminal à la racine du projet et exécutez la commande suivante :

```bash
docker build -t moniteur-systeme .
```

- `docker build` : La commande pour construire une image.
- `-t moniteur-systeme` : Donne un "tag" (un nom) à notre image. Ici, nous l'appelons `moniteur-systeme`.
- `.` : Indique à Docker d'utiliser le `Dockerfile` présent dans le répertoire actuel.

---

## 3. Exécuter le Conteneur

Une fois l'image construite, vous pouvez démarrer un conteneur avec cette commande :

```bash
docker run -d -p 5000:8000 --name moniteur-app moniteur-systeme
```

- `docker run` : La commande pour démarrer un nouveau conteneur.
- `-d` : **Mode détaché**. Le conteneur s'exécute en arrière-plan et ne bloque pas votre terminal.
- `-p 5000:8000` : **Mappe les ports**. Cela redirige le port `5000` de votre machine hôte vers le port `8000` du conteneur (où Gunicorn écoute). Vous pourrez donc accéder à l'application via `http://localhost:5000`.
- `--name moniteur-app` : Donne un nom facile à retenir à votre conteneur en cours d'exécution.
- `moniteur-systeme` : Le nom de l'image que nous voulons utiliser.

### Gérer le Conteneur

- Pour voir les logs de l'application : `docker logs moniteur-app`
- Pour arrêter le conteneur : `docker stop moniteur-app`
- Pour le redémarrer : `docker start moniteur-app`
- Pour le supprimer : `docker rm moniteur-app`

### Cas d'un Déploiement sur Serveur

La procédure est **exactement la même** sur un serveur distant (VPS, machine dédiée, etc.) où Docker est installé.

Pour un véritable environnement de production, il est recommandé de placer un **reverse proxy** (comme Nginx ou Traefik) devant votre conteneur. Le reverse proxy peut gérer :
- Le **HTTPS** avec des certificats SSL/TLS (Let's Encrypt).
- Le routage d'un nom de domaine (ex: `stats.votredomaine.com`) vers le conteneur.
- La mise en cache et la répartition de charge.
