"""
NTL-SysToolbox - Module 1: Server Statistics & Monitoring
Vérification des ressources serveur: Windows Server et Ubuntu/Linux via SSH
"""
from .utils import (
    get_ssh_credentials, ssh_connect, execute_ssh_command, format_bytes
)


# ============================================================================
# Menu Functions
# ============================================================================

def display_menu():
    """Affiche le menu principal du Module 1"""
    print("\n" + "="*64)
    print("MODULE 1 - STATISTIQUES SERVEURS".center(64))
    print("="*64 + "\n")
    print("  1. Vérifier état AD / DNS")
    print("      (Contrôleurs de domaine)")
    print()
    print("  2. Vérifier état MySQL")
    print("      (Base de données serveur)")
    print()
    print("  3. Vérifier ressources Windows Server")
    print("      (CPU, RAM, Disk, Uptime)")
    print()
    print("  4. Vérifier ressources Ubuntu/Linux Server")
    print("      (CPU, RAM, Disk, Uptime)")
    print()
    print("  0. Retour au menu principal")
    print()
    print("="*64)


# ============================================================================
# Placeholder Functions (1 & 2)
# ============================================================================

def check_ad_dns():
    """Vérification état AD/DNS (À développer)"""
    print("\n" + "="*64)
    print("VÉRIFICATION DES SERVICES AD/DNS (Windows)".center(64))
    print("="*64)
    creds = get_ssh_credentials(server_type='windows')
    client = ssh_connect(creds['hostname'], creds['username'], creds['password'], creds['port'])
    results = []
    if client:
        # Active Directory (NTDS)
        try:
            ad_status = execute_ssh_command(client, 'powershell -Command "Get-Service NTDS | Select-Object -ExpandProperty Status"')
            ad_ok = ad_status and ad_status.strip().lower() == 'running'
            results.append(("Active Directory (NTDS)", ad_ok, ad_status.strip() if ad_status else 'inconnu'))
        except Exception as e:
            results.append(("Active Directory (NTDS)", False, f"Erreur: {e}"))
        # DNS
        try:
            dns_status = execute_ssh_command(client, 'powershell -Command "Get-Service DNS | Select-Object -ExpandProperty Status"')
            dns_ok = dns_status and dns_status.strip().lower() == 'running'
            results.append(("DNS", dns_ok, dns_status.strip() if dns_status else 'inconnu'))
        except Exception as e:
            results.append(("DNS", False, f"Erreur: {e}"))
        client.close()
    else:
        results.append(("Connexion SSH Windows", False, "Impossible de se connecter"))
    # Affichage homogène
    print("\nRésultat :")
    for label, ok, status in results:
        print(f"  {label:<28} [{'OK' if ok else 'ERREUR'}]  {status}")
    print("\n" + "="*64)


def check_mysql():
    """Vérification état MySQL (À développer)"""
    print("\n" + "="*64)
    print("CHECK MYSQL".center(64))
    print("="*64 + "\n")
    print("\n" + "="*64)
    print("VÉRIFICATION DU SERVICE MYSQL (Linux)".center(64))
    print("="*64)
    creds = get_ssh_credentials(server_type='ubuntu')
    client = ssh_connect(creds['hostname'], creds['username'], creds['password'], creds['port'])
    results = []
    if client:
        # systemctl
        try:
            output = execute_ssh_command(client, "systemctl is-active mysql")
            ok = output.strip() == "active"
            results.append(("MySQL (systemctl)", ok, output.strip()))
        except Exception as e:
            results.append(("MySQL (systemctl)", False, f"Erreur: {e}"))
        # service (fallback)
        if not results[0][1]:
            try:
                output = execute_ssh_command(client, "service mysql status")
                ok = "active (running)" in output
                results.append(("MySQL (service)", ok, output.strip()))
            except Exception as e2:
                results.append(("MySQL (service)", False, f"Erreur: {e2}"))
        client.close()
    else:
        results.append(("Connexion SSH Linux", False, "Impossible de se connecter"))
    # Affichage homogène
    print("\nRésultat :")
    for label, ok, status in results:
        print(f"  {label:<28} [{'OK' if ok else 'ERREUR'}]  {status}")
    print("\n" + "="*64)


# ============================================================================
# Récupération des ressources serveur (fonctions Linux et Windows)
# ============================================================================

def get_remote_uptime_linux(client):
    """
    Récupère l'uptime via SSH pour Linux/Ubuntu
    
    Args:
        client: Client SSH paramiko connecté
    
    Retourne:
        dict: Dictionnaire avec clés days, hours, minutes, total_seconds ou None
    """
    try:
        output = execute_ssh_command(client, "cat /proc/uptime")
        if output:
            uptime_seconds = int(float(output.split()[0]))
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            minutes = (uptime_seconds % 3600) // 60
            
            return {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'total_seconds': uptime_seconds
            }
    except Exception as e:
        print(f"Erreur uptime: {e}")
    return None


def get_remote_cpu_linux(client):
    """
    Récupère l'utilisation CPU instantanée via SSH pour Linux/Ubuntu
    
    Utilise deux lectures de /proc/stat avec délai de 1 seconde pour calculer 
    l'utilisation instantanée (approche similaire à htop).
    
    Args:
        client: Client SSH paramiko connecté
    
    Retourne:
        dict: Dictionnaire avec clés percent, logical_count ou None
    """
    try:
        import time
        
        output = execute_ssh_command(client, "grep -c ^processor /proc/cpuinfo")
        logical_count = int(output.strip()) if output else 0
        
        # Première lecture de /proc/stat
        output1 = execute_ssh_command(client, "cat /proc/stat | head -1")
        time.sleep(1.0)  # Attendre 1 seconde pour avoir assez de variation dans les ticks
        # Deuxième lecture de /proc/stat
        output2 = execute_ssh_command(client, "cat /proc/stat | head -1")
        
        # Parser les deux lignes
        def parse_cpu_line(line):
            """
            Parse une ligne 'cpu' de /proc/stat
            Format: cpu user nice system idle iowait irq softirq steal guest guest_nice
            """
            fields = line.split()
            if len(fields) >= 5:
                user = int(fields[1])
                nice = int(fields[2])
                system = int(fields[3])
                idle = int(fields[4])
                iowait = int(fields[5]) if len(fields) > 5 else 0
                irq = int(fields[6]) if len(fields) > 6 else 0
                softirq = int(fields[7]) if len(fields) > 7 else 0
                steal = int(fields[8]) if len(fields) > 8 else 0
                
                # Ticks "busy" = tous les ticks sauf idle et guest
                busy = user + nice + system + iowait + irq + softirq + steal
                # Total de tous les ticks
                total = busy + idle
                
                return busy, idle, total
            return None
        
        result1 = parse_cpu_line(output1) if output1 else None
        result2 = parse_cpu_line(output2) if output2 else None
        
        if result1 and result2:
            busy1, idle1, total1 = result1
            busy2, idle2, total2 = result2
            
            # Calculer les deltas entre les deux lectures
            busy_delta = busy2 - busy1
            total_delta = total2 - total1
            
            # CPU% = (busy_delta / total_delta) * 100
            if total_delta > 0:
                cpu_percent = (busy_delta * 100.0) / total_delta
                # Limiter à 0-100%
                cpu_percent = max(0, min(100, cpu_percent))
            else:
                cpu_percent = 0.0
        else:
            cpu_percent = 0.0
        
        return {
            'percent': cpu_percent,
            'logical_count': logical_count
        }
    except Exception as e:
        print(f"Erreur CPU: {e}")
    return None


def get_remote_memory_linux(client):
    """
    Récupère la mémoire via SSH pour Linux/Ubuntu
    
    Args:
        client: Client SSH paramiko connecté
    
    Retourne:
        dict: Dictionnaire avec clés total, used, available, percent ou None
    """
    try:
        output = execute_ssh_command(client, "free -b | grep Mem")
        if output:
            parts = output.split()
            total = int(parts[1])
            used = int(parts[2])
            available = int(parts[6])
            percent = (used / total * 100) if total > 0 else 0
            
            return {
                'total': total,
                'used': used,
                'available': available,
                'percent': percent
            }
    except Exception as e:
        print(f"Erreur mémoire: {e}")
    return None


def get_remote_disk_linux(client):
    """
    Récupère l'utilisation disque via SSH pour Linux/Ubuntu
    
    Args:
        client: Client SSH paramiko connecté
    
    Retourne:
        list: Liste de dictionnaires avec infos disques ou None
    """
    try:
        output = execute_ssh_command(client, "df -B1 | tail -n +2")
        disks = []
        
        for line in output.split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 6:
                    disks.append({
                        'device': parts[0],
                        'total': int(parts[1]),
                        'used': int(parts[2]),
                        'free': int(parts[3]),
                        'percent': float(parts[4].rstrip('%')),
                        'mountpoint': parts[5]
                    })
        
        return disks if disks else None
    except Exception as e:
        print(f"Erreur disque: {e}")
    return None


# ============================================================================
# Windows Server Functions
# ============================================================================

def get_remote_uptime_windows(client):
    """
    Récupère l'uptime via SSH pour Windows Server (PowerShell)
    
    Args:
        client: Client SSH paramiko connecté
    
    Retourne:
        dict: Dictionnaire avec clés days, hours, minutes, total_seconds ou None
    """
    try:
        # Commande PowerShell retourne un objet TimeSpan avec Days, Hours, Minutes
        cmd = "powershell -Command \"(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime\""
        output = execute_ssh_command(client, cmd)
        
        if output:
            # Nettoyer les sauts de ligne Windows (\r)
            lines = output.replace('\r', '').strip().split('\n')
            days = hours = minutes = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Days') and ':' in line:
                    try:
                        days = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('Hours') and ':' in line:
                    try:
                        hours = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('Minutes') and ':' in line:
                    try:
                        minutes = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
            
            total_seconds = days * 86400 + hours * 3600 + minutes * 60
            return {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'total_seconds': total_seconds
            }
    except Exception as e:
        print(f"Erreur uptime Windows: {e}")
    
    return None


def get_remote_cpu_windows(client):
    """
    Récupère l'utilisation CPU via SSH pour Windows Server (PowerShell)
    
    Args:
        client: Client SSH paramiko connecté
    
    Retourne:
        dict: Dictionnaire avec clés percent, logical_count ou None
    """
    try:
        # Nombre de cœurs logiques (somme pour tous les processors)
        cmd = "powershell -Command \"(Get-WmiObject Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum\""
        output = execute_ssh_command(client, cmd)
        logical_count = int(output.strip().split('\r\n')[0].strip()) if output else 0
        
        # CPU percent (moyenne de tous les processeurs)
        # Note: Windows peut retourner des nombres avec virgule (locale française)
        cmd = "powershell -Command \"(Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average\""
        output = execute_ssh_command(client, cmd)
        cpu_str = output.strip().split('\r\n')[0].strip() if output else "0"
        # Remplacer virgule par point pour la conversion
        cpu_percent = float(cpu_str.replace(',', '.')) if cpu_str else 0
        
        return {
            'percent': cpu_percent,
            'logical_count': logical_count
        }
    except Exception as e:
        print(f"Erreur CPU Windows: {e}")
    return None


def get_remote_memory_windows(client):
    """
    Récupère la mémoire via SSH pour Windows Server (PowerShell)
    
    Args:
        client: Client SSH paramiko connecté
    
    Retourne:
        dict: Dictionnaire avec clés total, used, available, percent ou None
    """
    try:
        # Mémoire totale en bytes
        cmd = "powershell -Command \"(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory\""
        output = execute_ssh_command(client, cmd)
        total = int(output.strip()) if output else 0
        
        # Mémoire libre en KB
        cmd = "powershell -Command \"(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory\""
        output = execute_ssh_command(client, cmd)
        free_kb = int(output.strip()) if output else 0
        free = free_kb * 1024  # Convertir KB en bytes
        
        used = total - free if total > 0 else 0
        percent = (used / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'used': used,
            'available': free,
            'percent': percent
        }
    except Exception as e:
        print(f"Erreur mémoire Windows: {e}")
    return None


def get_remote_disk_windows(client):
    """
    Récupère l'utilisation disque via SSH pour Windows Server (wmic)
    
    Args:
        client: Client SSH paramiko connecté
    
    Retourne:
        list: Liste de dictionnaires avec infos disques ou None
    """
    try:
        # Utiliser wmic pour récupérer les disques logiques
        # Format: Node,FreeSpace,Name,Size
        cmd = "wmic logicaldisk get name,size,freespace /format:csv"
        output = execute_ssh_command(client, cmd)
        
        disks = []
        if output:
            lines = output.strip().split('\n')
            
            # Ignorer la première ligne (vide ou header)
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                try:
                    # Format: Node,FreeSpace,Name,Size (ex: DC01,515854061568,C:,536150536192)
                    parts = line.split(',')
                    if len(parts) >= 4:
                        # parts[0] = Node (nom du serveur)
                        # parts[1] = FreeSpace
                        # parts[2] = Name (le disque: C:, D:, etc.)
                        # parts[3] = Size (taille totale)
                        
                        name = parts[2].strip()
                        if not name:
                            continue
                        
                        try:
                            free = int(parts[1].strip()) if parts[1].strip() else 0
                            total = int(parts[3].strip()) if parts[3].strip() else 0
                        except ValueError:
                            continue
                        
                        used = total - free if total > 0 else 0
                        percent = (used / total * 100) if total > 0 else 0
                        
                        disks.append({
                            'device': name,
                            'total': total,
                            'used': used,
                            'free': free,
                            'percent': percent,
                            'mountpoint': name + "\\"
                        })
                except (ValueError, IndexError):
                    pass
        
        return disks if disks else None
    except Exception as e:
        print(f"Erreur disque Windows: {e}")
    return None


def display_remote_stats(client, server_type='ubuntu'):
    """
    Affiche les stats du serveur distant via SSH
    
    Args:
        client: Client SSH paramiko connecté
        server_type: Type de serveur ('ubuntu' ou 'windows')
    """
    print("\n" + "="*64)
    title = "STATISTIQUES - WINDOWS SERVER DISTANT" if server_type == 'windows' else "STATISTIQUES - UBUNTU/LINUX SERVER"
    print(title.center(64))
    print("="*64 + "\n")
    
    # Sélectionner les fonctions appropriées selon le type de serveur
    if server_type == 'windows':
        uptime = get_remote_uptime_windows(client)
        cpu = get_remote_cpu_windows(client)
        mem = get_remote_memory_windows(client)
        disks = get_remote_disk_windows(client)
    else:  # ubuntu/linux
        uptime = get_remote_uptime_linux(client)
        cpu = get_remote_cpu_linux(client)
        mem = get_remote_memory_linux(client)
        disks = get_remote_disk_linux(client)
    
    # Uptime
    if uptime:
        print(f"Uptime: {uptime['days']}j {uptime['hours']}h {uptime['minutes']}m")
    
    print()
    
    # CPU
    if cpu:
        print(f"CPU: {cpu['percent']:.1f}% utilisé")
        print(f"  Cœurs logiques: {cpu['logical_count']}")
    
    print()
    
    # RAM
    if mem:
        print(f"RAM: {mem['percent']:.1f}% utilisée")
        print(f"  Total: {format_bytes(mem['total'])}")
        print(f"  Utilisée: {format_bytes(mem['used'])}")
        print(f"  Disponible: {format_bytes(mem['available'])}")
    
    print()
    
    # Disks
    if disks:
        print("DISQUES:")
        print("-" * 64)
        print(f"{'Disque':<20} {'Total':<15} {'Utilisé':<15} {'Libre':<10}")
        print("-" * 64)
        
        for disk in disks:
            device = disk['device'][:20]
            total = format_bytes(disk['total'])[:15]
            used = format_bytes(disk['used'])[:15]
            free = format_bytes(disk['free'])[:10]
            
            print(f"{device:<20} {total:<15} {used:<15} {free:<10}")
    
    print()
    print("="*64)


# ============================================================================
# Menu Handlers
# ============================================================================

def check_remote_server(server_type='ubuntu'):
    """
    Vérifier les ressources du serveur distant via SSH
    
    Args:
        server_type: Type de serveur ('ubuntu' ou 'windows')
    """
    title = "WINDOWS SERVER" if server_type == 'windows' else "UBUNTU/LINUX SERVER"
    print("\n" + "-"*64)
    print(f"CHECK RESSOURCES {title}".center(64))
    print("-"*64)
    
    creds = get_ssh_credentials(server_type=server_type)
    client = ssh_connect(creds['hostname'], creds['username'], creds['password'], creds['port'])
    if client:
        display_remote_stats(client, server_type=server_type)
        client.close()
    else:
        print("Connexion échouée")
