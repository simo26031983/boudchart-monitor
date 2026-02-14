#!/usr/bin/env python3
"""Script de test pour envoyer une notification Telegram"""

import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

def test_telegram():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Variables Telegram non configurées!")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    message = """🎭 <b>TEST - ALERTE BOUDCHART</b> 🎭

Ceci est un message de TEST !

Le statut du spectacle de <b>Casablanca</b> a changé !
<b>Nouveau statut:</b> TICKETS

🔗 <a href='https://www.boudchart.com/'>Vérifier le site</a>

---
✅ Si vous recevez ce message, les notifications fonctionnent parfaitement !"""
    
    try:
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        
        response.raise_for_status()
        print("✅ Message de test envoyé avec succès!")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_telegram()
