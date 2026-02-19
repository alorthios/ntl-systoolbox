"""
Module 3 - End of Life Information & Network Scanning
Détecte les OS présents sur un réseau et fournit les dates de fin de vie
"""
import nmap
import socket
import re
import requests
from datetime import datetime


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
# End of Life Listing Functions - Fonction n°2
# ============================================================================

def list_os_versions():
    """Affiche toutes les versions d'un OS avec leurs dates de fin de vie"""
    print("\n⏳ Récupération de la liste des OS...")
    
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
        choice = input("Choisir (0-2): ").strip()
        
        if choice == "1":
            scan_network_menu()
        elif choice == "2":
            list_os_versions()
        elif choice == "0":
            break
        else:
            print("Choix invalide. Veuillez sélectionner 0, 1 ou 2.")
        
        input("\nAppuyez sur Entrée pour continuer...")