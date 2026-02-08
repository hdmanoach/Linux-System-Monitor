# 🖥️ Linux System Monitor

Une application web moderne et intuitive pour surveiller en temps réel les ressources système Linux, Windows (CPU, mémoire, disque) avec analyse IA intégrée.

## 📋 Table des matières

- [Caractéristiques](#caractéristiques)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du Projet](#structure-du-projet)
- [API Endpoints](#api-endpoints)
- [Déploiement Docker](#déploiement-docker)
- [Contribuer](#contribuer)
- [License](#license)

## ✨ Caractéristiques

### Surveillance en Temps Réel
- 📊 **Métriques CPU, Mémoire et Disque** - Affichage instantané des ressources système (Linux, Windows, macOS)
- 🔄 **Mise à jour automatique** - Rafraîchissement toutes les secondes
- 📈 **Graphiques historiques** - Visualisation des données sur les 24 dernières heures
- 🎯 **Alertes intelligentes** - Notifications quand les seuils sont dépassés

### Analyse Système Avancée
- 🔍 **Détection des fichiers gourmands** - Identifiez les répertoires occupant le plus d'espace disque
- ⚙️ **Moniteur de processus** - Top 10 des processus consommant le plus de ressources
- 🌐 **Statistiques réseau** - Suivi des données envoyées/reçues
- 🛠️ **Liste des services** - État détaillé de tous les services système

### Intelligence Artificielle
- 🤖 **Analyse IA avec Gemini** - Analysez automatiquement les processus, services et fichiers
- 📝 **Recommandations intelligentes** - Commandes et explications fournies par IA
- 🔒 **Sécurité** - Évaluation du risque avant suppression ou arrêt

### Recherche Intégrée
- 🔎 **Recherche multi-domaines** - Trouvez rapidement processus, services et fichiers
- 💡 **Suggestions intelligentes** - Résultats filtrés en temps réel

## 🔧 Prérequis

- Python 3.8+
- **Systèmes d'exploitation supportés :** Linux (Ubuntu, Debian, CentOS...), Windows, macOS
- pip (gestionnaire de paquets Python)
- Navigateur web moderne (Chrome, Firefox, Edge, Safari)
- *(Optionnel)* Clé API Google Gemini pour les analyses IA

## 📦 Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/hdmanoach/Linux-System-Monitor.git
cd Linux-System-Monitor
```

### 2. Créer un environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration (optionnel pour l'IA)
```bash
cp .env.example .env
```

Éditer le fichier `.env` et ajouter votre clé API Gemini :
```env
GEMINI_API_KEY=votre_cle_api_gemini_ici
```

Obtenir une clé API gratuite sur [Google AI Studio](https://aistudio.google.com)

## 🚀 Utilisation

### Démarrage de l'application
```bash
python app.py
```

L'application est accessible via `http://localhost:5000`

### Accès au tableau de bord
- **Accueil** - `http://localhost:5000/` - Vue d'ensemble des ressources
- **Recherche** - Utilisez la barre de recherche pour filtrer processus, services ou fichiers
- **Historique** - Consultez les graphiques des 24 dernières heures

## 📁 Structure du Projet

```
Linux-System-Monitor/
├── app.py                    # Application Flask principale
├── disk_utils.py             # Utilitaires pour l'analyse disque
├── monitor.db                # Base de données SQLite (créée automatiquement)
├── requirements.txt          # Dépendances Python
├── .env                      # Variables d'environnement (non versionné)
├── Dockerfile                # Configuration Docker
├── DOCKER_GUIDE.md          # Guide de déploiement Docker
├── PLAN.md                  # Roadmap du projet
├── EXPLICATIONS.md          # Documentation technique détaillée
├── templates/
│   ├── index.html           # Tableau de bord principal
│   └── search_results.html  # Page de résultats recherche
└── README.md                # Ce fichier
```

## 🔌 API Endpoints

### Données Système

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Tableau de bord principal |
| `/data` | GET | Métriques actuelles (CPU, mémoire, disque, réseau) |
| `/history` | GET | Historique des 24 dernières heures |

### Processus & Services

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/processes` | GET | Top 10 des processus par consommation CPU |
| `/services_status` | GET | Liste complète des services système |
| `/search` | GET | Recherche multi-domaines (query: string) |

### Disque & Fichiers

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/drives` | GET | Liste des partitions disque |
| `/disk-usage-details` | GET | Analyse détaillée disque (path: string) |

### Intelligence Artificielle

| Endpoint | Méthode | Description | Payload |
|----------|---------|-------------|---------|
| `/analyze` | POST | Analyse IA d'un élément | `{"type": "process\|service\|disk", "data": {...}}` |

### Exemples de requêtes

**Récupérer les métriques actuelles:**
```bash
curl http://localhost:5000/data
```

**Rechercher un processus:**
```bash
curl "http://localhost:5000/search?query=firefox"
```

**Analyser un processus avec IA:**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"type": "process", "data": {"pid": 1234, "name": "python", "cpu_percent": 25.5}}'
```

## 🐳 Déploiement Docker

### Build de l'image
```bash
docker build -t linux-system-monitor .
```

### Exécution du conteneur
```bash
docker run -d \
  --name monitor \
  -p 5000:5000 \
  -v /proc:/proc:ro \
  -v /sys:/sys:ro \
  -e GEMINI_API_KEY=votre_cle_api \
  linux-system-monitor
```

Consulter [DOCKER_GUIDE.md](DOCKER_GUIDE.md) pour des instructions détaillées.

## 🛠️ Configuration Avancée

### Variables d'environnement

```env
# Clé API pour les analyses Gemini
GEMINI_API_KEY=sk-...

# Port de l'application (optionnel)
FLASK_PORT=5000

# Mode debug
FLASK_ENV=production
```

### Base de données

L'application crée automatiquement une base SQLite `monitor.db` pour stocker l'historique. Pour réinitialiser:

```bash
rm monitor.db
python app.py  # Recréera une base vide
```

## 📊 Fonctionnement Technique

### Collecte des métriques
- **APScheduler** : Tâche de fond qui collecte les métriques toutes les 5 minutes
- **Psutil** : Bibliothèque système pour accéder aux infos du système d'exploitation (compatible multi-OS)
- **SQLite** : Stockage persistant de l'historique

### Analyse disque multi-plateforme
L'application implémente deux stratégies pour le scan disque :
- **Linux** : Utilise la commande optimisée `du` pour des scans ultra-rapides
- **Windows/macOS** : Utilise `os.walk()` en Python pour une approche multiplateforme compatible
- Détection automatique du système pour appliquer la stratégie appropriée

### Intelligence Artificielle
- **API Gemini** : Modèle `gemini-flash-latest` pour analyses rapides
- Contexte automatique selon le type d'élément et l'OS
- Réponses en Markdown avec commandes shell prêtes à l'emploi (adaptées à chaque OS)

## 🐛 Dépannage

### "Avertissement: La variable d'environnement GEMINI_API_KEY n'est pas définie"
L'IA n'est pas disponible. Créez un fichier `.env` avec votre clé API ou ignorez le message pour utiliser l'app sans IA.

### "Permission denied" lors de la recherche de services
Sur Linux, les droits administrateur peuvent être nécessaires pour certaines opérations. Exécutez avec `sudo` si besoin ou via Docker.

### Base de données verrouillée
Redémarrez l'application ou supprimez `monitor.db`.

## 🚀 Roadmap Future

- [ ] Dashboard multi-utilisateurs avec authentification
- [ ] Alertes par email/webhook
- [ ] API REST complète (OpenAPI/Swagger)
- [ ] Tests unitaires complets
- [ ] Thème sombre/clair personnalisable
- [ ] Export des métriques (CSV, JSON)
- [ ] Application desktop (Electron/PyQt)

## 📸 Captures d'écran

<img width="1366" height="639" alt="image" src="https://github.com/user-attachments/assets/2fa142e5-26ee-4c8c-a3e4-8fef290a0932" />


## 💡 Conseils d'utilisation

1. **Performance optimale** : Laissez l'app tourner quelques heures pour avoir un historique significatif
2. **Alertes** : Les seuils par défaut sont à 80% - modifiez-les selon vos besoins dans `app.py`
3. **Utilisation disque** : La première scan du répertoire personnel peut être longue (~10s) selon la taille
4. **Sécurité** : Ne partagez jamais votre clé API Gemini, stockez-la dans `.env` (non versionné)

## 🤝 Contribuer

Les contributions sont les bienvenues ! Pour proposer des améliorations :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 License

Ce projet est licensé sous la MIT License - voir le fichier [LICENSE](LICENSE) pour les détails.

## 👨‍💻 Auteur

Créé avec ❤️ par [Manoach](https://github.com/hdmanoach)

## 📞 Support

- 📧 Email : hdmanoach@gmail.com
- 🐛 Issues : [Créer une issue](https://github.com/hdmanoach/Linux-System-Monitor/issues)
- 💬 Discussions : [Rejoindre les discussions](https://github.com/hdmanoach/Linux-System-Monitor/discussions)

---

**⭐ Si ce projet vous a été utile, pensez à laisser une star !**
