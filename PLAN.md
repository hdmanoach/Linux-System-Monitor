# Plan du Projet: Moniteur Système avec Flask

## Objectif
Créer une application web simple pour surveiller l'utilisation du CPU, de la mémoire et du disque d'un système Linux en temps réel.

## Technologies
- **Backend:** Python, Flask, psutil
- **Frontend:** HTML, CSS, JavaScript (sans framework)

## Fonctionnalités
1.  **API de Données:** Un endpoint Flask (`/data`) qui fournit les métriques système (CPU, mémoire, disque) au format JSON.
2.  **Tableau de Bord Web:** Une page HTML unique qui consomme l'API pour afficher les données.
3.  **Visualisation en Temps Réel:** Les données sont actualisées automatiquement toutes les quelques secondes.
4.  **Alertes:** Des messages d'alerte s'affichent sur la page web lorsque l'utilisation dépasse des seuils prédéfinis.

## Structure des Fichiers
- `Linux-System-Monitor/`
  - `app.py`          # Logique du serveur Flask et de l'API
  - `templates/`
    - `index.html`    # Fichier HTML du tableau de bord
  - `requirements.txt`  # Dépendances Python (Flask, psutil)
  - `PLAN.md`         # Ce fichier
