# Dockerfile pour NTL-SysToolbox avec nmap
FROM python:3.14-slim

# Installer nmap, tkinter et dépendances système
# Alleger la taille de l'image en nettoyant le cache apt après l'installation
RUN apt-get update \
    && apt-get install -y nmap python3-tk tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

# Créer le répertoire d'exports
RUN mkdir -p /app/exports

CMD ["python", "-m", "src.main"]
