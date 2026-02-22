"""
NTL-SysToolbox - Utilities
Common functions and helpers for all modules
"""
import os
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
        # Fallback: demander le chemin en texte si la boîte de dialogue échoue
        print("Boîte de dialogue indisponible, saisie manuelle...")
        return input("Chemin du fichier: ").strip()


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
        print(f"\n[OK] Connexion avec infos de .env: {env_user}@{env_host}")
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
