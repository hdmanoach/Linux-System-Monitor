from flask import Flask, jsonify, render_template
import psutil

app = Flask(__name__)

# Cette route sert la page HTML principale du moniteur.
@app.route('/')
def index():
    return render_template('index.html')

# Cette route API fournit les données système en temps réel.
@app.route('/data')
def system_data():
    cpu_percent = psutil.cpu_percent(interval=1)  # Utilisation du CPU sur 1 seconde
    memory_info = psutil.virtual_memory()         # Informations sur la mémoire virtuelle
    disk_usage = psutil.disk_usage('/')           # Utilisation du disque pour la racine

    data = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_info.percent,
        'memory_total_gb': round(memory_info.total / (1024**3), 2),
        'memory_used_gb': round(memory_info.used / (1024**3), 2),
        'disk_percent': disk_usage.percent,
        'disk_total_gb': round(disk_usage.total / (1024**3), 2),
        'disk_used_gb': round(disk_usage.used / (1024**3), 2),
    }
    return jsonify(data)

if __name__ == '__main__':
    # Lance l'application Flask en mode debug.
    # En production, utilisez un serveur WSGI comme Gunicorn ou uWSGI.
    app.run(debug=True)
