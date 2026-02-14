#!/usr/bin/env python3
"""
Script de monitoring dual pour:
1. Boudchart - Casablanca (SOON → TICKETS)
2. Stade Toulousain - Match vs Montpellier ("PETIT COP STADE TOULOUSAIN")
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
import re

# Configuration
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes
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
        self.email_config = {
            'enabled': os.getenv('EMAIL_ENABLED', 'false').lower() == 'true',
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL', ''),
            'sender_password': os.getenv('SENDER_PASSWORD', ''),
            'recipient_email': os.getenv('RECIPIENT_EMAIL', '')
        }
        
        self.telegram_config = {
            'enabled': os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true',
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
        }
        
        self.discord_config = {
            'enabled': os.getenv('DISCORD_ENABLED', 'false').lower() == 'true',
            'webhook_url': os.getenv('DISCORD_WEBHOOK_URL', '')
        }
        
        logging.info(f"Configuration chargée:")
        logging.info(f"  - Email: {'✅' if self.email_config['enabled'] else '❌'}")
        logging.info(f"  - Telegram: {'✅' if self.telegram_config['enabled'] else '❌'}")
        logging.info(f"  - Discord: {'✅' if self.discord_config['enabled'] else '❌'}")
    
    def load_state(self):
        """Charge l'état précédent depuis le fichier"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.boudchart_status = data.get('boudchart_status')
                    self.stade_toulousain_found = data.get('stade_toulousain_found', False)
                    logging.info(f"État chargé:")
                    logging.info(f"  - Boudchart: {self.boudchart_status}")
                    logging.info(f"  - Stade Toulousain: {self.stade_toulousain_found}")
            except Exception as e:
                logging.error(f"Erreur lors du chargement de l'état: {e}")
    
    def save_state(self):
        """Sauvegarde l'état actuel"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'boudchart_status': self.boudchart_status,
                    'stade_toulousain_found': self.stade_toulousain_found,
                    'last_check': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde: {e}")
    
    def fetch_page(self, url, site_name=""):
        """Récupère le contenu d'une page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de {site_name}: {e}")
            return None
    
    def check_boudchart(self, html_content):
        """Vérifie le statut Casablanca sur Boudchart"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Méthode 1: Recherche dans le texte complet
            full_text = soup.get_text()
            
            # Trouver la position de "Casablanca" dans le texte
            casa_index = full_text.upper().find('CASABLANCA')
            
            if casa_index != -1:
                # Extraire 200 caractères après "Casablanca"
                text_after_casa = full_text[casa_index:casa_index+200].upper()
                
                logging.info(f"[Boudchart] Texte après Casablanca: '{text_after_casa[:100]}'")
                
                # Chercher "TICKETS" ou "SOON" dans les 200 caractères suivants
                if 'TICKETS' in text_after_casa:
                    # Vérifier qu'on n'est pas sur un autre concert
                    # Il ne doit pas y avoir d'autre nom de ville entre Casablanca et TICKETS
                    other_cities = ['PARIS', 'BORDEAUX', 'TOULOUSE', 'MARSEILLE', 'BRUSSELS', 
                                  'MADRID', 'OTTAWA', 'MONTREAL', 'TORONTO', 'GENEVA', 
                                  'TANGIER', 'DÜSSELDORF']
                    
                    before_tickets = text_after_casa[:text_after_casa.find('TICKETS')]
                    
                    has_other_city = any(city in before_tickets for city in other_cities)
                    
                    if not has_other_city:
                        logging.info(f"[Boudchart] ✓ Statut: TICKETS")
                        return 'TICKETS'
                
                if 'SOON' in text_after_casa:
                    # Vérifier qu'on n'est pas sur un autre concert
                    other_cities = ['PARIS', 'BORDEAUX', 'TOULOUSE', 'MARSEILLE', 'BRUSSELS', 
                                  'MADRID', 'OTTAWA', 'MONTREAL', 'TORONTO', 'GENEVA', 
                                  'TANGIER', 'DÜSSELDORF']
                    
                    before_soon = text_after_casa[:text_after_casa.find('SOON')]
                    
                    has_other_city = any(city in before_soon for city in other_cities)
                    
                    if not has_other_city:
                        logging.info(f"[Boudchart] ✓ Statut: SOON")
                        return 'SOON'
                
                if 'SOLD OUT' in text_after_casa or 'SOLD-OUT' in text_after_casa:
                    logging.info(f"[Boudchart] ✓ Statut: SOLD_OUT")
                    return 'SOLD_OUT'
            
            # Méthode 2: Recherche par éléments HTML
            all_headings = soup.find_all(['h3', 'h2', 'h4'])
            
            for i, heading in enumerate(all_headings):
                heading_text = heading.get_text().strip()
                
                if 'casablanca' in heading_text.lower():
                    logging.info(f"[Boudchart] Trouvé heading: '{heading_text}'")
                    
                    # Chercher dans les 5 éléments suivants
                    next_elements = heading.find_next_siblings(limit=5)
                    
                    for elem in next_elements:
                        elem_text = elem.get_text().strip().upper()
                        
                        if 'TICKETS' in elem_text:
                            logging.info(f"[Boudchart] ✓ Statut: TICKETS (via siblings)")
                            return 'TICKETS'
                        
                        if 'SOON' in elem_text:
                            logging.info(f"[Boudchart] ✓ Statut: SOON (via siblings)")
                            return 'SOON'
            
            logging.warning("[Boudchart] ⚠️  Statut non trouvé")
            return None
            
        except Exception as e:
            logging.error(f"[Boudchart] ❌ Erreur parsing: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return None
    
    def check_stade_toulousain(self, html_content):
        """Vérifie la présence de 'PETIT COP STADE TOULOUSAIN'"""
        try:
            # Recherche de la string exacte (insensible à la casse)
            if 'PETIT COP STADE TOULOUSAIN' in html_content.upper():
                logging.info("[Stade Toulousain] ✅ 'PETIT COP STADE TOULOUSAIN' TROUVÉ!")
                return True
            
            # Recherche avec BeautifulSoup pour plus de précision
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text().upper()
            
            if 'PETIT COP STADE TOULOUSAIN' in text_content:
                logging.info("[Stade Toulousain] ✅ 'PETIT COP STADE TOULOUSAIN' TROUVÉ (via BeautifulSoup)!")
                return True
            
            logging.info("[Stade Toulousain] ❌ 'PETIT COP STADE TOULOUSAIN' non trouvé")
            return False
            
        except Exception as e:
            logging.error(f"[Stade Toulousain] Erreur parsing: {e}")
            return False
    
    def send_notification(self, event_type, details):
        """Envoie une notification selon le type d'événement"""
        
        if event_type == "boudchart":
            title = "🎭 ALERTE BOUDCHART"
            message = f"""🎭 <b>ALERTE BOUDCHART</b> 🎭

Le statut du spectacle de <b>Casablanca</b> a changé !
<b>Nouveau statut:</b> {details['status']}

🔗 <a href='{BOUDCHART_URL}'>Vérifier le site</a>

---
Notification envoyée le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"""
        
        elif event_type == "stade_toulousain":
            title = "🏉 ALERTE STADE TOULOUSAIN"
            message = f"""🏉 <b>ALERTE STADE TOULOUSAIN</b> 🏉

<b>"PETIT COP STADE TOULOUSAIN"</b> est maintenant disponible !

Match: <b>Stade Toulousain vs Montpellier</b>

🔗 <a href='{STADE_TOULOUSAIN_URL}'>Réserver maintenant</a>

---
Notification envoyée le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"""
        
        logging.info(f"NOTIFICATION: {title}")
        
        # Console
        print("\n" + "="*60)
        print(message)
        print("="*60 + "\n")
        
        # Fichier
        try:
            with open(f'NOTIFICATION_{event_type}.txt', 'w') as f:
                f.write(message)
        except Exception as e:
            logging.error(f"Erreur écriture fichier: {e}")
        
        # Email
        if self.email_config['enabled']:
            self.send_email_notification(title, message)
        
        # Telegram
        if self.telegram_config['enabled']:
            self.send_telegram_notification(message)
        
        # Discord
        if self.discord_config['enabled']:
            self.send_discord_notification(message)
    
    def send_email_notification(self, subject, message):
        """Envoie une notification par email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
            
            logging.info("✅ Email envoyé")
        except Exception as e:
            logging.error(f"❌ Erreur email: {e}")
    
    def send_telegram_notification(self, message):
        """Envoie une notification via Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            
            response = requests.post(url, json={
                "chat_id": self.telegram_config['chat_id'],
                "text": message,
                "parse_mode": "HTML"
            }, timeout=10)
            
            response.raise_for_status()
            logging.info("✅ Telegram envoyé")
        except Exception as e:
            logging.error(f"❌ Erreur Telegram: {e}")
    
    def send_discord_notification(self, message):
        """Envoie une notification via Discord"""
        try:
            response = requests.post(
                self.discord_config['webhook_url'],
                json={
                    "content": message,
                    "username": "Dual Monitor"
                },
                timeout=10
            )
            
            response.raise_for_status()
            logging.info("✅ Discord envoyé")
        except Exception as e:
            logging.error(f"❌ Erreur Discord: {e}")
    
    def check_all(self):
        """Vérifie tous les sites surveillés"""
        logging.info("="*60)
        logging.info("🔍 VÉRIFICATION EN COURS...")
        logging.info("="*60)
        
        # 1. Vérifier Boudchart
        logging.info("\n[1/2] Vérification Boudchart...")
        boudchart_html = self.fetch_page(BOUDCHART_URL, "Boudchart")
        
        if boudchart_html:
            new_status = self.check_boudchart(boudchart_html)
            
            if new_status and self.boudchart_status != new_status:
                logging.info(f"[Boudchart] 🔔 Changement: {self.boudchart_status} -> {new_status}")
                
                if new_status == 'TICKETS':
                    self.send_notification("boudchart", {"status": new_status})
                
                self.boudchart_status = new_status
            elif new_status:
                logging.info(f"[Boudchart] ✓ Pas de changement: {new_status}")
        
        # 2. Vérifier Stade Toulousain
        logging.info("\n[2/2] Vérification Stade Toulousain...")
        stade_html = self.fetch_page(STADE_TOULOUSAIN_URL, "Stade Toulousain")
        
        if stade_html:
            found = self.check_stade_toulousain(stade_html)
            
            if found and not self.stade_toulousain_found:
                logging.info("[Stade Toulousain] 🔔 NOUVEAU: 'PETIT COP' trouvé!")
                self.send_notification("stade_toulousain", {})
                self.stade_toulousain_found = True
            elif found:
                logging.info("[Stade Toulousain] ✓ Déjà trouvé précédemment")
            else:
                logging.info("[Stade Toulousain] ✓ Toujours absent")
        
        # Sauvegarder l'état
        self.save_state()
        
        logging.info("="*60)
        logging.info(f"💤 Prochaine vérification dans {CHECK_INTERVAL} secondes")
        logging.info("="*60 + "\n")
    
    def run(self):
        """Lance le monitoring en continu"""
        logging.info("="*60)
        logging.info("🚀 DÉMARRAGE DU DUAL MONITORING")
        logging.info("="*60)
        logging.info(f"📍 Site 1: Boudchart - Casablanca")
        logging.info(f"📍 Site 2: Stade Toulousain - Petit Cop")
        logging.info(f"⏱️  Intervalle: {CHECK_INTERVAL} secondes")
        logging.info(f"🌍 Timezone: {os.getenv('TZ', 'UTC')}")
        logging.info("="*60 + "\n")
        
        while True:
            try:
                self.check_all()
            except Exception as e:
                logging.error(f"❌ Erreur globale: {e}")
            
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor = DualMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        logging.info("\n👋 Arrêt du monitoring")
    except Exception as e:
        logging.error(f"💥 Erreur fatale: {e}")
