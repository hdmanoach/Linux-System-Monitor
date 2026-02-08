# Guide d'utilisation de Docker pour le Moniteur Système

Ce guide explique comment construire une image Docker pour l'application et comment lancer un conteneur basé sur cette image.

## Prérequis

- Docker doit être installé sur votre machine.

## Étape 1 : Construire l'image Docker

1.  Ouvrez un terminal à la racine de votre projet (là où se trouve le `Dockerfile`).
2.  Exécutez la commande suivante pour construire l'image.

    -   `docker build`: C'est la commande pour construire une image.
    -   `-t system-monitor`: Le `-t` (tag) donne un nom à votre image (ici, `system-monitor`). Vous pouvez choisir un autre nom.
    -   `.`: Le point indique que le contexte de la construction est le répertoire actuel.

    ```bash
    docker build -t system-monitor .
    ```

    Cette commande va suivre les instructions du `Dockerfile`, télécharger l'image de base, installer les dépendances et copier vos fichiers pour créer une image nommée `system-monitor`.

## Étape 2 : Lancer un conteneur à partir de l'image

Une fois l'image construite, vous pouvez lancer un conteneur.

1.  **Récupérez votre clé API Gemini.** C'est très important, car elle doit être fournie au conteneur.

2.  Exécutez la commande suivante pour démarrer le conteneur :

    -   `docker run`: C'est la commande pour lancer un conteneur.
    -   `--rm`: Supprime automatiquement le conteneur lorsque vous l'arrêtez. C'est pratique pour le nettoyage.
    -   `-d`: Lance le conteneur en mode "détaché" (en arrière-plan). Si vous voulez voir les logs en direct, supprimez cette option.
    -   `-p 8080:8000`: Le `-p` (publish) mappe un port de votre machine (ici, `8080`) au port exposé par le conteneur (ici, `8000`). Vous pourrez accéder à l'application via `http://localhost:8080`.
    -   `-e GEMINI_API_KEY="VOTRE_CLE_API_ICI"`: Le `-e` (environment) définit une variable d'environnement à l'intérieur du conteneur. C'est la méthode sécurisée pour passer votre clé API. **Remplacez `VOTRE_CLE_API_ICI` par votre véritable clé.**
    -   `--name monitor-app`: Donne un nom facile à retenir à votre conteneur.
    -   `system-monitor`: Le nom de l'image que vous voulez utiliser.

    ```bash
    docker run --rm -d -p 8080:8000 -e GEMINI_API_KEY="VOTRE_CLE_API_ICI" --name monitor-app system-monitor
    ```

## Étape 3 : Accéder à l'application

Ouvrez votre navigateur web et allez à l'adresse suivante :

[http://localhost:8080](http://localhost:8080)

## Commandes Docker utiles

-   **Pour voir les logs du conteneur (si vous l'avez lancé en mode détaché) :**
    ```bash
    docker logs monitor-app
    ```

-   **Pour suivre les logs en direct :**
    ```bash
    docker logs -f monitor-app
    ```

-   **Pour arrêter le conteneur :**
    ```bash
    docker stop monitor-app
    ```

-   **Pour lister les conteneurs en cours d'exécution :**
    ```bash
    docker ps
    ```