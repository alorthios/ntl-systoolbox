"""
NTL-SysToolbox - Module 1: Server Statistics & Monitoring
Affiche les statistiques du serveur: CPU, RAM, Disk, Uptime
"""


# ============================================================================
# Menu Functions
# ============================================================================

def display_menu():
    """Affiche le menu du Module 1"""
    print("\n" + "="*60)
    print("MODULE 1 - STATISTIQUES SERVEURS".center(60))
    print("="*60 + "\n")
    print("  1. Afficher statistiques serveur")
    print("      (CPU, RAM, Disk)")
    print()
    print("  2. Afficher uptime du système")
    print()
    print("  0. Retour au menu principal")
    print()
    print("="*60)


# ============================================================================
# Server Statistics Functions
# ============================================================================

def get_server_stats():
    """
    Affiche les statistiques actuelles du serveur
    
    Statistiques à afficher:
    - CPU Usage: pourcentage d'utilisation du processeur en temps réel
    - RAM Usage: mémoire vive utilisée vs disponible en gigaoctets
    - Disk Usage: espace disque utilisé vs disponible par volume
    
    Note: Cette fonction est une placeholder en développement.
    À compléter avec les appels aux bibliothèques psutil ou os.
    """
    print("\nRécupération des statistiques serveur...")
    print("\n[Module 1 - À développer]")
    print("Affichage des statistiques:")
    print("  • CPU Usage")
    print("  • RAM Usage")
    print("  • Disk Usage")


# ============================================================================
# System Uptime Functions
# ============================================================================

def get_uptime():
    """
    Affiche le temps depuis le dernier démarrage du système
    
    L'uptime (durée de fonctionnement) indique depuis combien de temps
    le système est en cours d'exécution sans redémarrage.
    
    Affichage attendu: Jours, Heures, Minutes
    
    Note: Cette fonction est une placeholder en développement.
    À compléter avec les appels aux commandes système ou psutil.
    """
    print("\nRécupération de l'uptime du système...")
    print("\n[Module 1 - À développer]")
    print("Affichage de l'uptime du serveur")
