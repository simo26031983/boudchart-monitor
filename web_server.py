#!/usr/bin/env python3
"""
Serveur web wrapper pour Boudchart Monitor
Permet de déployer sur Render Web Service (gratuit) au lieu de Background Worker (payant)
"""

from flask import Flask, jsonify
import threading
import logging
import os
from boudchart_monitor import BoudchartMonitor

app = Flask(__name__)
monitor = None
monitor_thread = None

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/')
def home():
    """Page d'accueil"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Boudchart Monitor</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; }
            .status { 
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
            }
            .info {
                color: #666;
                line-height: 1.6;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎭 Boudchart Monitor</h1>
            <div class="status">
                <strong>✅ Service actif</strong>
            </div>
            <div class="info">
                <p>Le monitoring du site Boudchart est en cours d'exécution.</p>
                <p>Surveillance: Spectacle de Casablanca</p>
                <p>Vérification toutes les 5 minutes</p>
                <p><a href="/health">Voir le statut →</a></p>
            </div>
        </div>
    </body>
    </html>
    """, 200

@app.route('/health')
def health():
    """Endpoint de santé pour les checks"""
    if monitor:
        status = {
            "status": "ok",
            "service": "boudchart-monitor",
            "casablanca_status": monitor.current_status or "checking",
            "monitoring": True
        }
    else:
        status = {
            "status": "starting",
            "service": "boudchart-monitor",
            "monitoring": False
        }
    return jsonify(status), 200

@app.route('/ping')
def ping():
    """Endpoint simple pour UptimeRobot"""
    return "pong", 200

def run_monitor():
    """Lance le monitoring dans un thread séparé"""
    global monitor
    try:
        logging.info("Démarrage du monitoring Boudchart...")
        monitor = BoudchartMonitor()
        monitor.run()
    except Exception as e:
        logging.error(f"Erreur dans le thread de monitoring: {e}")

if __name__ == '__main__':
    # Démarrer le monitoring dans un thread daemon
    logging.info("Lancement du serveur web...")
    monitor_thread = threading.Thread(target=run_monitor, daemon=True)
    monitor_thread.start()
    
    # Démarrer le serveur Flask
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
