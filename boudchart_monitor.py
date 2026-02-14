#!/usr/bin/env python3
"""
Script de monitoring pour Boudchart - Casablanca
Version corrigée avec parsing précis de la structure HTML
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

# Configuration depuis variables d'environnement ou valeurs par défaut
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes
URL = "https://www.boudchart.com/"
STATE_FILE = "boudchart_state.json"
LOG_FILE = "boudchart_monitor.log"

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class BoudchartMonitor:
    def __init__(self):
        self.state_file = Path(STATE_FILE)
        self.current_status = None
        self.load_state()
        
        # Configuration des notifications depuis variables d'environnement
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
        logging.info(f"  - Email: {'✅ Activé' if self.email_config['enabled'] else '❌ Désactivé'}")
        logging.info(f"  - Telegram: {'✅ Activé' if self.telegram_config['enabled'] else '❌ Désactivé'}")
        logging.info(f"  - Discord: {'✅ Activé' if self.discord_config['enabled'] else '❌ Désactivé'}")
    
    def load_state(self):
        """Charge l'état précédent depuis le fichier"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.current_status = data.get('casablanca_status')
                    logging.info(f"État chargé: Casablanca = {self.current_status}")
            except Exception as e:
                logging.error(f"Erreur lors du chargement de l'état: {e}")
                self.current_status = None
    
    def save_state(self, status):
        """Sauvegarde l'état actuel dans le fichier"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'casablanca_status': status,
                    'last_check': datetime.now().isoformat()
                }, f, indent=2)
            self.current_status = status
            logging.info(f"État sauvegardé: Casablanca = {status}")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de l'état: {e}")
    
    def fetch_page(self):
        """Récupère le contenu de la page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(URL, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de la page: {e}")
            return None
    
    def parse_casablanca_status(self, html_content):
        """
        Parse le HTML pour trouver le statut de Casablanca
        Méthode améliorée basée sur la structure réelle du site
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Le site liste les concerts avec cette structure:
            # <h3>Casablanca</h3>
            # Suivi de "Soon" ou d'un lien "Tickets"
            
            # Méthode 1: Trouver tous les h3 et chercher celui contenant "Casablanca"
            all_headings = soup.find_all(['h3', 'h2', 'h4'])
            
            for i, heading in enumerate(all_headings):
                heading_text = heading.get_text().strip()
                
                # Vérifier si c'est le heading Casablanca
                if 'casablanca' in heading_text.lower():
                    logging.info(f"✓ Trouvé le heading Casablanca: '{heading_text}'")
                    
                    # Chercher le statut dans les éléments suivants
                    # Le statut peut être un lien ou un texte
                    next_elements = heading.find_next_siblings(limit=5)
                    
                    for elem in next_elements:
                        elem_text = elem.get_text().strip().upper()
                        
                        # Chercher un lien avec "Tickets"
                        link = elem.find('a')
                        if link:
                            link_text = link.get_text().strip().upper()
                            if 'TICKET' in link_text:
                                logging.info(f"✓ Statut trouvé via lien: TICKETS")
                                return 'TICKETS'
                        
                        # Chercher le texte "Soon"
                        if 'SOON' in elem_text:
                            logging.info(f"✓ Statut trouvé via texte: SOON")
                            return 'SOON'
                        
                        # Chercher "Sold out"
                        if 'SOLD OUT' in elem_text or 'SOLD-OUT' in elem_text:
                            logging.info(f"✓ Statut trouvé: SOLD OUT")
                            return 'SOLD_OUT'
                    
                    # Chercher dans le parent du heading
                    parent = heading.parent
                    if parent:
                        parent_text = parent.get_text().upper()
                        
                        # Vérifier si on trouve "Soon" juste après Casablanca
                        if 'SOON' in parent_text:
                            # S'assurer que c'est bien pour Casablanca et pas un autre concert
                            text_after_casa = parent_text.split('CASABLANCA')[-1]
                            if 'SOON' in text_after_casa[:50]:  # Dans les 50 premiers caractères
                                logging.info(f"✓ Statut trouvé dans parent: SOON")
                                return 'SOON'
                        
                        if 'TICKET' in parent_text:
                            text_after_casa = parent_text.split('CASABLANCA')[-1]
                            if 'TICKET' in text_after_casa[:50]:
                                logging.info(f"✓ Statut trouvé dans parent: TICKETS")
                                return 'TICKETS'
            
            # Méthode 2: Recherche par regex dans tout le HTML
            # Chercher "Casablanca" suivi de "Soon" ou "Tickets"
            casa_pattern = re.search(r'casablanca.*?(soon|tickets?)', html_content, re.IGNORECASE | re.DOTALL)
            if casa_pattern:
                status = casa_pattern.group(1).upper()
                if 'TICKET' in status:
                    logging.info(f"✓ Statut trouvé via regex: TICKETS")
                    return 'TICKETS'
                elif 'SOON' in status:
                    logging.info(f"✓ Statut trouvé via regex: SOON")
                    return 'SOON'
            
            logging.warning("⚠️  Statut de Casablanca non trouvé dans la page")
            return None
            
        except Exception as e:
            logging.error(f"❌ Erreur lors du parsing: {e}")
            return None
    
    def send_notification(self, status):
        """Envoie une notification (plusieurs méthodes disponibles)"""
        message = f"""🎭 ALERTE BOUDCHART 🎭

Le statut du spectacle de Casablanca a changé !
Nouveau statut: {status}

Vérifiez le site: {URL}

---
Notification envoyée le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
"""
        
        logging.info(f"NOTIFICATION: Envoi des notifications pour le statut {status}")
        
        # Console (toujours actif)
        print("\n" + "="*60)
        print(message)
        print("="*60 + "\n")
        
        # Fichier de notification
        try:
            with open('NOTIFICATION.txt', 'w') as f:
                f.write(message)
        except Exception as e:
            logging.error(f"Erreur écriture NOTIFICATION.txt: {e}")
        
        # Email
        if self.email_config['enabled']:
            self.send_email_notification(status, message)
        
        # Telegram
        if self.telegram_config['enabled']:
            self.send_telegram_notification(status, message)
        
        # Discord
        if self.discord_config['enabled']:
            self.send_discord_notification(status, message)
    
    def send_email_notification(self, status, message):
        """Envoie une notification par email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = f"🎭 Boudchart Casablanca - Statut: {status}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
            
            logging.info("✅ Email de notification envoyé avec succès")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'envoi de l'email: {e}")
    
    def send_telegram_notification(self, status, message):
        """Envoie une notification via Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            
            # Message formaté pour Telegram
            telegram_message = f"🎭 <b>ALERTE BOUDCHART</b> 🎭\n\n"
            telegram_message += f"Le statut du spectacle de <b>Casablanca</b> a changé !\n"
            telegram_message += f"<b>Nouveau statut:</b> {status}\n\n"
            telegram_message += f"🔗 <a href='{URL}'>Vérifier le site</a>"
            
            response = requests.post(url, json={
                "chat_id": self.telegram_config['chat_id'],
                "text": telegram_message,
                "parse_mode": "HTML"
            }, timeout=10)
            
            response.raise_for_status()
            logging.info("✅ Notification Telegram envoyée avec succès")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'envoi Telegram: {e}")
    
    def send_discord_notification(self, status, message):
        """Envoie une notification via Discord"""
        try:
            response = requests.post(
                self.discord_config['webhook_url'],
                json={
                    "content": message,
                    "username": "Boudchart Monitor",
                    "avatar_url": "https://em-content.zobj.net/thumbs/160/apple/354/performing-arts_1f3ad.png"
                },
                timeout=10
            )
            
            response.raise_for_status()
            logging.info("✅ Notification Discord envoyée avec succès")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'envoi Discord: {e}")
    
    def check_status(self):
        """Vérifie le statut et envoie une notification si changement"""
        logging.info("🔍 Vérification du statut en cours...")
        
        html_content = self.fetch_page()
        if not html_content:
            logging.warning("⚠️  Impossible de récupérer la page, nouvelle tentative au prochain cycle")
            return
        
        new_status = self.parse_casablanca_status(html_content)
        
        if new_status is None:
            logging.warning("⚠️  Statut non détecté, nouvelle tentative au prochain cycle")
            return
        
        logging.info(f"📊 Statut détecté: {new_status}")
        
        # Vérifier si le statut a changé
        if self.current_status != new_status:
            logging.info(f"🔔 Changement de statut détecté: {self.current_status} -> {new_status}")
            
            # Notification si passage à TICKETS
            if new_status == 'TICKETS':
                self.send_notification(new_status)
            
            self.save_state(new_status)
        else:
            logging.info(f"✓ Pas de changement (toujours: {new_status})")
    
    def run(self):
        """Lance le monitoring en continu"""
        logging.info("="*60)
        logging.info("🎭 DÉMARRAGE DU MONITORING BOUDCHART")
        logging.info("="*60)
        logging.info(f"🌐 URL surveillée: {URL}")
        logging.info(f"⏱️  Intervalle de vérification: {CHECK_INTERVAL} secondes")
        logging.info(f"🌍 Timezone: {os.getenv('TZ', 'UTC')}")
        logging.info("="*60)
        
        while True:
            try:
                self.check_status()
            except Exception as e:
                logging.error(f"❌ Erreur lors de la vérification: {e}")
            
            logging.info(f"💤 Prochaine vérification dans {CHECK_INTERVAL} secondes")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor = BoudchartMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        logging.info("\n👋 Arrêt du monitoring (Ctrl+C)")
    except Exception as e:
        logging.error(f"💥 Erreur fatale: {e}")
