"""
Module 3 - End of Life Information & Network Scanning
Détecte les OS présents sur un réseau et fournit les dates de fin de vie
"""
import nmap
import socket
import re
import requests
import csv
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from pathlib import Path


EOL_API_BASE = "https://endoflife.date/api"
POPULAR_OS = ["windows", "ubuntu", "debian", "macos", "centos", "rhel", "fedora", "opensuse"]


# ============================================================================
# API Functions - Récupération des données via endoflife.date
# ============================================================================

def fetch_eol_products():
    """Récupère la liste des OS populaires disponibles via l'API EOL"""
    try:
        response = requests.get(f"{EOL_API_BASE}/all.json", timeout=5)
        response.raise_for_status()
        all_products = response.json()
        
        os_products = {}
        for product_name in all_products:
            if product_name.lower() in POPULAR_OS:
                os_products[product_name] = product_name
        
        return os_products
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion: {e}")
        return None


def fetch_os_versions(product_name):
    """Récupère toutes les versions/cycles d'un OS avec leurs dates EOL"""
    try:
        url = f"{EOL_API_BASE}/{product_name.lower()}.json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        cycles = response.json()
        return cycles
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des versions: {e}")
        return None


# ============================================================================
# Menu Functions
# ============================================================================

def display_menu():
    """Affiche le menu principal du Module 3"""
    print("\n" + "="*64)
    print("MODULE 3 - END OF LIFE / SCAN RÉSEAU".center(64))
    print("="*64 + "\n")
    print("  1. Scanner une plage réseau (détection OS)")
    print("  2. Lister les versions d'un OS (dates de fin de vie)")
    print("  3. Importer CSV et ajouter infos EOL")
    print()
    print("  0. Retour au menu principal")
    print()
    print("="*64)


# ============================================================================
# Network Scanning Functions - Fonction n°1
# ============================================================================

def validate_subnet(subnet):
    """Valide une plage CIDR (ex: 192.168.1.0/24)"""
    cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if not re.match(cidr_pattern, subnet):
        return False
    
    ip_part = subnet.split('/')[0]
    for octet in ip_part.split('.'):
        if int(octet) > 255:
            return False
    
    return True


def scan_network(subnet):
    """
    Scan une plage réseau avec nmap pour détecter les OS
    
    Essaie plusieurs niveaux de détection:
    - Avec OS fingerprinting (nécessite droits admin)
    - Avec service detection uniquement
    - Juste la détection des ports ouverts
    """
    if not validate_subnet(subnet):
        print(f"Format invalide. Utilisez le format CIDR (ex: 192.168.1.0/24)")
        return None
    
    print(f"\n⏳ Scan en cours (cela peut prendre du temps)...")
    print(f"   Plage: {subnet}\n")
    
    try:
        nm = nmap.PortScanner()
        common_ports = "22,80,443,445,3389,5985,8080,8443"
        
        try:
            nm.scan(hosts=subnet, arguments=f'-p {common_ports} -O -sV')
        except:
            try:
                nm.scan(hosts=subnet, arguments=f'-p {common_ports} -sV')
            except:
                nm.scan(hosts=subnet, arguments=f'-p {common_ports}')
        
        return nm
    except nmap.PortScannerError as e:
        print(f"Erreur nmap: {e}")
        return None


def get_os_guess(nm_host):
    """Détermine l'OS détecté basé sur les ports et le fingerprinting"""
    try:
        os_matches = nm_host.get('osmatch')
        if os_matches and len(os_matches) > 0:
            for os_match in os_matches:
                if isinstance(os_match, str):
                    return os_match
    except:
        pass
    
    try:
        tcp_ports = nm_host.get('tcp', {})
        open_ports = [p for p, info in tcp_ports.items() if info.get('state') == 'open']
        
        if open_ports:
            windows_ports = [3389, 445, 5985]
            linux_ports = [22]
            
            windows_list = [p for p in open_ports if p in windows_ports]
            linux_list = [p for p in open_ports if p in linux_ports]
            
            if windows_list:
                port_list = ', '.join([str(p) for p in windows_list])
                return f"Windows (ports: {port_list})"
            elif linux_list:
                return "Linux/Unix (SSH: 22)"
            else:
                port_list = ', '.join([str(p) for p in open_ports[:3]])
                return f"Serveur (ports: {port_list})"
    except:
        pass
    
    try:
        cpe_list = nm_host.get('cpe')
        if cpe_list and len(cpe_list) > 0:
            return f"Basé sur: {str(cpe_list)[0:30]}"
    except:
        pass
    
    return "Unknown"


def display_scan_results(nm):
    """Affiche les résultats du scan réseau"""
    print("\n" + "="*64)
    print("RÉSULTATS DU SCAN RÉSEAU".center(64))
    print("="*64 + "\n")
    
    all_hosts = nm.all_hosts()
    
    if not all_hosts:
        print("Aucun hôte détecté.")
        return
    
    print(f"Hôtes détectés: {len(all_hosts)}\n")
    print(f"{'IP':<17} {'HOSTNAME':<17} {'OS DÉTECTÉ':<30}")
    print("-" * 64)
    
    for host in all_hosts:
        ip_str = str(host)[:16]
        hostname_str = "N/A"
        
        try:
            hostname_str = socket.gethostbyaddr(host)[0][:16]
        except:
            pass
        
        try:
            os_str = str(get_os_guess(nm[host]))[:29]
        except:
            os_str = "Erreur scan"
        
        print(f"{ip_str:<17} {hostname_str:<17} {os_str:<30}")
    
    print("\n" + "="*64)


def scan_network_menu():
    """Menu pour scanner une plage réseau"""
    subnet = input("\nEntrez la plage réseau (Enter pour 192.168.10.0/24): ").strip()
    
    if not subnet:
        subnet = "192.168.10.0/24"
    
    nm = scan_network(subnet)
    if nm is not None:
        display_scan_results(nm)


# ============================================================================
# Utility Functions
# ============================================================================

def get_destination_path():
    """
    Ouvre une boîte de dialogue pour sélectionner le dossier de destination
    Retourne: chemin valide ou None si annulé
    """
    default_path = os.path.expanduser("~/Downloads")
    
    try:
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre principale
        
        user_path = filedialog.askdirectory(
            title="Choix du dossier d'export du CSV EOL",
            initialdir=default_path
        )
        root.destroy()
        
        if not user_path:
            print("Opération annulée par l'utilisateur.")
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
# CSV Processing Functions - Fonction n°3
# ============================================================================

def get_eol_date_for_version(product_name, version):
    """
    Récupère la date EOL pour une version spécifique d'un OS
    
    Retourne:
        tuple: (eol_date, is_lts) ou (None, False) si non trouvé
    """
    try:
        cycles = fetch_os_versions(product_name)
        if not cycles:
            return None, False
        
        # Cherche la version exacte
        for cycle in cycles:
            if str(cycle.get('cycle', '')).lower() == str(version).lower():
                eol_str = cycle.get('eol', None)
                is_lts = cycle.get('lts', False)
                
                if eol_str and eol_str != "False":
                    try:
                        eol_date = datetime.strptime(str(eol_str), "%Y-%m-%d").date()
                        return eol_date, is_lts
                    except ValueError:
                        pass
                
                return eol_str, is_lts
        
        return None, False
    except:
        return None, False


def determine_status(eol_date):
    """
    Détermine le statut basé sur la date EOL
    
    Retourne:
        str: "Support actif", "EOL dans X jours" ou "Fin de vie (X jours)"
    """
    if eol_date is None:
        return "Statut inconnu"
    
    if isinstance(eol_date, str):
        return "Support actif" if eol_date == "False" else str(eol_date)
    
    try:
        today = datetime.now().date()
        
        if eol_date < today:
            days_ago = (today - eol_date).days
            return f"Fin de vie ({days_ago}j)"
        else:
            days_left = (eol_date - today).days
            if days_left < 180:
                return f"EOL dans {days_left} jours"
            else:
                return "Support actif"
    except:
        return "Statut inconnu"


def process_csv_file(input_file, output_file):
    """
    Traite un fichier CSV d'entrée et ajoute les informations EOL
    
    Format entrée: nom;os;version
    Format sortie: nom;os;version;date_eol;etat
    """
    try:
        # Vérifier que le fichier existe
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"Fichier introuvable: {input_file}")
            return False
        
        results = []
        
        print(f"\nTraitement du fichier {input_file}...")
        
        # Lire le fichier CSV
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            
            # Vérifier l'en-tête
            header = next(reader, None)
            if not header or len(header) < 3:
                print("Format invalide. attendu: nom;os;version")
                return False
            
            # Traiter chaque ligne
            for row_num, row in enumerate(reader, start=2):
                if len(row) < 3:
                    print(f"Ligne {row_num}: format invalide, ignorée")
                    continue
                
                nom, os, version = row[0].strip(), row[1].strip(), row[2].strip()
                
                # Récupérer les infos EOL
                eol_date, is_lts = get_eol_date_for_version(os, version)
                status = determine_status(eol_date)
                
                # Formater la date EOL pour la sortie
                eol_str = "N/A"
                if isinstance(eol_date, datetime) or hasattr(eol_date, 'year'):
                    eol_str = str(eol_date)
                elif eol_date is not None:
                    eol_str = str(eol_date)
                
                results.append({
                    'nom': nom,
                    'os': os,
                    'version': version,
                    'date_eol': eol_str,
                    'etat': status
                })
        
        # Écrire le fichier de sortie
        output_path = Path(output_file)
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['nom', 'os', 'version', 'date_eol', 'etat'], delimiter=';')
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nFichier généré: {output_file}")
        print(f"   {len(results)} entrées traitées")
        return True
    
    except Exception as e:
        print(f"Erreur lors du traitement: {e}")
        return False


def csv_import_menu():
    """Menu pour importer et traiter un fichier CSV"""
    print("\n" + "="*64)
    print("IMPORT CSV - EOL CHECK".center(64))
    print("="*64 + "\n")
    
    # Ouvrir une boîte de dialogue pour sélectionner le fichier CSV
    print("Choix du fichier CSV d'import")
    try:
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre principale
        
        input_file = filedialog.askopenfilename(
            title="Choix du fichier d'import CSV (nom;os;version)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        root.destroy()
        
        if not input_file:
            print("Opération annulée.")
            return
    except:
        # Fallback: demander le chemin en texte si la boîte de dialogue échoue
        print("Boîte de dialogue indisponible, saisie manuelle...")
        input_file = input("Fichier CSV source (nom;os;version): ").strip()
        
        if not input_file:
            print("Opération annulée.")
            return
    
    # Construire le nom du fichier de sortie
    input_path = Path(input_file)
    output_file = input_path.stem + "_eol" + input_path.suffix
    
    print(f"\nFichier de sortie: {output_file}")
    
    # Traiter le fichier
    if process_csv_file(input_file, output_file):
        print("\n" + "="*64)
        
        # Télécharger directement le fichier
        print("\nChoix du dossier d'export du CSV EOL :")
        dest_path = get_destination_path()
        
        if dest_path:
            try:
                dest_file = os.path.join(dest_path, str(output_file))
                shutil.copy(output_file, dest_file)
                print(f"\nFichier téléchargé: {dest_file}")
                
                # Supprimer le fichier du projet après téléchargement
                try:
                    os.remove(output_file)
                except Exception as e:
                    print(f"Impossible de supprimer le fichier temporaire: {e}")
            except Exception as e:
                print(f"Erreur lors du téléchargement: {e}")
        
        print("\n" + "="*64)
    else:
        print("\n" + "="*64)




def list_os_versions():
    """Affiche toutes les versions d'un OS avec leurs dates de fin de vie"""
    print("\nRécupération de la liste des OS...")
    
    products = fetch_eol_products()
    if products is None:
        return
    
    os_names = sorted(list(products.keys()))
    
    print("\n" + "="*64)
    print("OS DISPONIBLES".center(64))
    print("="*64 + "\n")
    
    for i, os_name in enumerate(os_names, 1):
        print(f"  {i}. {os_name}")
    
    print()
    choice = input("Choisir un OS (numéro): ").strip()
    
    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(os_names):
            print("Choix invalide.")
            return
        selected_os = os_names[choice_idx]
    except ValueError:
        print("Veuillez entrer un numéro valide.")
        return
    
    print(f"\nRécupération des versions de {selected_os}...")
    
    cycles = fetch_os_versions(selected_os)
    if cycles is None or len(cycles) == 0:
        print(f"Aucune version trouvée pour {selected_os}.")
        return
    
    # Affiche les versions
    print("\n" + "="*64)
    print(f"VERSIONS - {selected_os}".center(64))
    print("="*64 + "\n")
    
    print(f"{'VERSION':<18} {'EOL':<14} {'LTS':<2} {'STATUT':<30}")
    print("-" * 64)
    
    # Trie par numéro de version décroissant
    try:
        sorted_cycles = sorted(cycles, 
                              key=lambda x: tuple(map(int, str(x.get('cycle', '0')).split('.'))), 
                              reverse=True)
    except:
        sorted_cycles = cycles
    
    today = datetime.now().date()
    
    for cycle in sorted_cycles:
        version = str(cycle.get('cycle', 'N/A'))[:18]
        eol_str = str(cycle.get('eol', 'N/A'))[:13]
        is_lts = cycle.get('lts', False)
        lts_str = "✓" if is_lts else ""
        
        # Détermine le statut
        status = "Support actif"
        try:
            eol_date = datetime.strptime(eol_str, "%Y-%m-%d").date()
            
            if eol_date < today:
                days_ago = (today - eol_date).days
                status = f"Fin de vie ({days_ago}j)"
            elif (eol_date - today).days < 180:
                days_left = (eol_date - today).days
                status = f"EOL dans {days_left} jours"
        except ValueError:
            pass
        
        print(f"{version:<18} {eol_str:<14} {lts_str:<2} {status:<30}")
    
    print("\n" + "="*64)


# ============================================================================
# Main Entry Point
# ============================================================================

def get_eol_info():
    """Point d'entrée principal du Module 3"""
    while True:
        display_menu()
        choice = input("Choisir (0-3): ").strip()
        
        if choice == "1":
            scan_network_menu()
        elif choice == "2":
            list_os_versions()
        elif choice == "3":
            csv_import_menu()
        elif choice == "0":
            break
        else:
            print("Choix invalide. Veuillez sélectionner 0, 1, 2 ou 3.")
        
        input("\nAppuyez sur Entrée pour continuer...")