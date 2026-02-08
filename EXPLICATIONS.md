# Fichier d'Explications du Projet Moniteur Système

Ce document rassemble les explications fournies avant chaque modification majeure du code, servant de journal de développement et de documentation technique.

---

## 1. Initialisation du Projet

- **`requirements.txt`**: Création du fichier pour lister les dépendances Python (`Flask`, `psutil`).
- **`app.py`**: Mise en place d'un serveur Flask de base avec un endpoint API `/data` pour collecter les métriques système (CPU, mémoire, disque) via `psutil`, et une route `/` pour servir la page web.
- **`templates/index.html`**: Création d'une page HTML simple avec du JavaScript pour appeler l'API `/data` toutes les 3 secondes et afficher les résultats.

---

## 2. Versioning avec Git

- **`git init`**: Initialisation d'un dépôt Git local.
- **`.gitignore`**: Création d'un fichier pour exclure du suivi les répertoires non pertinents (`venv/`, `__pycache__/`, `*.pyc`).
- **`git commit`**: Création d'un commit initial sauvegardant la première version fonctionnelle de l'application.

---

## 3. Ajout des Fonctionnalités d'Amélioration

### 3.1. Identifier les Fichiers/Répertoires Gourmands

- **Backend (`app.py`)**:
    - **Objectif**: Créer un endpoint `/disk-usage-details` pour lister les 10 fichiers/dossiers les plus volumineux.
    - **Implémentation**: Utilisation du module `subprocess` pour exécuter la commande shell `du -sh ~/* | sort -rh | head -n 10`. Le résultat est ensuite parsé et renvoyé en JSON. Une gestion d'erreur a été ajoutée pour les cas où la commande échouerait.
- **Frontend (`templates/index.html`)**:
    - **Objectif**: Afficher la liste des fichiers/dossiers volumineux.
    - **Implémentation**: Ajout d'une nouvelle section HTML et d'une fonction JavaScript `fetchDiskUsageDetails()`. Cette fonction appelle l'API, reçoit les données, et construit dynamiquement une liste `<ul>` pour les afficher.

### 3.2. Intégrer des Graphiques en Temps Réel (Chart.js)

- **Frontend (`templates/index.html`)**:
    - **Objectif**: Remplacer l'affichage textuel des pourcentages par des graphiques de type "jauge" plus visuels.
    - **Implémentation**:
        1.  Ajout du CDN de Chart.js.
        2.  Remplacement des éléments `<span>` par des `<canvas>`.
        3.  Création d'une fonction `createGaugeChart()` pour initialiser les graphiques.
        4.  Modification de `fetchSystemData()` pour mettre à jour les données des graphiques (`chart.update()`) au lieu de simplement changer le texte.

### 3.3. Afficher la Liste des Processus Gourmands

- **Backend (`app.py`)**:
    - **Objectif**: Créer un endpoint `/processes` pour lister les processus consommant le plus de CPU.
    - **Implémentation**: Utilisation de `psutil.process_iter()` pour parcourir les processus, extraire les informations pertinentes (PID, nom, %CPU, %Mémoire), trier la liste par utilisation CPU, et renvoyer le top 10 en JSON.
- **Frontend (`templates/index.html`)**:
    - **Objectif**: Afficher la liste des processus dans un tableau.
    - **Implémentation**: Ajout d'une structure de tableau `<table>` en HTML. Création d'une fonction JavaScript `fetchProcessData()` qui appelle l'API `/processes` toutes les 5 secondes et reconstruit dynamiquement les lignes du tableau.

### 3.4. Ajouter la Surveillance du Réseau

- **Backend (`app.py`)**:
    - **Objectif**: Inclure les statistiques réseau dans l'API principale.
    - **Implémentation**: Modification de la route `/data` pour y ajouter les données de `psutil.net_io_counters()` (octets envoyés et reçus), converties en Go.
- **Frontend (`templates/index.html`)**:
    - **Objectif**: Afficher les nouvelles données réseau.
    - **ImplémentATION**: Ajout d'une section "Activité Réseau" en HTML et mise à jour de `fetchSystemData()` pour remplir les nouveaux champs.

### 3.5. Conteneurisation avec Docker

- **`requirements.txt`**: Ajout de `gunicorn`, un serveur WSGI de production plus robuste que le serveur de développement de Flask.
- **`Dockerfile`**:
    - **Objectif**: Créer une image Docker pour rendre l'application portable.
    - **Implémentation**:
        1.  Utilisation d'une image de base `python:3.9-slim`.
        2.  Copie des fichiers du projet.
        3.  Installation des dépendances via `pip`.
        4.  Exposition du port `8000`.
        5.  Définition de `gunicorn` comme commande de démarrage du conteneur.

### 3.6. Mettre en Place un Historique des Données (SQLite)

- **`requirements.txt`**: Ajout de `APScheduler` pour gérer des tâches en arrière-plan.
- **Backend (`app.py`)**:
    - **Objectif**: Enregistrer périodiquement les métriques et créer une API pour les consulter.
    - **Implémentation**:
        1.  Mise en place d'une base de données `monitor.db` avec SQLite.
        2.  Création d'une fonction `log_metrics()` qui enregistre le CPU, la mémoire et le disque dans la base de données.
        3.  Configuration de `APScheduler` pour exécuter `log_metrics()` toutes les 5 minutes.
        4.  Création d'une nouvelle route `/history` qui récupère les données des dernières 24 heures et les renvoie.
- **Frontend (`templates/index.html`)**:
    - **Objectif**: Afficher l'historique dans un graphique linéaire.
    - **Implémentation**:
        1.  Ajout des CDN pour `date-fns` et `chartjs-adapter-date-fns` pour que Chart.js puisse gérer les axes temporels.
        2.  Ajout d'un `<canvas>` pour le nouveau graphique.
        3.  Création d'une fonction `fetchHistoryData()` qui appelle l'API `/history` et dessine un graphique linéaire avec les données reçues.
