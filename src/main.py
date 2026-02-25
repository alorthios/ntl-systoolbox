"""
NTL-SysToolbox - Menu principal et navigation
Point d'entrée de l'application CLI
"""

import sys
from dotenv import load_dotenv

# Charger les variables d'environnement au démarrage
load_dotenv()

# Importer les modules
from . import module1_server_stats
from . import module2_mysql
from . import module3_eol


# ============================================================================
# Affichage - Bannière et menus
# ============================================================================

def display_banner():
    """Affiche la bannière ASCII de NTL-SysToolbox"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                   NTL-SysToolbox v3.0.0                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def display_main_menu():
    """Affiche le menu principal et retourne le choix de l'utilisateur"""
    display_banner()
    print("\n" + "="*64)
    print("MENU PRINCIPAL".center(64))
    print("="*64 + "\n")
    print("  1. Module 1 - Statistiques Serveurs (CPU, RAM, Disk, Uptime)")
    print("  2. Module 2 - Requêtes MySQL (Base de données serveur)")
    print("  3. Module 3 - End of Life (Informations de fin de vie)")
    print()
    print("  0. Quitter")
    print()
    print("="*64)
    
    choice = input("\nChoisir (0-3): ").strip()
    return choice


# ============================================================================
# Gestionnaires de modules
# ============================================================================

def handle_module_1():
    """Gère le Module 1 - Statistiques serveur"""
    while True:
        module1_server_stats.display_menu()
        choice = input("\nChoisir (0-4): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            module1_server_stats.check_ad_dns()
        elif choice == "2":
            module1_server_stats.check_mysql()
        elif choice == "3":
            module1_server_stats.check_remote_server(server_type='windows')
        elif choice == "4":
            module1_server_stats.check_remote_server(server_type='ubuntu')
        else:
            print("\nChoix invalide. Veuillez réessayer.")
        
        input("\nAppuyez sur Entrée pour continuer...")


def handle_module_2():
    """Gère le Module 2 - Gestion base de données MySQL"""
    module2_mysql.get_mysql_menu()


def handle_module_3():
    """Gère le Module 3 - Informations End of Life"""
    module3_eol.get_eol_info()



# ============================================================================
# Point d'entrée
# ============================================================================

def main():
    """Boucle principale de l'application"""
    try:
        while True:
            choice = display_main_menu()
            
            if choice == "0":
                print("\nAu revoir!\n")
                sys.exit(0)
            elif choice == "1":
                handle_module_1()
            elif choice == "2":
                handle_module_2()
            elif choice == "3":
                handle_module_3()
            else:
                print("\nChoix invalide (0-3). Veuillez réessayer.\n")
                input("Appuyez sur Entrée pour continuer...")
    
    except KeyboardInterrupt:
        print("\nApplication interrompue (Ctrl+C)")
        print("Au revoir!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nErreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
