"""
NTL-SysToolbox - Module 2: MySQL Database Management
Gère la sauvegarde et l'export de données depuis MySQL
"""
import pymysql
from pymysql import Error
import csv
import os
from datetime import datetime
from pathlib import Path
import sys

# Ajouter le répertoire parent (racine du projet) au path pour importer config
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from config import MYSQL_CONFIG
from .utils import get_destination_path


# ============================================================================
# Database Connection Functions
# ============================================================================

def get_mysql_connection():
    """
    Établit une connexion avec le serveur MySQL
    
    Utilise les paramètres définis dans config.py (MYSQL_CONFIG).
    La syntaxe **MYSQL_CONFIG dépacke le dictionnaire en paramètres nommés.
    
    Retourne:
        pymysql.Connection: Connexion MySQL ou None si erreur de connexion
    """
    try:
        # Dépackage du dictionnaire: **MYSQL_CONFIG devient host=..., user=..., etc.
        connection = pymysql.connect(**MYSQL_CONFIG)
        return connection
    except Error as err:
        # Gestion des erreurs courantes de MySQL
        if "Unknown MySQL server host" in str(err):
            print(f"Erreur: Serveur introuvable: {MYSQL_CONFIG['host']}")
        elif "Access denied" in str(err):
            print(f"Erreur: Authentification échouée - vérifiez utilisateur/password")
        else:
            print(f"Erreur de connexion: {err}")
        return None


# ============================================================================
# Menu Functions
# ============================================================================

def display_menu():
    """Affiche le menu du Module 2"""
    print("\n" + "="*64)
    print("MODULE 2 - REQUÊTES MYSQL".center(64))
    print("="*64 + "\n")
    print("  1. Sauvegarder la base de données (SQL)")
    print()
    print("  2. Exporter une table (CSV)")
    print()
    print("  0. Retour au menu principal")
    print()
    print("="*64)


# ============================================================================
# Database Backup Functions
# ============================================================================

def backup_database():
    """
    Sauvegarde complète de la base de données au format SQL
    
    Crée un fichier .sql contenant:
    - Commentaires avec métadonnées (base, timestamp)
    - La commande USE pour sélectionner la base de données
    - Pour chaque table:
      * DROP TABLE IF EXISTS (permet recréer/restore sans conflit)
      * CREATE TABLE (structure complète)
      * INSERT INTO (données avec typage correct)
    
    Stratégie de typage dans les INSERT:
    - Nombres (INT, FLOAT, DECIMAL, etc.): sans guillemets
    - Chaînes: avec guillemets simples, apostrophes échappées
    - NULL: mot-clé NULL sans guillemets
    """
    print("\nPréparation de la sauvegarde...")
    
    # Étape 1: Sélectionner le dossier de destination
    print("Choix du dossier de sauvegarde SQL ...")
    user_path = get_destination_path("Choix du dossier de sauvegarde SQL ...")
    if not user_path:
        return
    
    # Étape 2: Générer le nom du fichier avec timestamp
    # Format: nombase_backup_YYYYMMDD_HHMMSS.sql
    # Le timestamp évite les doublons si multiples sauvegardes
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{MYSQL_CONFIG['database']}_backup_{timestamp}.sql"
    filepath = os.path.join(user_path, filename)
    
    # Étape 3: Établir la connexion MySQL
    connection = get_mysql_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Étape 4: Récupérer la liste de toutes les tables de la base
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"Aucune table trouvée")
            return
        
        # Étape 5: Créer et remplir le fichier SQL
        with open(filepath, 'w', encoding='utf-8') as f:
            # En-tête SQL: commentaires avec information de sauvegarde
            f.write(f"-- Sauvegarde de {MYSQL_CONFIG['database']}\n")
            f.write(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            # La commande USE sélectionne la base (utile pour restaurer sur autre serveur)
            f.write(f"USE {MYSQL_CONFIG['database']};\n\n")
            
            # Boucle sur chaque table pour la sauvegarder
            for (table_name,) in tables:
                # DROP TABLE IF EXISTS: supprime la table si elle existe
                # Évite les erreurs lors du restore si table existe déjà
                f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n\n")
                
                # Récupère et écrit la définition structurelle de la table (CREATE TABLE)
                cursor.execute(f"SHOW CREATE TABLE {table_name}")
                create_table = cursor.fetchone()[1]
                f.write(f"{create_table};\n\n")
                
                # Récupère les types de colonnes pour formater correctement les INSERT
                # Exemple: col_id=INT, col_name=VARCHAR, col_price=DECIMAL, etc.
                cursor.execute(f"DESCRIBE {table_name}")
                column_info = cursor.fetchall()
                column_types = {col[0]: col[1].lower() for col in column_info}
                columns = [col[0] for col in column_info]
                
                # Récupère toutes les données de la table
                cursor.execute(f"SELECT * FROM {table_name}")
                data = cursor.fetchall()
                
                # Génère les instructions INSERT avec typage correct
                for row in data:
                    formatted_values = []
                    # Traite chaque colonne de chaque ligne
                    for col_name, val in zip(columns, row):
                        if val is None:
                            # NULL n'a pas de guillemets
                            formatted_values.append('NULL')
                        else:
                            col_type = column_types[col_name]
                            # Nombres: pas de guillemets
                            if any(num_type in col_type for num_type in ['int', 'float', 'double', 'decimal']):
                                formatted_values.append(str(val))
                            else:
                                # Chaînes: guillemets + échappement des apostrophes
                                escaped_val = str(val).replace("'", "''")
                                formatted_values.append(f"'{escaped_val}'")
                    
                    # Écrit la ligne INSERT
                    values_str = ', '.join(formatted_values)
                    f.write(f"INSERT INTO `{table_name}` VALUES ({values_str});\n")
                
                # Ligne vide entre les tables pour meilleure lisibilité
                f.write("\n")
        
        # Affichage du succès
        print(f"Sauvegarde réussie")
        print(f"   Fichier: {filepath}")
        
    except Error as err:
        print(f"Erreur lors de la sauvegarde: {err}")
    finally:
        # Toujours fermer la connexion, même en cas d'erreur
        cursor.close()
        connection.close()


# ============================================================================
# Database Export Functions  
# ============================================================================

def export_table():
    """
    Exporte une table sélectionnée au format CSV
    
    Étapes:
    1. Récupère la liste de toutes les tables disponibles
    2. Affiche et demande à l'utilisateur de choisir une table
    3. Demande le dossier de destination
    4. Exporte les données avec en-têtes de colonnes
    
    Format CSV:
    - Séparateur: ; (point-virgule) pour compatibilité Excel français
    - Encodage: UTF-8 avec BOM pour compatibilité Windows
    - Saut de lignes: géré correctement selon le système d'exploitation
    """
    print("\nRécupération des tables...")
    
    # Étape 1: Établir la connexion MySQL
    connection = get_mysql_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Étape 2: Récupérer la liste de toutes les tables de la base
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        if not tables:
            print(f"Aucune table trouvée")
            return
        
        # Étape 3: Afficher les tables disponibles pour que l'utilisateur choisisse
        print("\nTables disponibles")
        for i, table in enumerate(tables, 1):
            db_prefix = f"{MYSQL_CONFIG['database']}."
            print(f"  {i}. {db_prefix}{table}")
        
        # Étape 4: Demander à l'utilisateur de sélectionner une table
        try:
            choice = int(input("\nChoisir une table (numéro): "))
            if choice < 1 or choice > len(tables):
                print("Choix invalide")
                return
            selected_table = tables[choice - 1]
        except ValueError:
            print("Entrée invalide")
            return
        
        # Étape 5: Demander le chemin de destination
        print("\nChoix du dossier d'export CSV ...")
        user_path = get_destination_path("Choix du dossier d'export CSV ...")
        if not user_path:
            return
        
        # Étape 6: Générer le nom du fichier avec timestamp
        # Format: nombase_nomtable_YYYYMMDD_HHMMSS.csv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{MYSQL_CONFIG['database']}_{selected_table}_{timestamp}.csv"
        filepath = os.path.join(user_path, filename)
        
        # Étape 7: Récupérer les données de la table
        cursor.execute(f"SELECT * FROM {selected_table}")
        rows = cursor.fetchall()
        
        # Étape 8: Récupérer les noms des colonnes
        cursor.execute(f"DESCRIBE {selected_table}")
        columns = [col[0] for col in cursor.fetchall()]
        
        # Étape 9: Écrire le fichier CSV
        # encoding='utf-8-sig': ajoute BOM (Byte Order Mark) pour Excel Windows
        # delimiter=';': utilise point-virgule pour compatibilité Excel français
        # newline='': gère correctement les sauts de ligne cross-platform
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            # Première ligne: en-têtes de colonnes
            writer.writerow(columns)
            # Lignes suivantes: données
            writer.writerows(rows)
        
        # Affichage du succès
        print(f"Export réussi")
        print(f"   Table: {selected_table} ({len(rows)} lignes)")
        print(f"   Fichier: {filepath}")
        
    except Error as err:
        print(f"Erreur lors de l'export: {err}")
    finally:
        # Toujours fermer la connexion, même en cas d'erreur
        cursor.close()
        connection.close()


# ============================================================================
# Main Entry Point
# ============================================================================

def get_mysql_menu():
    """Point d'entrée principal du Module 2"""
    while True:
        display_menu()
        choice = input("Choisir (0-2): ").strip()
        
        if choice == "1":
            backup_database()
        elif choice == "2":
            export_table()
        elif choice == "0":
            break
        else:
            print("Choix invalide. Veuillez sélectionner 0, 1 ou 2.")
        
        input("\nAppuyez sur Entrée pour continuer...")
