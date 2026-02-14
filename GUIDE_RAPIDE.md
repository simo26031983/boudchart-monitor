# 🚀 DÉPLOIEMENT EN 5 MINUTES - RENDER.COM

Guide ultra-rapide pour avoir votre monitoring opérationnel gratuitement.

---

## ✅ ÉTAPE 1: Créer un compte GitHub (2 minutes)

1. Allez sur **https://github.com**
2. Cliquez "Sign up" (Inscription)
3. Remplissez: email, mot de passe, nom d'utilisateur
4. Vérifiez votre email
5. ✅ Compte créé!

---

## ✅ ÉTAPE 2: Créer le dépôt (2 minutes)

1. Cliquez sur le **+** en haut à droite → "New repository"
2. Remplissez:
   - **Repository name:** `boudchart-monitor`
   - **Public** (cochez)
   - ✅ "Add a README file" (cochez)
3. Cliquez "Create repository"

### Uploader les fichiers:

1. Sur la page de votre dépôt, cliquez "Add file" → "Upload files"
2. Glissez-déposez TOUS les fichiers:
   - ✅ `boudchart_monitor_v2.py` (renommez en `boudchart_monitor.py`)
   - ✅ `requirements.txt`
   - ✅ `Dockerfile`
   - ✅ `render.yaml`
3. Cliquez "Commit changes"

**Votre code est maintenant sur GitHub!** 🎉

---

## ✅ ÉTAPE 3: Déployer sur Render (1 minute)

1. Allez sur **https://render.com**
2. Cliquez "Get Started" → "Sign up with GitHub"
3. Autorisez Render à accéder à votre GitHub
4. Sur le tableau de bord Render:
   - Cliquez "New +" (en haut à droite)
   - Sélectionnez "Background Worker"
5. Connectez votre dépôt:
   - Cherchez `boudchart-monitor`
   - Cliquez "Connect"
6. Configuration (laissez tout par défaut):
   - Name: `boudchart-monitor` ✅
   - Environment: `Docker` ✅
   - Instance Type: `Free` ✅
7. Cliquez "Create Background Worker"

**C'EST TOUT!** 🎊

---

## ✅ VÉRIFIER QUE ÇA MARCHE

1. Sur Render, attendez que le déploiement se termine (1-2 minutes)
2. Le statut passera à "Live" 🟢
3. Cliquez sur l'onglet "Logs"
4. Vous devriez voir:
```
🎭 DÉMARRAGE DU MONITORING BOUDCHART
🌐 URL surveillée: https://www.boudchart.com/
⏱️  Intervalle de vérification: 300 secondes
🔍 Vérification du statut en cours...
📊 Statut détecté: SOON
✓ Pas de changement
💤 Prochaine vérification dans 300 secondes
```

**✅ Votre monitoring tourne 24/7 gratuitement!**

---

## 📱 BONUS: Recevoir les notifications sur Telegram (5 minutes)

Les notifications console sur Render c'est bien, mais Telegram c'est mieux!

### Créer un bot Telegram:

1. Ouvrez Telegram
2. Cherchez `@BotFather`
3. Envoyez: `/newbot`
4. Donnez un nom: `Boudchart Monitor`
5. Donnez un username: `boudchart_monitor_bot` (ou autre)
6. **Copiez le TOKEN** (exemple: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Obtenir votre Chat ID:

1. Envoyez un message à votre nouveau bot
2. Cherchez `@userinfobot` sur Telegram
3. Envoyez-lui `/start`
4. **Copiez votre ID** (exemple: `987654321`)

### Configurer sur Render:

1. Sur Render, page de votre worker
2. Onglet "Environment"
3. Cliquez "Add Environment Variable"
4. Ajoutez:

```
TELEGRAM_ENABLED = true
TELEGRAM_BOT_TOKEN = 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID = 987654321
```

5. Cliquez "Save Changes"
6. Le service redémarrera automatiquement

**✅ Vous recevrez maintenant les notifications sur Telegram!** 📱

---

## 🎯 RÉCAPITULATIF

Vous avez maintenant:
- ✅ Un script qui tourne 24/7 gratuitement
- ✅ Vérifie le site toutes les 5 minutes
- ✅ Vous alerte dès que "TICKETS" apparaît
- ✅ (Optionnel) Notifications Telegram instantanées

**Temps total: 5-10 minutes**
**Coût: 0€**

---

## 💡 ASTUCES

### Voir les logs en temps réel:
- Sur Render → Onglet "Logs"
- Les logs se rafraîchissent automatiquement

### Redémarrer le service:
- Sur Render → "Manual Deploy" → "Clear build cache & deploy"

### Arrêter temporairement:
- Sur Render → "Suspend Service"
- Pour relancer: "Resume Service"

### Supprimer complètement:
- Sur Render → Settings → "Delete Service"

---

## 🆘 PROBLÈMES?

**Le déploiement échoue:**
- Vérifiez que tous les fichiers sont bien uploadés sur GitHub
- Vérifiez que `Dockerfile` est bien présent

**Les logs ne montrent rien:**
- Attendez 1-2 minutes après le déploiement
- Cliquez sur "Refresh logs"

**Pas de notifications:**
- Vérifiez les logs pour voir si le statut est détecté
- Vérifiez que le token et chat_id Telegram sont corrects

---

## 🎭 BON SPECTACLE!

Votre monitoring est opérationnel. Vous serez prévenu dès que les billets pour Casablanca sont disponibles!

**N'oubliez pas de vérifier les logs de temps en temps pour être sûr que tout fonctionne bien.**
