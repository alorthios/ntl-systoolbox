"""
NTL-SysToolbox - Module 2: MySQL Database Management
Gère la sauvegarde et l'export de données depuis MySQL
"""
import os
from datetime import datetime

from .utils import get_destination_path, get_ssh_credentials, ssh_connect, execute_ssh_command, format_file_size


# ============================================================================
# Helper Functions
# ============================================================================

def select_database_interactive(client):
    """
    Liste et permet à l'utilisateur de choisir une base de données
    
    Args:
        client: Client SSH paramiko connecté
    
    Retourne:
        str: Nom de la base sélectionnée ou None si erreur/annulation
    """
    list_db_cmd = (
        f"mysql -h {os.getenv('MYSQL_HOST', 'localhost')} "
        f"-P {os.getenv('MYSQL_PORT', '3306')} "
        f"-u {os.getenv('MYSQL_USER', 'root')} "
        f"-p'{os.getenv('MYSQL_PASSWORD', '')}' "
        f"-e 'SHOW DATABASES;' | tail -n +2"
    )
    
    db_output = execute_ssh_command(client, list_db_cmd)
    if not db_output:
        print("Impossible de récupérer la liste des bases de données")
        return None
    
    # Filtrer les bases système
    system_dbs = ['information_schema', 'performance_schema', 'mysql', 'sys']
    databases = [db.strip() for db in db_output.split('\n') 
                 if db.strip() and db.strip() not in system_dbs]
    
    if not databases:
        print("Aucune base de données utilisateur trouvée")
        return None
    
    # Afficher les bases disponibles
    print("\nBases de données disponibles :")
    for i, db in enumerate(databases, 1):
        print(f"  {i}. {db}")
    
    choice = input("\nChoisir une base de données (numéro): ").strip()
    
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(databases):
            return databases[choice_idx]
        print("Choix invalide")
    except ValueError:
        print("Entrée invalide")
    
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
    print("  2. Exporter une table (CSV)")
    print()
    print("  0. Retour au menu principal")
    print()
    print("="*64)
    print()


# ============================================================================
# Database Backup Functions
# ============================================================================

def backup_database():
    """
    Sauvegarde complète de la base de données au format SQL via SSH + mysqldump
    
    Utilise mysqldump sur le serveur distant via SSH pour créer un fichier .sql contenant:
    - La structure complète (CREATE TABLE)
    - Toutes les données (INSERT)
    - Les vues, triggers, procédures stockées
    
    Avantages de mysqldump:
    - Outil natif MySQL optimisé
    - Gère automatiquement tous les types de données
    - Support des fonctionnalités avancées (vues, triggers, etc.)
    - Plus rapide et fiable que la reconstruction manuelle
    """
    # Afficher le titre
    print("\n" + "="*64)
    print("SAUVEGARDE DE LA BASE DE DONNÉES (SQL)".center(64))
    print("="*64 + "\n")
    
    # Étape 1: Établir la connexion SSH au serveur Linux (où MySQL tourne)
    creds = get_ssh_credentials(server_type='ubuntu')
    client = ssh_connect(creds['hostname'], creds['username'], creds['password'], creds['port'])
    
    if not client:
        print("Échec de la connexion SSH")
        return
    
    try:
        # Étape 2: Sélectionner une base de données
        selected_db = select_database_interactive(client)
        if not selected_db:
            return
        
        # Étape 3: Sélectionner le dossier de destination local
        print("\nChoix du dossier de sauvegarde SQL ...")
        user_path = get_destination_path("Choix du dossier de sauvegarde SQL ...")
        if not user_path:
            return
        
        # Étape 5: Générer le nom du fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{selected_db}_backup_{timestamp}.sql"
        filepath = os.path.join(user_path, filename)
        remote_filepath = f"/tmp/{filename}"
        
        # Étape 6: Exécuter mysqldump sur le serveur distant
        print(f"\nCréation du dump MySQL de '{selected_db}'...")
        
        # Construction de la commande mysqldump avec options
        # --single-transaction: pour éviter les locks (InnoDB)
        # --routines: inclut les procédures stockées et fonctions
        # --triggers: inclut les triggers
        # --events: inclut les événements planifiés
        dump_cmd = (
            f"mysqldump "
            f"-h {os.getenv('MYSQL_HOST', 'localhost')} "
            f"-P {os.getenv('MYSQL_PORT', '3306')} "
            f"-u {os.getenv('MYSQL_USER', 'root')} "
            f"-p'{os.getenv('MYSQL_PASSWORD', '')}' "
            f"--single-transaction "
            f"--routines "
            f"--triggers "
            f"--events "
            f"{selected_db} > {remote_filepath}"
        )
        
        execute_ssh_command(client, dump_cmd)
        
        # Vérifier si le fichier a été créé sur le serveur distant
        check_cmd = f"test -f {remote_filepath} && echo 'OK' || echo 'ERROR'"
        check_result = execute_ssh_command(client, check_cmd)
        
        if check_result and check_result.strip() == 'OK':
            print("Dump créé avec succès sur le serveur distant")
            
            # Étape 7: Récupérer le fichier via SFTP
            print("Téléchargement du fichier SQL...")
            sftp = client.open_sftp()
            sftp.get(remote_filepath, filepath)
            sftp.close()
            
            # Étape 8: Nettoyer le fichier temporaire sur le serveur
            execute_ssh_command(client, f"rm -f {remote_filepath}")
            
            # Affichage du succès
            print(f"\nSauvegarde réussie")
            print(f"   Base de données: {selected_db}")
            print(f"   Taille: {format_file_size(filepath)}")
            print(f"   Fichier: {filepath}")
            print("\n" + "="*64)
        else:
            print(f"Erreur lors de la création du dump sur le serveur distant")
            # Afficher les erreurs éventuelles
            error_output = execute_ssh_command(client, f"cat {remote_filepath} 2>&1 || echo 'Pas de fichier'")
            if error_output:
                print(f"Sortie d'erreur: {error_output}")
    
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
    finally:
        client.close()


# ============================================================================
# Database Export Functions  
# ============================================================================

def export_table():
    """
    Exporte une table sélectionnée au format CSV
    
    Étapes:
    1. Établit connexion SSH et liste les bases de données
    2. Utilisateur choisit une base de données
    3. Liste les tables de cette base
    4. Utilisateur choisit une table
    5. Exporte les données avec en-têtes de colonnes
    
    Format CSV:
    - Séparateur: ; (point-virgule) pour compatibilité Excel français
    - Encodage: UTF-8 avec BOM pour compatibilité Windows
    - Saut de lignes: géré correctement selon le système d'exploitation
    """
    # Afficher le titre
    print("\n" + "="*64)
    print("SÉLECTION DE LA BASE DE DONNÉES".center(64))
    print("="*64 + "\n")
    
    # Étape 1: Établir la connexion SSH
    creds = get_ssh_credentials(server_type='ubuntu')
    client = ssh_connect(creds['hostname'], creds['username'], creds['password'], creds['port'])
    
    if not client:
        print("Échec de la connexion SSH")
        return
    
    try:
        # Étape 2: Sélectionner une base de données
        selected_db = select_database_interactive(client)
        if not selected_db:
            return
        
        # Étape 3: Lister les tables de la base sélectionnée
        list_tables_cmd = (
            f"mysql -h {os.getenv('MYSQL_HOST', 'localhost')} "
            f"-P {os.getenv('MYSQL_PORT', '3306')} "
            f"-u {os.getenv('MYSQL_USER', 'root')} "
            f"-p'{os.getenv('MYSQL_PASSWORD', '')}' "
            f"{selected_db} -e 'SHOW TABLES;' | tail -n +2"
        )
        
        tables_output = execute_ssh_command(client, list_tables_cmd)
        
        if not tables_output:
            print(f"Aucune table trouvée dans la base {selected_db}")
            return
        
        tables = [table.strip() for table in tables_output.split('\n') if table.strip()]
        
        if not tables:
            print(f"Aucune table trouvée dans la base {selected_db}")
            return
        
        # Étape 5: Afficher les tables disponibles
        print(f"\nTables disponibles dans '{selected_db}' :")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
        
        # Étape 6: Demander à l'utilisateur de sélectionner une table
        try:
            choice = int(input("\nChoisir une table (numéro): "))
            if choice < 1 or choice > len(tables):
                print("Choix invalide")
                return
            selected_table = tables[choice - 1]
        except ValueError:
            print("Entrée invalide")
            return
        
        # Étape 7: Demander le chemin de destination
        print("\nChoix du dossier d'export CSV ...")
        user_path = get_destination_path("Choix du dossier d'export CSV ...")
        if not user_path:
            return
        
        # Étape 8: Générer le nom du fichier avec timestamp
        # Format: nombase_nomtable_YYYYMMDD_HHMMSS.csv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{selected_db}_{selected_table}_{timestamp}.csv"
        filepath = os.path.join(user_path, filename)
        remote_temp_file = f"/tmp/{filename}"
        
        # Étape 9: Exporter via mysql client en SSH (streaming, pas de limite mémoire)
        print(f"Export de la table {selected_db}.{selected_table} en cours...")
        
        # Commande mysql qui exporte directement en CSV sur le serveur
        export_cmd = (
            f"mysql -h {os.getenv('MYSQL_HOST', 'localhost')} "
            f"-P {os.getenv('MYSQL_PORT', '3306')} "
            f"-u {os.getenv('MYSQL_USER', 'root')} "
            f"-p'{os.getenv('MYSQL_PASSWORD', '')}' "
            f"{selected_db} "
            f"-e 'SELECT * FROM {selected_table}' "
            f"| sed 's/\\t/;/g' > {remote_temp_file}"
        )
        
        execute_ssh_command(client, export_cmd)
        
        # Étape 10: Transférer le fichier via SFTP
        sftp = client.open_sftp()
        sftp.get(remote_temp_file, filepath)
        sftp.close()
        
        # Étape 11: Nettoyer le fichier temporaire sur le serveur
        execute_ssh_command(client, f"rm -f {remote_temp_file}")
        
        # Étape 12: Compter les lignes exportées (hors en-tête)
        with open(filepath, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f) - 1  # -1 pour l'en-tête
        
        # Étape 13: Convertir en UTF-8 avec BOM pour Excel Windows
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        
        # Affichage du succès
        print(f"\nExport réussi")
        print(f"   Table: {selected_db}.{selected_table} ({line_count} lignes)")
        print(f"   Taille: {format_file_size(filepath)}")
        print(f"   Fichier: {filepath}")
        print("\n" + "="*64)
        
    except Exception as err:
        print(f"Erreur lors de l'export: {err}")
    finally:
        # Toujours fermer la connexion SSH
        if 'client' in locals():
            client.close()


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
