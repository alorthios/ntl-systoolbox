"""
NTL-SysToolbox - Utilities
Common functions and helpers for all modules
"""
import os
import tkinter as tk
from tkinter import filedialog


def _create_dialog_root():
    """
    Crée et configure une fenêtre tkinter pour les dialogues
    Retourne un root configuré pour être au premier plan
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
    
    Retourne: chemin du fichier ou None si annulé
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
        title: Titre personalisé du dialogue (optionnel)
    
    Retourne: chemin valide ou None si annulé
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
