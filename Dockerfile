FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY requirements.txt .
COPY boudchart_monitor.py .
COPY web_server.py .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Créer un utilisateur non-root
RUN useradd -m -u 1000 monitor && chown -R monitor:monitor /app
USER monitor

# Exposer le port pour le web service
EXPOSE 10000

# Lancer le serveur web (qui lancera aussi le monitoring)
CMD ["python3", "web_server.py"]
```

5. **Commit changes** → "Update Dockerfile to use web server"

---

### **ÉTAPE 3: Vérifier requirements.txt** (1 minute)

1. **Sur GitHub, cliquez sur** `requirements.txt`

2. **Vérifiez qu'il contient Flask:**
```
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
flask==3.0.0
```

3. **Si Flask n'est pas là**, éditez le fichier et ajoutez `flask==3.0.0`

4. **Commit changes** si modifié

---

### **ÉTAPE 4: Attendre le redéploiement** (2-3 minutes)

1. **Allez sur Render.com** → Votre service

2. Render va détecter les changements GitHub et redéployer automatiquement

3. Attendez que le statut passe à **"Live"** 🟢

---

### **ÉTAPE 5: Vérifier que tout fonctionne** (1 minute)

#### A. Tester le serveur web:

1. Sur Render, vous avez une **URL** (ex: `https://boudchart-monitor.onrender.com`)

2. **Cliquez sur cette URL** → Vous devriez voir:
```
🎭 Boudchart Monitor
✅ Service actif

Le monitoring du site Boudchart est en cours d'exécution.
Surveillance: Spectacle de Casablanca
Vérification toutes les 5 minutes
