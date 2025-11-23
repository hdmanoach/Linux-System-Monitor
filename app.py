from flask import Flask, jsonify, render_template
import psutil
import subprocess
import os
import sqlite3
import atexit
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

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
    }
    return jsonify(data)

@app.route('/disk-usage-details')
def disk_usage_details():
    # ... (code existant)
    try:
        home_dir = os.path.expanduser('~')
        command = f"du -sh {home_dir}/* | sort -rh | head -n 10"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": "Erreur lors de l'exécution de la commande 'du'", "details": result.stderr}), 500
        lines = result.stdout.strip().split('\n')
        top_files = []
        for line in lines:
            if line:
                size, path = line.split('\t', 1)
                top_files.append({"size": size.strip(), "path": path.strip()})
        return jsonify(top_files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == '__main__':
    init_db()  # Initialise la base de données au démarrage
    log_metrics() # Log initial
    app.run(debug=True)

