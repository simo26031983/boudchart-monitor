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
