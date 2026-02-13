"""
NTL-SysToolbox - Module 2: MySQL Database
Gère la sauvegarde et l'export de données depuis MySQL
"""
import pymysql
from pymysql import Error
import csv
import os
from datetime import datetime
from config import MYSQL_CONFIG


def get_mysql_connection():
    """
    Établit une connexion avec le serveur MySQL
    Utilise les paramètres définis dans config.py (MYSQL_CONFIG)
    Retourne: connexion MySQL ou None si erreur de connexion
    """
    try:
        # **MYSQL_CONFIG dépacke le dictionnaire en paramètres nommés
        # Équivalent à: connect(host=..., user=..., password=..., database=..., port=...)
        connection = pymysql.connect(**MYSQL_CONFIG)
        return connection
    except Error as err:
        # Gestion des erreurs courantes
        if "Unknown MySQL server host" in str(err):
            print(f"❌ Impossible de se connecter au serveur: {MYSQL_CONFIG['host']}")
        elif "Access denied" in str(err):
            print(f"❌ Erreur d'authentification - vérifiez l'utilisateur/password")
        else:
            print(f"❌ Erreur: {err}")
        return None


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


def get_destination_path():
    """
    Demande le chemin de destination et crée le dossier s'il n'existe pas
    Retourne: chemin valide ou None si erreur
    """
    default_path = os.path.expanduser("~/Downloads")
    user_path = input(f"\nChemin de destination (Enter pour {default_path}): ").strip()
    user_path = user_path if user_path else default_path
    
    # Crée le dossier s'il n'existe pas
    if not os.path.exists(user_path):
        try:
            os.makedirs(user_path)
        except Exception as e:
            print(f"❌ Impossible de créer le dossier: {e}")
            return None
    
    return user_path


def backup_database():
    """
    Sauvegarde complète de la base de données au format SQL
    Crée un fichier .sql avec:
    - DROP TABLE IF EXISTS pour chaque table (permet un rebuild complet)
    - CREATE TABLE pour le schéma complet
    - INSERT INTO avec données typées correctement (nombres sans guillemets, strings avec)
    """
    print("\n⏳ Préparation de la sauvegarde...")
    
    # Demande le chemin de destination à l'utilisateur
    user_path = get_destination_path()
    if not user_path:
        return
    
    # Génère le nom du fichier avec timestamp pour éviter les doublons
    # Format: nombase_backup_YYYYMMDD_HHMMSS.sql
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{MYSQL_CONFIG['database']}_backup_{timestamp}.sql"
    filepath = os.path.join(user_path, filename)
    
    # Se connecte à MySQL
    connection = get_mysql_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 1. Récupère la liste des tables de la base de données
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"❌ Aucune table trouvée")
            return
        
        # 2. Crée le fichier SQL
        with open(filepath, 'w', encoding='utf-8') as f:
            # En-tête du fichier avec métadonnées
            f.write(f"-- Sauvegarde de {MYSQL_CONFIG['database']}\n")
            f.write(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            # Sélectionne la base de données (essentiellement si restore sur autre base)
            f.write(f"USE {MYSQL_CONFIG['database']};\n\n")
            
            # 3. Exporte chaque table
            for (table_name,) in tables:
                # Supprime la table si elle existe (permet un rebuild/restore complet)
                # Sans cela, les INSERT échouent si les données existent déjà
                f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n\n")
                
                # Récupère et écrit la structure complète de la table
                cursor.execute(f"SHOW CREATE TABLE {table_name}")
                create_table = cursor.fetchone()[1]
                f.write(f"{create_table};\n\n")
                
                # 4. Détermine les types de colonnes (utile pour formater les INSERT)
                # Permet de différencier: nombres (sans guillemets) vs strings (avec guillemets)
                cursor.execute(f"DESCRIBE {table_name}")
                column_info = cursor.fetchall()
                column_types = {col[0]: col[1].lower() for col in column_info}
                columns = [col[0] for col in column_info]
                
                # 5. Récupère toutes les données de la table
                cursor.execute(f"SELECT * FROM {table_name}")
                data = cursor.fetchall()
                
                # 6. Génère les instructions INSERT avec typage correct
                for row in data:
                    formatted_values = []
                    for col_name, val in zip(columns, row):
                        # Gère les valeurs NULL
                        if val is None:
                            formatted_values.append('NULL')
                        else:
                            col_type = column_types[col_name]
                            # Les nombres ne doivent pas avoir de guillemets (INT, FLOAT, DECIMAL, etc.)
                            if any(num_type in col_type for num_type in ['int', 'float', 'double', 'decimal']):
                                formatted_values.append(str(val))
                            else:
                                # Les strings doivent avoir des guillemets, avec échappement des apostrophes
                                escaped_val = str(val).replace("'", "''")
                                formatted_values.append(f"'{escaped_val}'")
                    
                    # Génère la ligne INSERT
                    values_str = ', '.join(formatted_values)
                    f.write(f"INSERT INTO `{table_name}` VALUES ({values_str});\n")
                
                # Ligne vide entre les tables pour lisibilité
                f.write("\n")
        
        print(f"✅ Sauvegarde réussie!")
        print(f"   Fichier: {filepath}")
        
    except Error as err:
        print(f"❌ Erreur lors de la sauvegarde: {err}")
    finally:
        cursor.close()
        connection.close()



def export_table():
    """
    Exporte une table sélectionnée au format CSV
    Utilise le séparateur `;` pour compatibilité Excel français
    Format d'en-tête CSV: colonne1;colonne2;colonne3;...
    """
    print("\n⏳ Récupération des tables...")
    
    # Établit la connexion MySQL
    connection = get_mysql_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 1. Récupère la liste de toutes les tables de la base
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        if not tables:
            print(f"❌ Aucune table trouvée")
            return
        
        # 2. Affiche les tables disponibles avec le préfixe de la base
        print("\n📊 Tables disponibles:")
        for i, table in enumerate(tables, 1):
            db_prefix = f"{MYSQL_CONFIG['database']}."
            print(f"  {i}. {db_prefix}{table}")
        
        # 3. Demande à l'utilisateur de sélectionner une table
        try:
            choice = int(input("\nChoisir une table (numéro): "))
            if choice < 1 or choice > len(tables):
                print("❌ Choix invalide")
                return
            selected_table = tables[choice - 1]
        except ValueError:
            print("❌ Entrée invalide")
            return
        
        # 4. Demande le chemin de destination (crée le dossier si nécessaire)
        user_path = get_destination_path()
        if not user_path:
            return
        
        # 5. Génère le nom du fichier avec timestamp
        # Format: nombase_nomtable_YYYYMMDD_HHMMSS.csv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{MYSQL_CONFIG['database']}_{selected_table}_{timestamp}.csv"
        filepath = os.path.join(user_path, filename)
        
        # 6. Récupère toutes les données de la table sélectionnée
        cursor.execute(f"SELECT * FROM {selected_table}")
        rows = cursor.fetchall()
        
        # 7. Récupère les noms des colonnes pour l'en-tête CSV
        cursor.execute(f"DESCRIBE {selected_table}")
        columns = [col[0] for col in cursor.fetchall()]
        
        # 8. Écrit le fichier CSV avec les paramètres approrpiés:
        # - encoding='utf-8-sig': Ajoute BOM pour compatibilité Excel/Windows
        # - delimiter=';': Séparateur français (virgule pour décimales)
        # - newline='': Gère correctement les sauts de ligne entre OS
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            # Écrit l'en-tête avec les noms de colonnes
            writer.writerow(columns)
            # Écrit toutes les lignes de données
            writer.writerows(rows)
        
        print(f"✅ Export réussi!")
        print(f"   Table: {selected_table} ({len(rows)} lignes)")
        print(f"   Fichier: {filepath}")
        
    except Error as err:
        print(f"❌ Erreur lors de l'export: {err}")
    finally:
        cursor.close()
        connection.close()
