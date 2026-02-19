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
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
MYSQL_PORT=3306
```

## Utilisation

```bash
python -m src.main
```

L'application affiche un menu interactif avec 3 modules.

## Modules

### Module 1 - Statistiques Serveurs
Affiche les statistiques système en temps réel:
- **CPU Usage**: Utilisation du processeur (%)
- **RAM Usage**: Mémoire disponible vs utilisée (GB)
- **Disk Usage**: Espace disque par volume
- **System Uptime**: Durée de fonctionnement depuis le dernier démarrage

*État: Placeholder en développement - structure disponible pour implémentation*

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

- **tkinter**: Dialogues de sélection de fichiers/dossiers
- **pymysql**: Connexion et gestion MySQL
- **python-nmap**: Scan réseau avec détection OS
- **requests**: Appels API endoflife.date
- **python-dotenv**: Gestion des variables d'environnement

## Dépendances

```
pymysql==1.1.0
python-dotenv==1.0.0
python-nmap==0.0.1
requests==2.31.0
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

## Améliorations v2.0.0

✅ Nettoyage du code: Suppression des imports inutilisés et du code mort
✅ Cohérence: Tous les modules suivent la même structure et style
✅ Documentation: Commentaires améliorés pour compréhension étudiante
✅ Widgets: Tous les dialogues utilisent tkinter avec fallback texte
✅ Formatage: Tables alignées et affichées correctement

## Notes

- **Dialogues**: Si la boîte de dialogue graphique échoue, l'application propose une saisie manuelle
- **Encodage**: Tous les fichiers utilisent UTF-8 pour prendre en charge les caractères spéciaux
- **Cross-platform**: Compatible Windows, Linux, macOS
