"""
NTL-SysToolbox - Module 3 - End of Life Information & Network Scanning
Détecte les OS présents sur un réseau et fournit les dates de fin de vie
"""
try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False
    
import socket
import re
import requests
import csv
import os
import shutil
from datetime import datetime
from pathlib import Path
from .utils import get_destination_path, get_file_path, validate_subnet


EOL_API_BASE = "https://endoflife.date/api"
POPULAR_OS = ["windows", "ubuntu", "debian", "macos", "centos", "rhel", "fedora", "opensuse"]


# ============================================================================
# API Functions - Récupération des données via endoflife.date
# ============================================================================

def fetch_eol_products():
    """
    Récupère la liste des OS populaires disponibles via l'API EOL
    
    Utilise l'API https://endoflife.date/api pour récupérer les OS supportés
    et filtre uniquement les OS populaires définis dans POPULAR_OS.
    
    Retourne:
        dict: dictionnaire {nom_os: nom_os} ou None si erreur de connexion
        Exemple: {'windows': 'windows', 'ubuntu': 'ubuntu', ...}
    """
    try:
        # Appel à l'API pour récupérer la liste complète de tous les OS
        response = requests.get(f"{EOL_API_BASE}/all.json", timeout=5)
        response.raise_for_status()  # Lève une exception si code d'erreur HTTP
        all_products = response.json()
        
        # Filtrage: garder seulement les OS populaires
        os_products = {}
        for product_name in all_products:
            if product_name.lower() in POPULAR_OS:
                os_products[product_name] = product_name
        
        return os_products
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion: {e}")
        return None


def fetch_os_versions(product_name):
    """
    Récupère toutes les versions/cycles d'un OS avec leurs dates EOL
    
    L'API endoflife.date retourne pour chaque version les informations:
    - cycle: numéro de version (8.0, 10.0, 22.04, etc.)
    - eol: date ou statut de fin de support (AAAA-MM-JJ ou "False")
    - lts: booléen indiquant si c'est une version Long-Term Support
    
    Retourne:
        list: liste de dictionnaires contenant les cycles ou None si erreur
        Exemple: [{'cycle': '8.0', 'eol': '2022-01-10', 'lts': false}, ...]
    """
    try:
        # Appel API spécifique pour un OS
        # Exemple: https://endoflife.date/api/windows.json
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
    print()


# ============================================================================
# Network Scanning Functions - Fonction n°1
# ============================================================================

def scan_network(subnet):
    """
    Scan une plage réseau avec nmap pour détecter les adresses et OS actifs
    
    Stratégie de détection:
    - Essaie d'abord OS fingerprinting (analyse approfondie, nécessite admin)
    - Bascule sur détection de services (-sV) si OS fail
    - Recours simple: scan des ports courants si services fail
    
    Ports scannés: 22, 80, 443, 445, 3389, 5985, 8080, 8443
    - 22: SSH (Linux/Unix)
    - 80, 443, 8080, 8443: HTTP/HTTPS (serveurs web)
    - 445: SMB (Windows partage)
    - 3389: RDP (Windows bureau distant)
    - 5985: WinRM (Windows management)
    
    Retourne:
        nmap.PortScanner: objet résultat nmap ou None si erreur
    """
    if not NMAP_AVAILABLE:
        print("Erreur: nmap n'est pas disponible.\nInstallez nmap avant de continuer.")
        return None
    
    # Valider le format de la plage réseau avant de scanner
    if not validate_subnet(subnet):
        print(f"Format invalide. Utilisez le format CIDR (ex: 192.168.1.0/24)")
        return None
    
    print(f"\nScan en cours sur {subnet}...\n")
    
    try:
        nm = nmap.PortScanner()
        # Ports courants utilisés pour détecter les services
        common_ports = "22,80,443,445,3389,5985,8080,8443"
        
        try:
            # Tentative 1: Scan complet avec OS fingerprinting et scripts (-Pn pour Windows)
            nm.scan(hosts=subnet, arguments=f'-Pn -p {common_ports} -O -sV --script nbstat')
        except:
            try:
                # Tentative 2: Scan avec détection de services et nbstat
                nm.scan(hosts=subnet, arguments=f'-Pn -p {common_ports} -sV --script nbstat')
            except:
                # Tentative 3: Scan simple des ports
                nm.scan(hosts=subnet, arguments=f'-Pn -p {common_ports}')
        
        return nm
    except nmap.PortScannerError as e:
        print(f"Erreur nmap: {e}")
        return None


def get_os_guess(nm_host):
    """
    Détermine l'OS détecté basé sur les ports et le fingerprinting
    
    Args:
        nm_host: Données nmap du host scanné
    
    Retourne:
        str: String décrivant l'OS détecté
    """
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
    """
    Affiche les résultats du scan réseau
    
    Args:
        nm: Objet nmap.PortScanner avec résultats du scan
    """
    all_hosts = nm.all_hosts()
    
    if not all_hosts:
        print("Aucun hôte détecté.")
        return
    
    # Filtrer uniquement les hôtes avec au moins un port ouvert
    active_hosts = []
    for host in all_hosts:
        try:
            tcp_ports = nm[host].get('tcp', {})
            open_ports = [p for p, info in tcp_ports.items() if info.get('state') == 'open']
            if open_ports:
                active_hosts.append(host)
        except:
            pass
    
    if not active_hosts:
        print("Aucun hôte actif détecté avec des ports ouverts.")
        return
    
    print(f"Hôtes détectés: {len(active_hosts)}\n")
    print(f"{'IP':<17} {'HOSTNAME':<17} {'OS DÉTECTÉ':<30}")
    print("-" * 64)
    
    for host in active_hosts:
        ip_str = str(host)[:16]
        hostname_str = "N/A"
        
        # Essayer plusieurs méthodes pour récupérer le hostname
        try:
            # Méthode 1: NetBIOS name depuis le script nbstat
            if 'hostscript' in nm[host]:
                for script in nm[host]['hostscript']:
                    if script.get('id') == 'nbstat' and 'output' in script:
                        output = script['output']
                        # Extraire "NetBIOS name: XXX" de la sortie
                        match = re.search(r'NetBIOS name:\s*(\S+)', output)
                        if match:
                            # Nettoyer le hostname (retirer virgules, espaces)
                            hostname_str = match.group(1).strip(',').strip()[:16]
                            break
        except:
            pass
        
        # Méthode 2: Hostname détecté par nmap
        if hostname_str == "N/A":
            try:
                if 'hostnames' in nm[host]:
                    hostnames = nm[host]['hostnames']
                    if hostnames and len(hostnames) > 0:
                        for hostname_entry in hostnames:
                            if isinstance(hostname_entry, dict) and 'name' in hostname_entry:
                                name = hostname_entry['name']
                                if name and name.strip():
                                    hostname_str = name[:16]
                                    break
            except:
                pass
        
        # Méthode 3: DNS inverse si pas trouvé par nmap
        if hostname_str == "N/A":
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
    """
    Menu interactif pour scanner une plage réseau
    Lance un scan nmap et affiche les résultats
    """
    if not NMAP_AVAILABLE:
        print("\n" + "="*64)
        print("ERREUR: NMAP NON DISPONIBLE".center(64))
        print("="*64 + "\n")
        print("Pour utiliser le scanner réseau, installez nmap:")
        print("\n  Windows:")
        print("    - Téléchargez depuis: https://nmap.org/download.html")
        print("    - Ou: choco install nmap")
        print("\n  Ubuntu/Linux:")
        print("    - apt-get install nmap")
        print("\n")
        return
    
    # Afficher l'en-tête
    print("\n" + "="*64)
    print("SCAN D'UNE PLAGE RÉSEAU".center(64))
    print("="*64 + "\n")
    
    subnet = input("Entrez la plage réseau (Par défaut: 192.168.100.0/24): ").strip()
    
    if not subnet:
        subnet = "192.168.100.0/24"
    
    nm = scan_network(subnet)
    if nm is not None:
        display_scan_results(nm)


# ============================================================================
# CSV Processing Functions - Fonction n°3
# ============================================================================

def get_eol_date_for_version(product_name, version):
    """
    Récupère la date EOL pour une version spécifique d'un OS
    
    Gère les variantes de versions (ex: Windows 10-20h2 → 10)
    
    Retourne:
        tuple: (eol_date, is_lts) ou (None, False) si non trouvé
    """
    try:
        cycles = fetch_os_versions(product_name)
        if not cycles:
            return None, False
        
        # Normaliser la version: extraire la partie principale
        # Ex: "10-20h2" → "10", "22.04" → "22.04"
        version_normalized = version.split('-')[0].lower()
        version_original = str(version).lower()
        
        # Cherche d'abord une correspondance exacte
        for cycle in cycles:
            cycle_str = str(cycle.get('cycle', '')).lower()
            if cycle_str == version_original or cycle_str == version_normalized:
                eol_str = cycle.get('eol', None)
                is_lts = cycle.get('lts', False)
                
                if eol_str and eol_str != "False":
                    try:
                        eol_date = datetime.strptime(str(eol_str), "%Y-%m-%d").date()
                        return eol_date, is_lts
                    except ValueError:
                        pass
                
                return eol_str, is_lts
        
        # Si pas trouvé, cherche avec la version normalisée
        for cycle in cycles:
            cycle_str = str(cycle.get('cycle', '')).lower()
            if cycle_str == version_normalized:
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
    
    Args:
        eol_date: Date EOL ou None
    
    Retourne:
        str: "Support actif", "EOL dans X jours" ou "Fin de vie (X jours)"
    """
    if eol_date is None:
        return "Statut inconnu"

    if isinstance(eol_date, bool):
        return "Support actif" if eol_date is False else "Statut inconnu"
    
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
            return False, []
        
        results = []
        
        # Lire le fichier CSV
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            
            # Vérifier l'en-tête
            header = next(reader, None)
            if not header or len(header) < 3:
                print("Format invalide. attendu: nom;os;version")
                return False, []
            
            # Traiter chaque ligne
            for row_num, row in enumerate(reader, start=2):
                if len(row) < 3:
                    print(f"Ligne {row_num}: format invalide, ignorée")
                    continue
                
                nom, os, version = row[0].strip(), row[1].strip(), row[2].strip()
                
                # Récupérer les infos EOL
                eol_date, _ = get_eol_date_for_version(os, version)
                status = determine_status(eol_date)
                
                # Formater la date EOL pour la sortie
                eol_str = "N/A" if (eol_date is None or eol_date is False) else str(eol_date)
                
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
        return True, results
    
    except Exception as e:
        print(f"Erreur lors du traitement: {e}")
        return False, []


def display_imported_csv(input_file):
    """
    Affiche le contenu du fichier CSV importé par l'utilisateur
    
    Format d'affichage :
    - NOM: nom du serveur/système
    - OS: système d'exploitation
    - VERSION: numéro de version
    
    Args:
        input_file: Chemin du fichier CSV à afficher
    """
    try:
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"Fichier introuvable: {input_file}")
            return
        
        print("\n" + "-"*64)
        print("CONTENU DU FICHIER IMPORTÉ".center(64))
        print("-"*64 + "\n")
        
        # En-têtes avec largeurs de colonnes
        print(f"{'NOM':<20} {'OS':<20} {'VERSION':<24}")
        print("-" * 64)
        
        # Lire et afficher le CSV
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            header = next(reader, None)
            
            if not header or len(header) < 3:
                print("Format invalide")
                return
            
            # Afficher chaque ligne
            for row in reader:
                if len(row) >= 3:
                    nom = row[0].strip()[:20]
                    os = row[1].strip()[:20]
                    version = row[2].strip()[:24]
                    print(f"{nom:<20} {os:<20} {version:<24}")
        
        print("\n" + "-"*64)
    except Exception as e:
        print(f"Erreur lors de l'affichage du fichier: {e}")


def csv_import_menu():
    """
    Menu interactif pour importer et traiter un fichier CSV
    Enrichit le CSV avec les informations de fin de vie
    """
    print("\n" + "="*64)
    print("IMPORT CSV - EOL CHECK".center(64))
    print("="*64 + "\n")
    
    # Ouvrir une boîte de dialogue pour sélectionner le fichier CSV
    print("Choix du fichier CSV d'import (nom;os;version) ...")
    input_file = get_file_path(
        title="Choix du fichier d'import CSV (nom;os;version) ...",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if not input_file:
        return
    
    # Afficher le contenu du CSV importé
    display_imported_csv(input_file)
    
    # Construire le nom du fichier de sortie
    input_path = Path(input_file)
    output_file = input_path.stem + "_eol" + input_path.suffix
    
    # Traiter le fichier
    success, results = process_csv_file(input_file, output_file)
    
    if success:
        print("\n" + "="*64)
        
        # Télécharger directement le fichier
        print("\nChoix du dossier d'export du CSV EOL ...")
        dest_path = get_destination_path("Choix du dossier d'export du CSV EOL ...")
        
        if dest_path:
            try:
                dest_file = os.path.join(dest_path, str(output_file))
                shutil.copy(output_file, dest_file)
                print(f"\nFichier téléchargé: {dest_file}")
                
                # Supprimer le fichier du projet après téléchargement
                try:
                    os.remove(output_file)
                except Exception as e:
                    pass
            except Exception as e:
                print(f"Erreur lors du téléchargement: {e}")
        
        print("\n" + "="*64)




def list_os_versions():
    """
    Affiche toutes les versions d'un OS avec leurs dates de fin de vie
    Récupère les données via l'API endoflife.date
    """
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
    
    cycles = fetch_os_versions(selected_os)
    if cycles is None or len(cycles) == 0:
        print(f"Aucune version trouvée pour {selected_os}.")
        return
    
    # Affiche les versions
    print("\n" + "="*64)
    print(f"VERSIONS - {selected_os}".center(64))
    print("="*64 + "\n")
    
    print(f"{'VERSION':<18} {'EOL':<14} {'LTS':<6} {'STATUT':<26}")
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
        lts_str = "Oui" if is_lts else "Non"
        
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
        
        print(f"{version:<18} {eol_str:<14} {lts_str:<6} {status:<26}")
    
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