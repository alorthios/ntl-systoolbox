# NTL-SysToolbox v3.1.0

Application CLI de gestion système pour l’administration de serveurs Windows/Linux, la gestion MySQL distante et l’analyse End-of-Life (EOL).

## Table des matières
- [1. Fonctionnalités](#1-fonctionnalités)
- [2. Prérequis](#2-prérequis)
- [3. Installation classique (Git + Python)](#3-installation-classique-git--python)
- [4. Installation via Docker Hub](#4-installation-via-docker-hub)
- [5. Configuration](#5-configuration)
- [6. Utilisation](#6-utilisation)
- [7. Structure du projet](#7-structure-du-projet)

---

## 1. Fonctionnalités

### Module 1 - Monitoring serveurs
- Vérification des services AD/DNS (Windows)
- Vérification du service MySQL (Linux)
- Statistiques ressources distantes via SSH: uptime, CPU, RAM, disques

### Module 2 - Gestion MySQL
- Sauvegarde SQL complète via `mysqldump` (exécution distante SSH)
- Export de tables en CSV (`;`) via client `mysql`
- Transfert des fichiers via SFTP (Paramiko)

### Module 3 - EOL / Scan réseau
- Scan réseau CIDR avec `nmap`
- Détection OS/ports/hostnames
- Enrichissement CSV avec les données de https://endoflife.date/

---

## 2. Prérequis

### 2.1 Prérequis techniques communs
- Accès SSH fonctionnel vers les serveurs Linux et Windows
- Serveur Linux cible avec MySQL/MariaDB et outils `mysql`/`mysqldump`
- Accès réseau entre le poste d’exécution et les serveurs cibles

### 2.2 Prérequis installation classique
- `git`
- `python` (3.10+ recommandé)
- `pip`
- `venv`
- `nmap`
- `tkinter` (optionnel mais recommandé pour dialogues fichiers)

### 2.3 Prérequis installation Docker
- Docker
- Docker Compose (`docker compose`)

---

## 3. Installation classique (Git + Python)

### 3.1 Cloner le dépôt
```bash
git clone https://github.com/alorthios/ntl-systoolbox.git
cd ntl-systoolbox
```

### 3.2 Créer et activer l’environnement virtuel
```bash
python -m venv venv
```

- Linux/macOS:
```bash
source venv/bin/activate
```

- Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```

- Windows (CMD):
```cmd
venv\Scripts\activate
```

### 3.3 Installer les dépendances
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.4 Préparer la configuration
- Créer `.env` à partir de `.env.example`
- Renseigner les variables (voir section 5)

### 3.5 Lancer l’application
```bash
python -m src.main
```

---

## 4. Installation via Docker Hub

Cette méthode est recommandée pour les techniciens: environnement packagé, moins de prérequis locaux.

### 4.1 Préparer le dossier de travail
```bash
mkdir -p ntl-systoolbox
cd ntl-systoolbox
mkdir -p exports
```

### 4.2 Créer le fichier `.env`
Créer un fichier `.env` en reprenant le contenu de `.env.example`:

```dotenv
# MySQL Configuration
MYSQL_HOST=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_PORT=3306

# Linux Server
LINUX_SERVER_HOST=
LINUX_SERVER_USER=
LINUX_SERVER_PASSWORD=
LINUX_SERVER_PORT=22

# Windows Server
WINDOWS_SERVER_HOST=
WINDOWS_SERVER_USER=
WINDOWS_SERVER_PASSWORD=
WINDOWS_SERVER_PORT=22
```

### 4.3 Créer `docker-compose.yml`
```yaml
services:
  ntl-systoolbox:
    image: alorthios/ntl-systoolbox:3.1.0
    container_name: ntl-systoolbox

    # Accès réseau direct pour les scans nmap
    network_mode: host

    # Capacités réseau nécessaires à nmap
    cap_add:
      - NET_RAW
      - NET_ADMIN

    volumes:
      - ./.env:/app/.env
      - ./exports:/app/exports
```

### 4.4 Récupérer l’image
```bash
docker pull alorthios/ntl-systoolbox:3.1.0
```

### 4.5 Lancer l’application
```bash
docker compose run --rm ntl-systoolbox
```

Les fichiers exportés seront disponibles dans le dossier local `exports/`.

---

## 5. Configuration

Les connexions se font via variables d’environnement du fichier `.env`.

Variables supportées:
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_PORT`
- `LINUX_SERVER_HOST`, `LINUX_SERVER_USER`, `LINUX_SERVER_PASSWORD`, `LINUX_SERVER_PORT`
- `WINDOWS_SERVER_HOST`, `WINDOWS_SERVER_USER`, `WINDOWS_SERVER_PASSWORD`, `WINDOWS_SERVER_PORT`

> Si `.env` est incomplet, l’application demande les informations de connexion en mode interactif.

---

## 6. Utilisation

Lancer l’application puis choisir un module dans le menu principal:

1. **Module 1**: état AD/DNS, état MySQL, ressources serveurs Windows/Linux
2. **Module 2**: backup SQL et export CSV de tables MySQL
3. **Module 3**: scan réseau CIDR, consultation EOL, enrichissement CSV

### Format CSV attendu (module 3)
Entrée:
```text
nom;os;version
```

Sortie:
```text
nom;os;version;date_eol;etat
```

---

---

## 7. Structure du projet

```text
ntl-systoolbox/
├── .dockerignore              # Exclusions du contexte Docker
├── .gitignore                 # Exclusions du contexte Git
├── .env.example               # Modèle de variables d'environnement
├── docker-compose.yml         # Lancement conteneurisé (Docker Compose)
├── Dockerfile                 # Construction de l'image applicative (Build Docker)
├── README.md                  # Documentation
├── requirements.txt           # Dépendances Python
├── exports/                   # Dossier local des fichiers exportés (Environnement Docker)
└── src/
  ├── main.py                  # Point d'entrée et menu principal
  ├── module1_server_stats.py  # Monitoring serveurs (SSH)
  ├── module2_mysql.py         # Sauvegarde/export MySQL (SSH/SFTP)
  ├── module3_eol.py           # Scan réseau et enrichissement EOL (nmap, api EOL)
  └── utils.py                 # Fonctions partagées
```

