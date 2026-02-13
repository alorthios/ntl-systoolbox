"""
NTL-SysToolbox
"""

import sys
import os


def display_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                   NTL-SysToolbox v1.0                         ║
║                                                               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def display_main_menu():
    display_banner()
    print("\n" + "="*64)
    print("MENU PRINCIPAL".center(64))
    print("="*64 + "\n")
    print("  1. Module 1 - Statistiques Serveurs")
    print("      (CPU, RAM, Disk, Uptime)")
    print()
    print("  2. Module 2 - Requêtes MySQL")
    print("      (Base de données serveur)")
    print()
    print("  3. Module 3 - End of Life")
    print("      (Informations de fin de vie)")
    print()
    print("  0. Quitter")
    print()
    print("="*64)
    
    choice = input("\nChoisir (0-3): ").strip()
    return choice


def handle_module_1():
    while True:
        module1_server_stats.display_menu()
        choice = input("\nChoisir (0-2): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            module1_server_stats.get_server_stats()
        elif choice == "2":
            module1_server_stats.get_uptime()
        else:
            print("\n❌ Choix invalide. Veuillez réessayer.")
        
        input("\nAppuyez sur Entrée pour continuer...")


def handle_module_2():
    while True:
        module2_mysql.display_menu()
        choice = input("\nChoisir (0-2): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            module2_mysql.query_database()
        elif choice == "2":
            module2_mysql.list_tables()
        else:
            print("\n❌ Choix invalide. Veuillez réessayer.")
        
        input("\nAppuyez sur Entrée pour continuer...")


def handle_module_3():
    while True:
        module3_eol.display_menu()
        choice = input("\nChoisir (0-1): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            module3_eol.get_eol_info()
        else:
            print("\n❌ Choix invalide. Veuillez réessayer.")
        
        input("\nAppuyez sur Entrée pour continuer...")


def main():
    try:
        while True:
            choice = display_main_menu()
            
            if choice == "0":
                print("\n👋 Au revoir!\n")
                sys.exit(0)
            elif choice == "1":
                handle_module_1()
            elif choice == "2":
                handle_module_2()
            elif choice == "3":
                handle_module_3()
            else:
                print("\n❌ Choix invalide (0-3). Veuillez réessayer.\n")
                input("Appuyez sur Entrée pour continuer...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrompue (Ctrl+C)")
        print("Au revoir!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
