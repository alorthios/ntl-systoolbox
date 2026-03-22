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
# NTL-SysToolbox v3.1.0

**Application CLI de gestion système avancée** pour l'administration de serveurs Windows et Linux.

## 📋 Table des matières
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Modules](#modules)
- [Technologies](#technologies-utilisées)
- [Structure du projet](#structure-du-projet)
- [Exemples](#exemples-dutilisation)
- [Historique des versions](#historique-des-versions)
- [Licence](#licence)

## Fonctionnalités

### 🖥️ Module 1 - Monitoring Serveurs
- Vérification des services AD/DNS et MySQL
- Statistiques en temps réel (CPU, RAM, Disk, Uptime)
- Support Windows Server 2022+ et Linux/Ubuntu via SSH

### 🗄️ Module 2 - Gestion MySQL
- Sauvegarde complète de bases de données (mysqldump via SSH)
- Export de tables au format CSV
- Sélection interactive des bases de données et tables

### 🔍 Module 3 - End of Life / Scan Réseau
- Scan réseau avec détection d'OS (nmap)
- Consultation des dates de fin de support (API endoflife.date)
- Enrichissement de fichiers CSV avec informations EOL

## Prérequis Généraux

### Connectivité
- **Accès SSH** configuré sur les serveurs Windows et Linux distants
- **MySQL/MariaDB** installé et accessible sur le serveur Linux
- **Active Directory** et **DNS** configurés sur Windows Server

## Installation

Choisissez la méthode qui vous convient le mieux :

### Option 1️⃣ - Installation Classique (Native Python)

**Prérequis spécifiques:**
- Python 3.7+
- nmap installé sur votre système
  - Windows: [Télécharger depuis nmap.org](https://nmap.org/download.html)
  - Linux: `sudo apt-get install nmap`
  - macOS: `brew install nmap`

**Étapes:**

1. **Cloner le dépôt:**
```bash
git clone https://github.com/alorthios/ntl-systoolbox.git
cd ntl-systoolbox
```

2. **Créer et activer l'environnement virtuel:**
```bash
python -m venv venv
```
   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

3. **Installer les dépendances:**
```bash
pip install -r requirements.txt
```

4. **Créer le fichier de configuration (voir section Configuration ci-dessous)**

5. **Lancer l'application:**
```bash
python -m src.main
```

---

### Option 2️⃣ - Installation Docker

**Prérequis spécifiques:**
- Docker installé
- Docker Compose installé

**Étapes:**

1. **Créer le fichier de configuration (voir section Configuration ci-dessous)**

2. **Créer le fichier `docker-compose.yml` avec le contenu suivant :**
```yaml
services:
  ntl-systoolbox:
    build:
      context: .
      dockerfile: Dockerfile
    image: ntl-systoolbox:3.1.0
    container_name: ntl-systoolbox

    # Mode réseau
    network_mode: bridge

    # Volumes
    volumes:
      # Bind mount pour le fichier .env (depuis l'hôte)
      - ./.env:/app/.env
      # Volume nommé pour les exports
      - exports-volume:/app/exports

# Définir le volume nommé
volumes:
  exports-volume:
    driver: local
```

3. **Lancer l'application:**
```bash
docker compose run --rm ntl-systoolbox
```

Les exports (fichiers CSV) seront stockés dans le volume Docker `exports-volume`.

---

## Configuration

Les deux méthodes d'installation utilisent un fichier `.env` pour stocker les identifiants.

**Créer le fichier `.env` avec vos paramètres, exemple:**
```env
# Configuration serveur Linux
LINUX_SERVER_HOST=192.168.100.21
LINUX_SERVER_USER=votre_utilisateur
LINUX_SERVER_PASSWORD=votre_mot_de_passe
LINUX_SERVER_PORT=22

# Configuration serveur Windows 
WINDOWS_SERVER_HOST=192.168.100.10
WINDOWS_SERVER_USER=Administrateur
WINDOWS_SERVER_PASSWORD=votre_mot_de_passe
WINDOWS_SERVER_PORT=22

# Configuration MySQL
MYSQL_HOST=192.168.100.21
MYSQL_USER=votre_utilisateur
MYSQL_PASSWORD=votre_mot_de_passe
MYSQL_PORT=3306
```

**Note:** Si le fichier `.env` n'est pas configuré, l'application demandera les informations de connexion de manière interactive.

## Utilisation

L'application affiche un menu interactif permettant d'accéder aux 3 modules disponibles.

## Modules

### Module 1 - Statistiques Serveurs
Monitoring avancé des serveurs Windows et Linux distants via SSH :

**Option 1 - Vérifier état AD/DNS**
- Vérification des services Active Directory (NTDS) et DNS sur serveur Windows
- Détection via Get-Service

**Option 2 - Vérifier état MySQL**
- Vérification du service MySQL sur serveur Linux
- Détection via systemctl is-active

**Option 3 - Windows Server Distant**
- Connexion SSH au serveur Windows Server 2022+
- Affiche statistiques en temps réel :
  - **Uptime**: Durée depuis dernier démarrage (jours/heures/minutes)
  - **CPU**: Utilisation processeur (%) et nombre de cœurs logiques
  - **RAM**: Utilisation mémoire (%) avec total/utilisée/disponible en GB
  - **DISQUES**: Liste de tous les disques logiques avec utilisation

**Option 4 - Ubuntu/Linux Server Distant**
- Connexion SSH au serveur Ubuntu/Linux via SSH
- Affiche statistiques en temps réel :
  - **Uptime**: Durée depuis dernier démarrage
  - **CPU**: Utilisation processeur (%) et nombre de cœurs logiques
  - **RAM**: Utilisation mémoire avec métriques détaillées
  - **PARTITIONS**: Liste de tous les points de montage et utilisation

### Module 2 - Gestion MySQL
Gestion de bases de données MySQL distantes via SSH + mysqldump/mysql client :

**Option 1 - Sauvegarde complète:**
- Connexion SSH au serveur Linux hébergeant MySQL
- Sélection interactive de la base de données
- Export via mysqldump avec options complètes (--single-transaction, --routines, --triggers, --events)
- Transfert SFTP du fichier .sql vers le poste local
- Format: `nombase_backup_YYYYMMDD_HHMMSS.sql`

**Option 2 - Export de table CSV:**
- Connexion SSH et sélection de base de données
- Liste des tables disponibles
- Export via mysql client avec conversion en CSV (séparateur `;`)
- Transfert SFTP vers le poste local
- Format: `nombase_nomtable_YYYYMMDD_HHMMSS.csv`
- Encodage: UTF-8 avec BOM pour compatibilité Excel

### Module 3 - End of Life / Scan Réseau
Détecte les systèmes et fournit les dates de fin de support:

**Option 1 - Scanner réseau:**
- Scan une plage réseau en format CIDR (ex: 192.168.1.0/24)
- Utilise nmap pour détecter hosts et OS
- Stratégie multi-niveaux: OS fingerprinting → Détection de services → Ports
- Affiche IP, Hostname, OS détecté

**Option 2 - Lister versions d'un OS:**
- Récupère la liste complète des versions via API endoflife.date
- Affiche pour chaque version:
  - Numéro de version
  - Date de fin de support (EOL)
  - Statut LTS (Long-Term Support)
  - Statut actuel (Support actif / EOL dans X jours / Fin de vie depuis X jours)

**Option 3 - Import CSV et EOL Check:**
- Importe un CSV contenant: nom;os;version
- Affiche le contenu du CSV importé
- Enrichit chaque ligne avec les infos EOL via API
- Exporte un CSV enrichi: nom;os;version;date_eol;etat

## Structure du Projet

```
ntl-systoolbox/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Point d'entrée et menu principal
│   ├── module1_server_stats.py    # Monitoring serveurs (SSH)
│   ├── module2_mysql.py           # Gestion MySQL (SSH + mysqldump)
│   ├── module3_eol.py             # Scan réseau et API EOL
│   └── utils.py                   # Fonctions SSH et utilitaires partagées
├── .env.example                   # Template de configuration
├── .env                           # Configuration (à créer, non versionné)
├── .gitignore                     # Fichiers exclus du versioning
├── requirements.txt               # Dépendances Python
└── README.md                      # Documentation
```

## Technologies utilisées

| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| **python-dotenv** | 1.0.0 | Gestion des variables d'environnement (.env) |
| **python-nmap** | 0.7.1 | Scan réseau et détection d'hôtes/OS |
| **requests** | 2.31.0 | Requêtes HTTP vers l'API endoflife.date |
| **paramiko** | ≥2.12.0 | Client SSH pour connexions distantes et opérations MySQL |

**Modules Python standard utilisés:**
- `tkinter` : Dialogues de sélection de fichiers/dossiers (avec fallback texte)
- `csv`, `os`, `datetime`, `re` : Traitement de données et système

