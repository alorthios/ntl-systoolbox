# NTL-SysToolbox v2.0.0

**Application de gestion système avancée** - Contient des outils pour:
- Monitoring de serveurs (statistiques CPU, RAM, Disk, Uptime)
- Gestion de bases de données MySQL (sauvegarde SQL, export CSV)
- Analyse End of Life (scan réseau, dates de support des OS)

## Installation

### Prérequis
- **Python 3.7+**
- **nmap** (pour le scan réseau)
  - Windows: Installer depuis https://nmap.org/download.html
  - Linux/Mac: `sudo apt-get install nmap` ou `brew install nmap`

### Étapes d'installation

1. **Créer l'environnement virtuel:**
```bash
python -m venv venv
```

2. **Activer l'environnement virtuel:**
   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

3. **Installer les dépendances:**
```bash
pip install -r requirements.txt
```

4. **Configurer les paramètres (optionnel):**
   - Éditer `config.py` pour ajouter les identifiants MySQL
   - Ou créer un fichier `.env`:
```
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
MYSQL_PORT=3306

# Linux Server (Ubuntu/Debian)
LINUX_SERVER_HOST=192.168.x.x
LINUX_SERVER_USER=username
LINUX_SERVER_PASSWORD=password
LINUX_SERVER_PORT=22

# Windows Server
WINDOWS_SERVER_HOST=192.168.x.x
WINDOWS_SERVER_USER=username
WINDOWS_SERVER_PASSWORD=password
WINDOWS_SERVER_PORT=22
```

## Utilisation

```bash
python -m src.main
```

L'application affiche un menu interactif avec 3 modules.

## Modules

### Module 1 - Statistiques Serveurs
Monitoring avancé des serveurs Windows et Linux distants via SSH :

**Option 1 - Vérifier état AD/DNS (A développer)**
- Structure placée pour vérification de l'Active Directory et DNS

**Option 2 - Vérifier état MySQL (A développer)**
- Structure placée pour vérification de la connectivité MySQL

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

### Module 2 - Requêtes MySQL
Gère une base de données MySQL:
- **Sauvegarde complète**: Génère un fichier SQL avec DROP/CREATE/INSERT
  - Format: `nombase_backup_YYYYMMDD_HHMMSS.sql`
  - Support du typage correct des données (nombres, chaînes, NULL)
- **Export de table**: Exporte une table sélectionnée au format CSV
  - Format: `nombase_nomtable_YYYYMMDD_HHMMSS.csv`
  - Délimiteur: `;` (point-virgule pour Excel français)
  - Encodage: UTF-8 avec BOM

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
│   ├── main.py                    # Point d'entrée et menu principal
│   ├── module1_server_stats.py    # Statistiques serveur
│   ├── module2_mysql.py           # Gestion MySQL
│   ├── module3_eol.py             # EOL et scan réseau
│   └── utils.py                   # Fonctions utilitaires partagées
├── config.py                      # Configuration centralisée
├── requirements.txt               # Dépendances Python
├── README.md                      # This file
└── .env                          # Variables d'environnement (optionnel)
```

## Technologies utilisées

- **paramiko**: Client SSH pour monitoring distants (Windows/Linux)
- **tkinter**: Dialogues de sélection de fichiers/dossiers (fallback texte)
- **pymysql**: Connexion et gestion MySQL
- **python-nmap**: Scan réseau avec détection OS
- **requests**: Appels API endoflife.date
- **python-dotenv**: Gestion des variables d'environnement

## Dépendances

```txt
pymysql==1.1.0
python-dotenv==1.0.0
python-nmap==0.0.1
requests==2.31.0
paramiko>=2.12.0
```

## Exemple d'utilisation

### Sauvegarde MySQL
```
Menu Principal > Module 2 > Option 1
→ Sélectionne le dossier de destination
→ Génère: wms_backup_20260219_233514.sql (9KB)
```

### Export d'une table CSV
```
Menu Principal > Module 2 > Option 2
→ Sélectionne une table dans la liste
→ Sélectionne le dossier de destination
→ Génère: wms_stocks_20260219_233520.csv
```

### Scan réseau
```
Menu Principal > Module 3 > Option 1
→ Saisit plage réseau: 192.168.10.0/24
→ Affiche résultats avec 3 hosts détectés
```

## Historique des versions

### v2.0.1 (22 février 2026)
✅ Standardisation étendue :
- Docstrings unififiées avec format `Args:/Retourne:` systématique
- Tous les fichiers 100% en français (main.py, docstrings, commentaires)
- Sections séparatrice cohérentes dans tous les modules
- Suppression des sections vides / commentaires inutiles
✅ Infrastructure SSH :
- Refactorisation complète des fonctions SSH dans utils.py
- Crédentiels centralisés dans .env
- Support complet Windows Server 2022 + Ubuntu 20.04+

### v2.0.0
✅ Nettoyage du code: Suppression des imports inutilisés et du code mort
✅ Cohérence: Tous les modules suivent la même structure et style
✅ Documentation: Commentaires améliorés pour compréhension étudiante
✅ Widgets: Tous les dialogues utilisent tkinter avec fallback texte
✅ Formatage: Tables alignées et affichées correctement

## Notes

- **Dialogues**: Si la boîte de dialogue graphique échoue, l'application propose une saisie manuelle
- **Encodage**: Tous les fichiers utilisent UTF-8 pour prendre en charge les caractères spéciaux
- **Cross-platform**: Compatible Windows, Linux, macOS
