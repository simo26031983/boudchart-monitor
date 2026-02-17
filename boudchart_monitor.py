#!/usr/bin/env python3
"""
Script de monitoring dual avec logs détaillés pour debug
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import logging
import os
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))
BOUDCHART_URL = "https://www.boudchart.com/"
STADE_TOULOUSAIN_URL = "https://billetterie.stadetoulousain.fr/fr/catalogue/match-rugby-stade-toulousain-montpellier-herault-rugby-club"
STATE_FILE = "monitoring_state.json"
LOG_FILE = "monitoring.log"

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class DualMonitor:
    def __init__(self):
        self.state_file = Path(STATE_FILE)
        self.boudchart_status = None
        self.stade_toulousain_found = False
        self.load_state()
        
        # Configuration des notifications
        self.telegram_config = {
            'enabled': os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true',
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
        }
        
        logging.info(f"Configuration:")
        logging.info(f"  - Telegram: {'✅' if self.telegram_config['enabled'] else '❌'}")
    
    def load_state(self):
        """Charge l'état précédent"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.boudchart_status = data.get('boudchart_status')
                    self.stade_toulousain_found = data.get('stade_toulousain_found', False)
                    logging.info(f"État chargé: Boudchart={self.boudchart_status}, Stade={self.stade_toulousain_found}")
            except Exception as e:
                logging.error(f"Erreur chargement état: {e}")
    
    def save_state(self):
        """Sauvegarde l'état"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'boudchart_status': self.boudchart_status,
                    'stade_toulousain_found': self.stade_toulousain_found,
                    'last_check': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logging.error(f"Erreur sauvegarde: {e}")
    
    def fetch_page(self, url, site_name=""):
        """Récupère une page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            logging.info(f"[{site_name}] Page récupérée: {len(response.text)} caractères")
            return response.text
        except Exception as e:
            logging.error(f"[{site_name}] Erreur récupération: {e}")
            return None
    
    def check_boudchart(self, html_content):
        """Vérifie Boudchart - VERSION CORRIGÉE (Parsing Texte)"""
        try:
            # 1. On utilise BeautifulSoup pour nettoyer le HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 2. On extrait uniquement le texte visible, séparé par des espaces
            # Cela transforme "<div>Casablanca</div><div>...</div><button>SOON</button>"
            # en "Casablanca ... SOON"
            text_clean = soup.get_text(separator=' ').upper()
            
            # 3. On nettoie les espaces multiples pour avoir une chaine propre
            text_clean = " ".join(text_clean.split())
            
            # Trouver "CASABLANCA"
            casa_pos = text_clean.find('CASABLANCA')
            
            if casa_pos == -1:
                logging.warning("[Boudchart] 'Casablanca' non trouvé dans le texte visible!")
                return None
            
            # 4. On extrait une fenêtre de texte après Casablanca
            # Comme on a retiré le HTML, 100 caractères suffisent largement
            text_after = text_clean[casa_pos:casa_pos+100]
            
            # Log pour debug
            logging.info(f"[Boudchart] Texte visible après 'CASABLANCA': {text_after}...")
            
            # Liste des autres villes pour éviter les faux positifs
            other_cities = ['PARIS', 'BORDEAUX', 'TOULOUSE', 'MARSEILLE', 'BRUSSELS', 
                          'MADRID', 'OTTAWA', 'MONTREAL', 'TORONTO', 'GENEVA', 
                          'TANGIER', 'DÜSSELDORF', 'LILLE', 'LYON']
            
            # Fonction utilitaire pour vérifier si le statut appartient bien à Casablanca
            def is_valid_match(keyword, text_segment):
                if keyword not in text_segment:
                    return False
                keyword_pos = text_segment.find(keyword)
                before_keyword = text_segment[:keyword_pos]
                # Si une autre ville apparait entre Casablanca et le mot clé, ce n'est pas le bon concert
                if any(city in before_keyword for city in other_cities):
                    return False
                return True

            # Vérifications des statuts
            if is_valid_match('TICKETS', text_after):
                logging.info("[Boudchart] ✅ Statut détecté: TICKETS")
                return 'TICKETS'
            
            if is_valid_match('SOON', text_after):
                logging.info("[Boudchart] ✅ Statut détecté: SOON")
                return 'SOON'
                
            if is_valid_match('SOLD OUT', text_after) or is_valid_match('SOLD-OUT', text_after) or is_valid_match('COMPLET', text_after):
                logging.info("[Boudchart] ✅ Statut détecté: SOLD_OUT")
                return 'SOLD_OUT'
            
            logging.warning("[Boudchart] ⚠️ Aucun statut connu trouvé juste après Casablanca")
            return None
            
        except Exception as e:
            logging.error(f"[Boudchart] ❌ Erreur: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return None
    
    def check_stade_toulousain(self, html_content):
        """Vérifie Stade Toulousain"""
        try:
            text_upper = html_content.upper()
            
            if 'PETIT COP STADE TOULOUSAIN' in text_upper:
                logging.info("[Stade Toulousain] ✅✅✅ 'PETIT COP STADE TOULOUSAIN' TROUVÉ!")
                return True
            
            logging.info("[Stade Toulousain] ❌ 'PETIT COP STADE TOULOUSAIN' non trouvé")
            return False
            
        except Exception as e:
            logging.error(f"[Stade Toulousain] ❌ Erreur: {e}")
            return False
    
    def send_telegram_notification(self, event_type, details=None):
        """Envoie notification Telegram"""
        
        if event_type == "boudchart":
            message = f"""🎭 <b>ALERTE BOUDCHART</b> 🎭

Le statut du spectacle de <b>Casablanca</b> a changé !
<b>Nouveau statut:</b> {details.get('status')}

🔗 <a href='{BOUDCHART_URL}'>Vérifier le site</a>

---
{datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"""
        
        elif event_type == "stade_toulousain":
            message = f"""🏉 <b>ALERTE STADE TOULOUSAIN</b> 🏉

<b>"PETIT COP STADE TOULOUSAIN"</b> est maintenant disponible !

Match: <b>Stade Toulousain vs Montpellier</b>

🔗 <a href='{STADE_TOULOUSAIN_URL}'>Réserver maintenant</a>

---
{datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"""
        
        logging.info(f"NOTIFICATION: {event_type}")
        print("\n" + "="*60)
        print(message)
        print("="*60 + "\n")
        
        # Telegram
        if self.telegram_config['enabled']:
            try:
                url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
                
                response = requests.post(url, json={
                    "chat_id": self.telegram_config['chat_id'],
                    "text": message,
                    "parse_mode": "HTML"
                }, timeout=10)
                
                response.raise_for_status()
                logging.info("✅ Telegram envoyé!")
            except Exception as e:
                logging.error(f"❌ Erreur Telegram: {e}")
    
    def check_all(self):
        """Vérifie tous les sites"""
        logging.info("="*60)
        logging.info("🔍 VÉRIFICATION EN COURS...")
        logging.info("="*60)
        
        # 1. Boudchart
        logging.info("\n[1/2] Vérification Boudchart...")
        boudchart_html = self.fetch_page(BOUDCHART_URL, "Boudchart")
        
        if boudchart_html:
            new_status = self.check_boudchart(boudchart_html)
            
            if new_status:
                if self.boudchart_status != new_status:
                    logging.info(f"[Boudchart] 🔔 Changement: {self.boudchart_status} → {new_status}")
                    
                    if new_status == 'TICKETS':
                        self.send_telegram_notification("boudchart", {"status": new_status})
                    
                    self.boudchart_status = new_status
                else:
                    logging.info(f"[Boudchart] ✓ Pas de changement: {new_status}")
        
        # 2. Stade Toulousain
        logging.info("\n[2/2] Vérification Stade Toulousain...")
        stade_html = self.fetch_page(STADE_TOULOUSAIN_URL, "Stade Toulousain")
        
        if stade_html:
            found = self.check_stade_toulousain(stade_html)
            
            if found and not self.stade_toulousain_found:
                logging.info("[Stade Toulousain] 🔔 NOUVEAU: PETIT COP trouvé!")
                self.send_telegram_notification("stade_toulousain")
                self.stade_toulousain_found = True
            elif found:
                logging.info("[Stade Toulousain] ✓ Déjà trouvé")
            else:
                logging.info("[Stade Toulousain] ✓ Toujours absent")
        
        # Sauvegarder
        self.save_state()
        
        logging.info("="*60)
        logging.info(f"💤 Prochaine vérification dans {CHECK_INTERVAL} secondes")
        logging.info("="*60 + "\n")
    
    def run(self):
        """Lance le monitoring"""
        logging.info("="*60)
        logging.info("🚀 DUAL MONITORING - VERSION DEBUG")
        logging.info("="*60)
        logging.info(f"📍 Site 1: Boudchart Casablanca")
        logging.info(f"📍 Site 2: Stade Toulousain Petit Cop")
        logging.info(f"⏱️  Intervalle: {CHECK_INTERVAL}s")
        logging.info("="*60 + "\n")
        
        while True:
            try:
                self.check_all()
            except Exception as e:
                logging.error(f"❌ Erreur: {e}")
            
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor = DualMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        logging.info("\n👋 Arrêt")
    except Exception as e:
        logging.error(f"💥 Erreur fatale: {e}")
