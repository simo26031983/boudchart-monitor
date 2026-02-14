# 🆓 Déploiement GRATUIT du Monitoring Boudchart

Guide complet pour déployer le script de monitoring sur des serveurs gratuits en ligne.

## 🏆 Meilleures Options Gratuites

### Option 1: Render.com (⭐ RECOMMANDÉ)
**Avantages:** Facile, fiable, toujours actif, 750h/mois gratuites
**Inconvénient:** Peut se mettre en veille après 15min d'inactivité

### Option 2: Railway.app
**Avantages:** Très simple, $5 de crédit gratuit/mois, bon pour débuter
**Inconvénient:** Limité à 500h/mois

### Option 3: Fly.io
**Avantages:** Toujours actif, 3 machines gratuites
**Inconvénient:** Configuration un peu plus technique

### Option 4: PythonAnywhere
**Avantages:** Spécialisé Python, interface web simple
**Inconvénient:** Limitations sur les requêtes externes (compte gratuit)

### Option 5: Google Cloud Run (Avancé)
**Avantages:** Généreux, bon niveau gratuit
**Inconvénient:** Plus complexe à configurer

---

## 🚀 DÉPLOIEMENT RENDER.COM (Le plus simple!)

### Étape 1: Préparation du code

Vous avez déjà tous les fichiers nécessaires! Il faut juste créer un compte.

### Étape 2: Créer un compte Render

1. Allez sur **https://render.com**
2. Cliquez sur "Get Started"
3. Inscrivez-vous avec GitHub, GitLab ou email

### Étape 3: Créer un dépôt GitHub (gratuit)

1. Allez sur **https://github.com**
2. Créez un compte si nécessaire
3. Cliquez sur "New repository"
   - Nom: `boudchart-monitor`
   - Visibilité: Public (pour Render gratuit)
4. Uploadez tous les fichiers du projet:
   - boudchart_monitor.py
   - requirements.txt
   - Dockerfile
   - render.yaml (je vais le créer ci-dessous)

### Étape 4: Déployer sur Render

1. Connectez-vous sur Render.com
2. Cliquez "New +" → "Background Worker"
3. Connectez votre dépôt GitHub
4. Configuration:
   - **Name:** boudchart-monitor
   - **Environment:** Docker
   - **Instance Type:** Free
5. Cliquez "Create Background Worker"

**C'est tout!** Le script tournera 24/7 gratuitement.

### Étape 5: Voir les logs

Sur Render, onglet "Logs" → Vous verrez les vérifications en temps réel.

---

## 🛤️ DÉPLOIEMENT RAILWAY.APP (Alternative facile)

### Étape 1: Créer un compte

1. Allez sur **https://railway.app**
2. Inscrivez-vous avec GitHub
3. Vous avez $5 de crédit gratuit/mois (≈500h)

### Étape 2: Déployer

1. Cliquez "New Project"
2. Sélectionnez "Deploy from GitHub repo"
3. Choisissez votre dépôt `boudchart-monitor`
4. Railway détecte automatiquement le Dockerfile
5. Cliquez "Deploy"

**Configuration automatique!**

### Étape 3: Voir les logs

Onglet "Deployments" → Cliquez sur le déploiement → "View Logs"

---

## ✈️ DÉPLOIEMENT FLY.IO (Toujours actif)

### Étape 1: Installation

```bash
# Sur Mac
brew install flyctl

# Sur Linux
curl -L https://fly.io/install.sh | sh

# Sur Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

### Étape 2: Connexion

```bash
flyctl auth signup  # Créer un compte
# OU
flyctl auth login   # Se connecter
```

### Étape 3: Déployer

```bash
# Dans le dossier du projet
flyctl launch

# Questions:
# - App name: boudchart-monitor
# - Region: cdg (Paris) - le plus proche de Casablanca
# - PostgreSQL: No
# - Redis: No

# Déployer
flyctl deploy
```

### Étape 4: Voir les logs

```bash
flyctl logs
```

---

## 🐍 DÉPLOIEMENT PYTHONANYWHERE (Simple mais limité)

### Étape 1: Créer un compte

1. Allez sur **https://www.pythonanywhere.com**
2. Cliquez "Pricing & signup"
3. Choisissez "Create a Beginner account" (gratuit)

### Étape 2: Upload des fichiers

1. Onglet "Files"
2. Créez un dossier: `boudchart-monitor`
3. Uploadez tous les fichiers Python

### Étape 3: Installer les dépendances

1. Onglet "Consoles"
2. Cliquez "Bash"
3. Exécutez:
```bash
cd boudchart-monitor
pip3 install --user -r requirements.txt
```

### Étape 4: Créer une tâche programmée

1. Onglet "Tasks"
2. Créez une tâche qui s'exécute toutes les heures:
```
/home/votre_username/boudchart-monitor/boudchart_monitor.py
```

⚠️ **Limitation:** Seulement 1 tâche/heure sur le plan gratuit

### Alternative: Always-on console

Sur le plan gratuit, vous ne pouvez pas avoir de scripts "always-on", mais vous pouvez:
- Utiliser une tâche programmée (toutes les heures)
- Ou upgrader à $5/mois pour always-on

---

## ☁️ DÉPLOIEMENT GOOGLE CLOUD RUN (Avancé)

### Prérequis

- Compte Google Cloud (300$ gratuits pour commencer)
- gcloud CLI installé

### Étape 1: Configuration

```bash
# Installer gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Se connecter
gcloud auth login

# Créer un projet
gcloud projects create boudchart-monitor --name="Boudchart Monitor"
gcloud config set project boudchart-monitor

# Activer Cloud Run API
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Étape 2: Déployer

```bash
# Dans le dossier du projet
gcloud run deploy boudchart-monitor \
  --source . \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --no-cpu-throttling
```

⚠️ **Note:** Cloud Run facture par utilisation, mais le niveau gratuit est généreux (2 millions de requêtes/mois)

---

## 📧 CONFIGURER LES NOTIFICATIONS EMAIL

### Pour Gmail (après déploiement)

1. **Activer la validation en 2 étapes:**
   - https://myaccount.google.com/security
   - Activez la "Validation en deux étapes"

2. **Générer un mot de passe d'application:**
   - https://myaccount.google.com/apppasswords
   - Application: "Mail"
   - Appareil: "Autre" → "Boudchart Monitor"
   - Copiez le mot de passe généré (16 caractères)

3. **Configurer dans le script:**
   
   Sur Render/Railway, ajoutez des variables d'environnement:
   - `EMAIL_ENABLED` = `true`
   - `SENDER_EMAIL` = `votre_email@gmail.com`
   - `SENDER_PASSWORD` = `mot_de_passe_application`
   - `RECIPIENT_EMAIL` = `votre_email@gmail.com`

4. **Modifiez le script pour lire ces variables:**

```python
import os

EMAIL_CONFIG = {
    'enabled': os.getenv('EMAIL_ENABLED', 'false').lower() == 'true',
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': os.getenv('SENDER_EMAIL', ''),
    'sender_password': os.getenv('SENDER_PASSWORD', ''),
    'recipient_email': os.getenv('RECIPIENT_EMAIL', '')
}
```

---

## 📱 ALTERNATIVES: Notifications Push gratuites

### Option 1: Telegram Bot (RECOMMANDÉ)

**Avantages:** Gratuit, instantané, notifications push mobiles

```python
import requests

def send_telegram(message):
    bot_token = "VOTRE_BOT_TOKEN"
    chat_id = "VOTRE_CHAT_ID"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    requests.post(url, json={
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    })
```

**Configuration:**
1. Parlez à @BotFather sur Telegram
2. Créez un bot: `/newbot`
3. Copiez le token
4. Trouvez votre chat_id: parlez à @userinfobot

### Option 2: Discord Webhook

```python
import requests

def send_discord(message):
    webhook_url = "VOTRE_WEBHOOK_URL"
    
    requests.post(webhook_url, json={
        "content": message,
        "username": "Boudchart Monitor"
    })
```

**Configuration:**
1. Dans un serveur Discord → Paramètres du salon
2. Intégrations → Webhooks → Nouveau Webhook
3. Copiez l'URL

### Option 3: Pushover

```python
import requests

def send_pushover(message):
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": "VOTRE_APP_TOKEN",
        "user": "VOTRE_USER_KEY",
        "message": message
    })
```

**Configuration:**
1. Créez un compte sur pushover.net
2. Créez une application
3. Notez le token et user key

---

## 🎯 RECOMMANDATION FINALE

### Pour le plus simple et gratuit:

**1. Render.com (Option #1)**
   - Le plus facile à configurer
   - Interface web claire
   - Gratuit et fiable

**2. Telegram Bot pour les notifications**
   - Gratuit à vie
   - Notifications instantanées sur mobile
   - Pas de configuration email compliquée

### Tutoriel complet en 5 minutes:

1. ✅ Créez un compte GitHub
2. ✅ Uploadez les fichiers du projet
3. ✅ Créez un compte Render.com
4. ✅ Déployez depuis GitHub
5. ✅ (Optionnel) Configurez Telegram Bot

**C'est parti! Vous aurez votre monitoring 24/7 gratuit en moins de 10 minutes!**

---

## 🆘 Besoin d'aide?

Si vous avez des questions sur le déploiement, n'hésitez pas à demander!

**Bon spectacle! 🎭**
