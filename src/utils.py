"""
NTL-SysToolbox - Utilities
Common functions and helpers for all modules
"""
import os
import re
import tkinter as tk
from tkinter import filedialog
import paramiko
import socket


def _create_dialog_root():
    """
    Crée et configure une fenêtre tkinter pour les dialogues
    
    Retourne:
        tk.Tk: Fenêtre configurée pour être au premier plan
    """
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    root.lift()  # Mettre au premier plan
    root.attributes('-topmost', True)  # Toujours visible
    return root


def get_file_path(title="Sélectionner un fichier", filetypes=None):
    """
    Ouvre une boîte de dialogue pour sélectionner un fichier
    
    Args:
        title: Titre du dialogue
        filetypes: Liste des types de fichiers acceptés
    
    Retourne:
        str: Chemin du fichier ou None si annulé
    """
    if filetypes is None:
        filetypes = [("All files", "*.*")]
    
    try:
        root = _create_dialog_root()
        
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=os.path.expanduser("~")
        )
        root.destroy()
        
        if not file_path:
            print("Opération annulée.")
            return None
        
        return file_path
    except:
        # Fallback: lister les fichiers du répertoire courant
        print("Boîte de dialogue indisponible, liste des fichiers disponibles...")
        current_dir = os.getcwd()
        
        # Extraire les extensions à chercher depuis filetypes
        extensions = []
        for file_type in filetypes:
            if len(file_type) > 1:
                pattern = file_type[1]
                if pattern != "*.*":
                    extensions.append(pattern)
        
        # Lister les fichiers
        available_files = []
        try:
            for file in os.listdir(current_dir):
                file_path = os.path.join(current_dir, file)
                if os.path.isfile(file_path):
                    # Si des extensions spécifiques, filtrer
                    if extensions:
                        for ext in extensions:
                            if file.endswith(ext.replace("*", "")):
                                available_files.append(file)
                                break
                    else:
                        available_files.append(file)
        except PermissionError:
            available_files = []
        
        # Afficher les fichiers disponibles
        if available_files:
            print(f"Fichiers disponibles dans {current_dir}:")
            for i, f in enumerate(available_files, 1):
                print(f"  {i}. {f}")
            choice = input("Sélectionner un fichier (numéro ou chemin): ").strip()
            
            # Si un numéro
            if choice.isdigit() and 1 <= int(choice) <= len(available_files):
                return os.path.join(current_dir, available_files[int(choice) - 1])
            # Si un chemin
            elif os.path.isfile(choice):
                return choice
            elif os.path.isfile(os.path.join(current_dir, choice)):
                return os.path.join(current_dir, choice)
        
        # Fallback final: demander le chemin
        file_path = input(f"Chemin du fichier (répertoire courant: {current_dir}): ").strip()
        if not file_path:
            return None
        
        # Chemin absolu ou relatif
        if os.path.isabs(file_path):
            return file_path if os.path.isfile(file_path) else None
        else:
            full_path = os.path.join(current_dir, file_path)
            return full_path if os.path.isfile(full_path) else None


def get_destination_path(title="Choix du dossier de destination ..."):
    """
    Ouvre une boîte de dialogue pour sélectionner le dossier de destination
    
    Args:
        title: Titre personnalisé du dialogue (optionnel)
    
    Retourne:
        str: Chemin valide ou None si annulé
    """
    default_path = os.path.expanduser("~/Downloads")
    
    try:
        root = _create_dialog_root()
        
        user_path = filedialog.askdirectory(
            title=title,
            initialdir=default_path
        )
        root.destroy()
        
        if not user_path:
            print("Opération annulée.")
            return None
    except:
        # Fallback: demander le chemin en texte si la boîte de dialogue échoue
        print("Boîte de dialogue indisponible, saisie manuelle...")
        user_path = input(f"Chemin de destination (Enter pour {default_path}): ").strip()
        user_path = user_path if user_path else default_path
    
    # Crée le dossier s'il n'existe pas
    if not os.path.exists(user_path):
        try:
            os.makedirs(user_path)
        except Exception as e:
            print(f"Impossible de créer le dossier: {e}")
            return None
    
    return user_path


# ============================================================================
# SSH Connection Functions
# ============================================================================

def format_bytes(bytes_value):
    """
    Convertit les bytes en format lisible (B, KB, MB, GB, TB)
    
    Args:
        bytes_value: Nombre de bytes à convertir
    
    Retourne:
        str: Taille formatée avec unité (ex: "1.50 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_file_size(filepath):
    """
    Retourne la taille formatée d'un fichier (KB ou MB)
    
    Args:
        filepath: Chemin du fichier
    
    Retourne:
        str: Taille formatée (ex: "1.50 KB" ou "2.34 MB")
    """
    file_size = os.path.getsize(filepath)
    if file_size < 1024 * 1024:
        return f"{file_size / 1024:.2f} KB"
    return f"{file_size / (1024 * 1024):.2f} MB"


def get_ssh_credentials(server_type='ubuntu'):
    """
    Charge les paramètres de connexion SSH depuis .env ou demande à l'utilisateur
    
    Args:
        server_type: 'ubuntu' ou 'windows'
    """
    if server_type == 'ubuntu':
        env_host = os.getenv('LINUX_SERVER_HOST')
        env_user = os.getenv('LINUX_SERVER_USER')
        env_password = os.getenv('LINUX_SERVER_PASSWORD')
        env_port = os.getenv('LINUX_SERVER_PORT', '22')
    else:  # windows
        env_host = os.getenv('WINDOWS_SERVER_HOST')
        env_user = os.getenv('WINDOWS_SERVER_USER')
        env_password = os.getenv('WINDOWS_SERVER_PASSWORD')
        env_port = os.getenv('WINDOWS_SERVER_PORT', '22')
    
    # Si les infos sont dans .env (non vides), les utiliser
    if env_host and env_user and env_password:
        print(f"\nConnexion SSH en cours {env_user}@{env_host}")
        return {
            'hostname': env_host,
            'username': env_user,
            'password': env_password,
            'port': int(env_port)
        }
    
    # Sinon, demander à l'utilisateur
    print("\n" + "-"*64)
    print("PARAMÈTRES DE CONNEXION SSH".center(64))
    print("-"*64)
    print("(Les infos .env ne sont pas configurées)\n")
    
    hostname = input("Adresse IP ou hostname du serveur: ").strip()
    username = input("Nom d'utilisateur: ").strip()
    password = input("Mot de passe: ").strip()
    
    try:
        port = int(input("Port SSH (Enter pour 22): ").strip() or "22")
    except ValueError:
        port = 22
    
    return {
        'hostname': hostname,
        'username': username,
        'password': password,
        'port': port
    }


def ssh_connect(hostname, username, password, port=22):
    """
    Établit une connexion SSH avec le serveur
    
    Args:
        hostname: Adresse IP ou hostname du serveur
        username: Nom d'utilisateur
        password: Mot de passe
        port: Port SSH (défaut: 22)
    
    Retourne:
        paramiko.SSHClient: Client SSH connecté ou None si erreur
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=5)
        return client
    except paramiko.AuthenticationException:
        print(f"Erreur: Authentification échouée pour {username}@{hostname}")
        return None
    except paramiko.SSHException as e:
        print(f"Erreur SSH: {e}")
        return None
    except socket.error as e:
        print(f"Erreur de connexion: {e}")
        return None


def execute_ssh_command(client, command):
    """
    Exécute une commande via SSH et retourne le résultat
    
    Args:
        client: Client SSH paramiko connecté
        command: Commande à exécuter
    
    Retourne:
        str: Sortie de la commande ou None si erreur
    """
    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        return output
    except Exception as e:
        print(f"Erreur lors de l'exécution: {e}")
        return None


# ============================================================================
# Network Validation Functions
# ============================================================================

def validate_subnet(subnet):
    """
    Valide une plage réseau au format CIDR
    
    Format CIDR (Classless Inter-Domain Routing):
    - XXX.XXX.XXX.XXX/NN
    - XXX = octet IP (0-255)
    - NN = masque de réseau (8-32 pour IPv4)
    
    Exemples valides:
    - 192.168.1.0/24 (réseau local classique)
    - 10.0.0.0/8 (réseau privé classe A)
    - 172.16.0.0/12 (réseau privé classe B)
    
    Args:
        subnet: Plage réseau en format CIDR
    
    Retourne:
        bool: True si format CIDR valide, False sinon
    """
    # Expression régulière pour vérifier le format X.X.X.X/NN
    cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if not re.match(cidr_pattern, subnet):
        return False
    
    # Vérification que chaque octet est entre 0-255
    ip_part = subnet.split('/')[0]
    for octet in ip_part.split('.'):
        if int(octet) > 255:
            return False
    
    return True
