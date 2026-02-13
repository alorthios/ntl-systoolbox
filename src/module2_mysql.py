"""
NTL-SysToolbox - Module 2: MySQL Database
Gère la sauvegarde et l'export de données depuis MySQL
"""
import mysql.connector
from mysql.connector import Error
import csv
import os
from datetime import datetime
from config import MYSQL_CONFIG


def get_mysql_connection():
    """
    Établit une connexion avec le serveur MySQL
    Retourne: connexion MySQL ou None si erreur
    """
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except Error as err:
        # Gestion des erreurs courantes
        if err.errno == 2003:
            print(f"❌ Impossible de se connecter au serveur: {MYSQL_CONFIG['host']}")
        elif err.errno == 1045:
            print(f"❌ Erreur d'authentification - vérifiez l'utilisateur/password")
        else:
            print(f"❌ Erreur: {err}")
        return None


def display_menu():
    """Affiche le menu du Module 2"""
    print("\n" + "="*60)
    print("MODULE 2 - REQUÊTES MYSQL".center(60))
    print("="*60 + "\n")
    print("  1. Sauvegarder la base de données (SQL)")
    print()
    print("  2. Exporter une table (CSV)")
    print()
    print("  0. Retour au menu principal")
    print()
    print("="*60)


def backup_database():
    """
    Sauvegarde la base de données entière au format SQL
    Crée un fichier .sql avec tous les schémas et données
    """
    print("\n⏳ Préparation de la sauvegarde...")
    
    # Demande le chemin de destination
    default_path = os.path.expanduser("~/Downloads")
    user_path = input(f"\nChemin de destination (Enter pour {default_path}): ").strip()
    user_path = user_path if user_path else default_path
    
    # Crée le dossier s'il n'existe pas
    if not os.path.exists(user_path):
        try:
            os.makedirs(user_path)
        except Exception as e:
            print(f"❌ Impossible de créer le dossier: {e}")
            return
    
    # Génère le nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{MYSQL_CONFIG['database']}_backup_{timestamp}.sql"
    filepath = os.path.join(user_path, filename)
    
    # Se connecte à MySQL
    connection = get_mysql_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Récupère la liste des tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"❌ Aucune table trouvée")
            return
        
        # Crée le fichier SQL
        with open(filepath, 'w', encoding='utf-8') as f:
            # En-tête du fichier
            f.write(f"-- Sauvegarde de {MYSQL_CONFIG['database']}\n")
            f.write(f"-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"USE {MYSQL_CONFIG['database']};\n\n")
            
            # Exporte chaque table
            for (table_name,) in tables:
                # Structure de la table
                cursor.execute(f"SHOW CREATE TABLE {table_name}")
                create_table = cursor.fetchone()[1]
                f.write(f"{create_table};\n\n")
                
                # Données de la table
                cursor.execute(f"SELECT * FROM {table_name}")
                data = cursor.fetchall()
                
                # Récupère les noms de colonnes
                cursor.execute(f"DESCRIBE {table_name}")
                columns = [col[0] for col in cursor.fetchall()]
                
                # Écrit les instructions INSERT
                for row in data:
                    values = ', '.join([
                        f"'{str(val).replace(chr(39), chr(39)+chr(39))}'" 
                        if val is not None else 'NULL' 
                        for val in row
                    ])
                    f.write(f"INSERT INTO {table_name} VALUES ({values});\n")
                
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
    Exporte une table au format CSV avec séparateur ;
    L'utilisateur choisit la table à exporter
    """
    print("\n⏳ Récupération des tables...")
    
    # Se connecte à MySQL
    connection = get_mysql_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Récupère la liste des tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        if not tables:
            print(f"❌ Aucune table trouvée")
            return
        
        # Affiche les tables disponibles
        print("\n📊 Tables disponibles:")
        for i, table in enumerate(tables, 1):
            db_prefix = f"{MYSQL_CONFIG['database']}."
            print(f"  {i}. {db_prefix}{table}")
        
        # Demande à l'utilisateur de choisir
        try:
            choice = int(input("\nChoisir une table (numéro): "))
            if choice < 1 or choice > len(tables):
                print("❌ Choix invalide")
                return
            selected_table = tables[choice - 1]
        except ValueError:
            print("❌ Entrée invalide")
            return
        
        # Demande le chemin de destination
        default_path = os.path.expanduser("~/Downloads")
        user_path = input(f"\nChemin de destination (Enter pour {default_path}): ").strip()
        user_path = user_path if user_path else default_path
        
        # Crée le dossier s'il n'existe pas
        if not os.path.exists(user_path):
            try:
                os.makedirs(user_path)
            except Exception as e:
                print(f"❌ Impossible de créer le dossier: {e}")
                return
        
        # Génère le nom du fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{MYSQL_CONFIG['database']}_{selected_table}_{timestamp}.csv"
        filepath = os.path.join(user_path, filename)
        
        # Récupère les données
        cursor.execute(f"SELECT * FROM {selected_table}")
        rows = cursor.fetchall()
        
        # Récupère les noms de colonnes
        cursor.execute(f"DESCRIBE {selected_table}")
        columns = [col[0] for col in cursor.fetchall()]
        
        # Écrit le fichier CSV avec séparateur ;
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"✅ Export réussi!")
        print(f"   Table: {selected_table} ({len(rows)} lignes)")
        print(f"   Fichier: {filepath}")
        
    except Error as err:
        print(f"❌ Erreur lors de l'export: {err}")
    finally:
        cursor.close()
        connection.close()
