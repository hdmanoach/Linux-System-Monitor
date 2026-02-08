from flask import Flask, jsonify, render_template, request, redirect, url_for
import psutil
import platform
import os
import sqlite3
import atexit
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from disk_utils import get_disk_usage_linux, get_disk_usage_cross_platform, search_disk
import subprocess
from dotenv import load_dotenv # Importation de load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# --- Configuration de la base de données et du planificateur ---
DATABASE = 'monitor.db'


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp DATETIME PRIMARY KEY,
            cpu_percent REAL,
            memory_percent REAL,
            disk_percent REAL
        )
    ''')
    conn.commit()
    conn.close()

def log_metrics():
    """Fonction pour collecter et enregistrer les métriques système."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    cursor.execute(
        "INSERT INTO metrics (timestamp, cpu_percent, memory_percent, disk_percent) VALUES (?, ?, ?, ?)",
        (datetime.now(), cpu, mem, disk)
    )
    conn.commit()
    conn.close()
    print(f"Logged metrics at {datetime.now()}: CPU {cpu}%, Mem {mem}%, Disk {disk}%")

# Initialise le planificateur pour exécuter log_metrics toutes les 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(func=log_metrics, trigger="interval", minutes=5)
scheduler.start()

# S'assure que le planificateur s'arrête proprement à la sortie de l'application
atexit.register(lambda: scheduler.shutdown())
# --- Fin de la configuration ---


app = Flask(__name__)

# Le reste de votre code Flask...
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def system_data():
    # ... (code existant)
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()

    data = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_info.percent,
        'memory_total_gb': round(memory_info.total / (1024**3), 2),
        'memory_used_gb': round(memory_info.used / (1024**3), 2),
        'disk_percent': disk_usage.percent,
        'disk_total_gb': round(disk_usage.total / (1024**3), 2),
        'disk_used_gb': round(disk_usage.used / (1024**3), 2),
        'net_bytes_sent_gb': round(net_io.bytes_sent / (1024**3), 2),
        'net_bytes_recv_gb': round(net_io.bytes_recv / (1024**3), 2),
        'platform': platform.system(), # Ajout de la plateforme
    }
    return jsonify(data)

@app.route('/drives')
def get_drives():
    """Retourne la liste des partitions de disque disponibles."""
    partitions = psutil.disk_partitions()
    # On ne retourne que le point de montage (ex: 'C:\\', '/boot')
    drive_paths = [p.mountpoint for p in partitions]
    return jsonify(drive_paths)


@app.route('/disk-usage-details')
def disk_usage_details():
    path_to_scan = request.args.get('path', os.path.expanduser('~'))
    
    current_os = platform.system()
    if current_os == "Linux":
        # Pour Linux, on continue de scanner le répertoire personnel par défaut pour la rapidité
        data = get_disk_usage_linux(os.path.expanduser('~'))
    else:
        # Pour les autres OS (Windows), on utilise le chemin fourni
        data = get_disk_usage_cross_platform(path_to_scan)
        
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data)

@app.route('/processes')
def top_processes():
    # ... (code existant)
    processes = []
    attrs = ['pid', 'name', 'username', 'cpu_percent', 'memory_percent']
    for p in psutil.process_iter(attrs=attrs):
        try:
            p.info['cpu_percent'] = p.cpu_percent(interval=0.1)
            processes.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    top_processes = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:10]
    for p in top_processes:
        p['memory_percent'] = round(p['memory_percent'], 2)
    return jsonify(top_processes)

# Nouvelle route API pour l'historique
@app.route('/history')
def get_history():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Récupérer les données des dernières 24 heures
    time_threshold = datetime.now() - timedelta(hours=24)
    cursor.execute("SELECT * FROM metrics WHERE timestamp >= ? ORDER BY timestamp", (time_threshold,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Formater pour Chart.js
    history_data = {
        'timestamps': [row[0] for row in rows],
        'cpu': [row[1] for row in rows],
        'memory': [row[2] for row in rows],
        'disk': [row[3] for row in rows],
    }
    return jsonify(history_data)

@app.route('/services_status')
def services_status():
    """
    Returns a list of system services and their status on Linux.
    """
    if os.name != 'posix':
        return jsonify({'error': 'This feature is only available on Linux systems.'}), 400

    try:
        command = ['systemctl', 'list-units', '--type=service', '--all', '--no-pager']
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        output_lines = result.stdout.splitlines()

        services = []
        header_found = False
        for line in output_lines:
            if line.strip().startswith('UNIT'):
                header_found = True
                continue
            if not header_found:
                continue
            if not line.strip() or line.strip().startswith('●') or 'loaded units listed' in line:
                continue

            parts = line.split(maxsplit=4)
            if len(parts) >= 4:
                unit = parts[0]
                load = parts[1]
                active = parts[2]
                sub = parts[3]
                description = parts[4] if len(parts) > 4 else ''
                
                services.append({
                    'unit': unit,
                    'load': load,
                    'active': active,
                    'sub': sub,
                    'description': description.strip()
                })

        return jsonify(services)

    except FileNotFoundError:
        return jsonify({'error': 'systemctl command not found. This server might not be using systemd or systemctl is not in PATH.'}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to list services: {e.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return redirect(url_for('index'))

    results = {
        'query': query,
        'processes': [],
        'services': [],
        'disk': []
    }

    # Search processes
    try:
        attrs = ['pid', 'name', 'username', 'cpu_percent', 'memory_percent']
        for p in psutil.process_iter(attrs=attrs):
            if query.lower() in p.info['name'].lower():
                results['processes'].append(p.info)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

    # Search services
    if os.name == 'posix':
        try:
            command = ['systemctl', 'list-units', '--type=service', '--all', '--no-pager']
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                if query.lower() in line.lower():
                    parts = line.split(maxsplit=4)
                    if len(parts) >= 4:
                        results['services'].append({
                            'unit': parts[0],
                            'load': parts[1],
                            'active': parts[2],
                            'sub': parts[3],
                            'description': parts[4] if len(parts) > 4 else ''
                        })
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass # Ignore errors if systemctl is not available or fails

    # Search disk
    disk_results = search_disk(query)
    if isinstance(disk_results, list):
        results['disk'] = disk_results

    return render_template('search_results.html', results=results)

# --- Configuration de l'IA Gemini ---
# IMPORTANT: Remplacez "VOTRE_CLE_API_GEMINI" par votre véritable clé API Gemini.
# Vous pouvez l'obtenir sur le site de Google AI Studio.
# Pour plus de sécurité, utilisez des variables d'environnement en production.
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Si la clé API n'est pas définie, nous ne chargerons pas le modèle IA et afficherons un avertissement.
# Cela permet à l'application de démarrer même sans la clé, mais la fonctionnalité IA sera désactivée.
if not GEMINI_API_KEY:
    model = None
    print("Avertissement: La variable d'environnement GEMINI_API_KEY n'est pas définie. Les fonctionnalités d'IA seront désactivées.")
else:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('models/gemini-flash-latest') # Correction du nom du modèle
        print("Modèle Gemini Flash (latest) chargé avec succès.")
    except ImportError:
        model = None
        print("Avertissement: La bibliothèque google-generativeai n'est pas installée. `pip install google-generativeai` pour activer les fonctionnalités d'IA.")
    except Exception as e:
        model = None
        print(f"Erreur lors de la configuration de Gemini: {e}")


@app.route('/analyze', methods=['POST'])
def analyze_item():
    # Vérifie si le modèle Gemini est bien configuré
    if not model:
        return jsonify({'error': "Le modèle d'IA n'est pas configuré. Veuillez vérifier la clé API et l'installation."}), 500

    # Récupère les données envoyées par le frontend
    data = request.get_json()
    item_type = data.get('type')
    item_data = data.get('data')
    
    # Détermine le système d'exploitation du serveur pour contextualiser le prompt de l'IA
    system_os = platform.system()

    # Vérifie si les données essentielles sont présentes
    if not item_type or not item_data:
        return jsonify({'error': 'Données d\'analyse manquantes.'}), 400

    # Initialise le prompt pour l'IA avec un contexte général
    prompt = f"En tant qu'expert système pour {system_os}, analyse l'élément suivant et réponds de manière concise en français:\n\n"

    # Construit le prompt spécifique en fonction du type d'élément
    if item_type == 'process':
        # Gère les cas où le nom d'utilisateur pourrait être absent
        username = item_data.get('username', 'N/A')
        prompt += f"""
        **Élément à analyser :** Processus
        - **Nom :** {item_data.get('name')}
        - **PID :** {item_data.get('pid')}
        - **Utilisateur :** {username}
        - **% CPU :** {item_data.get('cpu_percent')}
        - **% Mémoire :** {item_data.get('memory_percent')}

        **Tâches :**
        1.  **Identifier le processus :** Quel est son rôle principal ?
        2.  **Analyser l'impact :** Quelles sont les conséquences si je l'arrête ? (Critique pour le système, application spécifique, sans danger ?)
        3.  **Proposer une action :** Fournis la commande exacte et sûre pour l'arrêter sur {system_os}. Si l'arrêt est déconseillé, dis-le clairement.
        **Formule ta réponse entièrement en Markdown.**
        """
    elif item_type == 'service':
        prompt += f"""
        **Élément à analyser :** Service
        - **Unité :** {item_data.get('unit')}
        - **État :** {item_data.get('active')} / {item_data.get('sub')}
        - **Description :** {item_data.get('description')}
        
        **Tâches :**
        1.  **Identifier le service :** À quoi sert ce service ?
        2.  **Analyser l'impact :** Qu'arrive-t-il si je le désactive ou l'arrête ? Est-ce risqué pour la stabilité ou la sécurité du système ?
        3.  **Proposer une action :** Fournis les commandes (`systemctl` pour Linux, `net` ou `sc` pour Windows, `launchctl` pour macOS) pour l'arrêter, le redémarrer et vérifier son statut.
        **Formule ta réponse entièrement en Markdown.**
        """
    elif item_type == 'disk':
        prompt += f"""
        **Élément à analyser :** Fichier ou Répertoire
        - **Chemin :** {item_data.get('path')}
        - **Taille :** {item_data.get('size')}
        
        **Tâches :**
        1.  **Estimer le contenu et la criticité :** Que pourrait contenir cet élément en se basant sur son chemin ? Fais une estimation basée sur les conventions de nommage des systèmes {system_os} (ex: fichiers journaux, fichiers temporaires, données utilisateur, fichiers système).
        2.  **Évaluer le risque :** Est-il généralement sûr de le supprimer ? Indique si c'est un fichier système critique, un cache d'application, un fichier utilisateur, etc.
        3.  **Proposer une action :** Suggérer s'il est plausible de supprimer le contenu pour libérer de l'espace, et inclure un avertissement sur les précautions à prendre.
        **Formule ta réponse entièrement en Markdown.**
        """
    else:
        # Renvoie une erreur si le type d'analyse n'est pas supporté
        return jsonify({'error': 'Type d\'analyse non supporté.'}), 400

    try:
        # Appelle le modèle Gemini pour générer l'analyse
        response = model.generate_content(prompt)
        # Renvoie la réponse de l'IA au frontend
        return jsonify({'analysis': response.text})
    except Exception as e:
        # Gère les erreurs lors de l'appel à l'API Gemini
        print(f"Erreur lors de l'appel à l'API Gemini: {e}")
        return jsonify({'error': f"Une erreur est survenue lors de la communication avec l'IA: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()  # Initialise la base de données au démarrage
    log_metrics() # Log initial
    app.run(debug=True)

