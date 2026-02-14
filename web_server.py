#!/usr/bin/env python3
"""
Serveur web wrapper pour Boudchart Monitor
Permet de déployer sur Render Web Service (gratuit) au lieu de Background Worker (payant)
"""

from flask import Flask, jsonify
import threading
import logging
import os
from boudchart_monitor import DualMonitor

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
    # Obtenir les statuts actuels si disponibles
    boudchart_status = "Vérification..."
    stade_status = "Vérification..."
    
    if monitor:
        boudchart_status = monitor.boudchart_status or "En attente"
        stade_status = "Trouvé ✅" if monitor.stade_toulousain_found else "Non trouvé ❌"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dual Monitor</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #2c3e50; margin-bottom: 10px; }}
            .subtitle {{ color: #7f8c8d; margin-bottom: 30px; }}
            .status {{ 
                padding: 15px;
                margin: 15px 0;
                border-radius: 5px;
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
            }}
            .monitoring-item {{
                background: #f8f9fa;
                padding: 20px;
                margin: 15px 0;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }}
            .monitoring-item h3 {{
                margin-top: 0;
                color: #2c3e50;
            }}
            .monitoring-item p {{
                margin: 8px 0;
                color: #666;
            }}
            .status-badge {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
            .status-soon {{ background: #fff3cd; color: #856404; }}
            .status-tickets {{ background: #d4edda; color: #155724; }}
            .status-found {{ background: #d4edda; color: #155724; }}
            .status-notfound {{ background: #f8d7da; color: #721c24; }}
            .info {{
                color: #666;
                line-height: 1.6;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .links {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Dual Monitor</h1>
            <div class="subtitle">Surveillance automatique de 2 sites</div>
            
            <div class="status">
                <strong>✅ Service actif</strong>
            </div>
            
            <div class="monitoring-item">
                <h3>🎭 Boudchart - Casablanca</h3>
                <p><strong>Site:</strong> <a href="https://www.boudchart.com/" target="_blank">www.boudchart.com</a></p>
                <p><strong>Surveillance:</strong> Changement de statut SOON → TICKETS</p>
                <p><strong>Statut actuel:</strong> <span class="status-badge status-{boudchart_status.lower()}">{boudchart_status}</span></p>
            </div>
            
            <div class="monitoring-item">
                <h3>🏉 Stade Toulousain</h3>
                <p><strong>Site:</strong> <a href="https://billetterie.stadetoulousain.fr" target="_blank">billetterie.stadetoulousain.fr</a></p>
                <p><strong>Surveillance:</strong> Apparition de "PETIT COP STADE TOULOUSAIN"</p>
                <p><strong>Statut actuel:</strong> <span class="status-badge {'status-found' if monitor and monitor.stade_toulousain_found else 'status-notfound'}">{stade_status}</span></p>
            </div>
            
            <div class="info">
                <p>✓ Vérification automatique toutes les 5 minutes</p>
                <p>✓ Notifications Telegram instantanées</p>
            </div>
            
            <div class="links">
                <p><a href="/health">📊 API Statut (JSON) →</a></p>
                <p><a href="/test-telegram">📱 Test Telegram →</a></p>
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
            "service": "dual-monitor",
            "monitoring": True,
            "boudchart": {
                "casablanca_status": monitor.boudchart_status or "checking"
            },
            "stade_toulousain": {
                "petit_cop_found": monitor.stade_toulousain_found
            }
        }
    else:
        status = {
            "status": "starting",
            "service": "dual-monitor",
            "monitoring": False
        }
    return jsonify(status), 200

@app.route('/ping')
def ping():
    """Endpoint simple pour UptimeRobot"""
    return "pong", 200

@app.route('/test-telegram')
def test_telegram():
    """Endpoint pour tester les notifications Telegram"""
    import requests
    
    telegram_enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
    
    if not telegram_enabled:
        return jsonify({
            "status": "error",
            "message": "Telegram n'est pas activé. Configurez TELEGRAM_ENABLED=true"
        }), 400
    
    if not bot_token or not chat_id:
        return jsonify({
            "status": "error",
            "message": "Token ou Chat ID manquant"
        }), 400
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        message = """🎭 <b>TEST - ALERTE BOUDCHART</b> 🎭

✅ <b>Félicitations!</b> Les notifications Telegram fonctionnent parfaitement!

Ceci est un message de <b>TEST</b>.

Quand le statut de Casablanca passera de "SOON" à "TICKETS", vous recevrez exactement ce type de notification!

🔗 <a href='https://www.boudchart.com/'>Vérifier le site</a>

---
📊 Statut actuel: SOON
⏱️ Vérification: Toutes les 5 minutes
🎉 Tout est opérationnel!"""
        
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        
        response.raise_for_status()
        
        return jsonify({
            "status": "success",
            "message": "Message de test envoyé sur Telegram! Vérifiez votre application.",
            "telegram_response": response.json()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur: {str(e)}"
        }), 500

def run_monitor():
    """Lance le monitoring dans un thread séparé"""
    global monitor
    try:
        logging.info("Démarrage du monitoring Boudchart & Stade Toulousain...")
        monitor = DualMonitor()
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
