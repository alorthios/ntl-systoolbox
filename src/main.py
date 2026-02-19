"""
NTL-SysToolbox - Main Menu and Navigation
Entry point for the CLI application
"""

import sys

# Import modules
from . import module1_server_stats
from . import module2_mysql
from . import module3_eol


def display_banner():
    """Display the ASCII art banner for NTL-SysToolbox"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                   NTL-SysToolbox v2.0.0                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def display_main_menu():
    """Display the main menu and return user choice"""
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
    """Handle Module 1 - Server Statistics"""
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
            print("\nChoix invalide. Veuillez réessayer.")
        
        input("\nAppuyez sur Entrée pour continuer...")


def handle_module_2():
    """Handle Module 2 - MySQL Database Management"""
    module2_mysql.get_mysql_menu()


def handle_module_3():
    """Handle Module 3 - End of Life Info"""
    module3_eol.get_eol_info()


def main():
    """Main application loop"""
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
