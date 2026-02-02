import argparse
import platform
import sys
import os
from utils.colors import Fore, Style
from core.forensic_view import TimeStomper
from core.network_utils import NetworkManager
from utils.shredder import secure_delete
from utils.logger import log
from config import config
from core.janitor import Janitor

def print_banner():
    """Hacker-style ASCII Banner (Corrected)"""
    banner = f"""
{Fore.CYAN}
   _____ __               __               _____ __
  / ___// /_  ____ ______/ /___ _      __ / ___// /____  ____
  \__ \/ __ \/ __ `/ __  / __ \ | /| / / \__ \/ __/ _ \/ __ \\
 ___/ / / / / /_/ / /_/ / /_/ / |/ |/ / ___/ / /_/  __/ /_/ /
/____/_/ /_/\__,_/\__,_/\____/|__/|__/ /____/\__/\___/ .___/ 
                                                    /_/      
{Fore.WHITE}   Version: {config['app']['version']} | {config['app']['environment']}
    """
    print(banner)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="ShadowStep: Advanced System Artifact & Metadata Management Suite",
        epilog="Use with caution. Authorized use only."
    )

    # Primary command group (use mutually exclusive group instead of subparsers)
    group = parser.add_mutually_exclusive_group(required=True)
    
    # Module 1: Secure Delete (Shredder)
    group.add_argument('--shred', '-s', metavar='FILE', help='Securely delete a file (DoD 5220.22-M)')
    
    # Module 2: Timestomp (Metadata)
    group.add_argument('--timestomp', '-ts', metavar='TARGET', help='Change target file timestamps')
    
    # Module 3: Network (Spoof)
    group.add_argument('--spoof', '-m', action='store_true', help='Change the MAC address of a network interface')

    # Helper arguments
    parser.add_argument('--ref', '-r', metavar='FILE', help='Reference file to copy timestamps from')
    parser.add_argument('--passes', '-p', type=int, default=3, help='Number of shredder passes (Default: 3)')
    parser.add_argument('--interface', '-i', default='eth0', help='Network interface to operate on (Default: eth0)')
    parser.add_argument('--mac', metavar='MAC', help='Manual MAC address to set (e.g., 00:11:22:33:44:55)')
    # Modül 4: Janitor (Sistem Temizliği)
    group.add_argument('--clean', '-c', action='store_true', help='Clear system traces (History, Clipboard, DNS)')

    args = parser.parse_args()

    # --- Execution Logic ---

    # 1. SHREDDER MODULE
    if args.shred:
        if not os.path.exists(args.shred):
            log.error(f"File not found for deletion: {args.shred}")
            sys.exit(1)
            
        confirm = input(f"{Fore.RED}[!] {args.shred} will be permanently deleted. Confirm? (y/n): {Style.RESET_ALL}")
        if confirm.lower() == 'y':
            secure_delete(args.shred, passes=args.passes)
        else:
            log.warning("Operation canceled by the user.")

    # 2. TIMESTOMPER MODULE
    elif args.timestomp:
        ts = TimeStomper()
        
        if not args.ref:
            log.error("A reference file (--ref) is required for timestomp.")
            log.info("Example: shadowstep --ts malware.exe --ref C:\\Windows\\System32\\calc.exe")
            sys.exit(1)
            
        ts.stomp(target_path=args.timestomp, ref_path=args.ref)

    # 3. NETWORK MODULE
    elif args.spoof:
        nm = NetworkManager(interface=args.interface)
        
        new_mac = args.mac
        if not new_mac:
            # If not provided, generate automatically
            new_mac = nm.generate_mac()
            log.info(f"Generated random MAC: {new_mac}")
            
        nm.change_mac(new_mac)
    # 4. JANITOR MODÜLÜ
    elif args.clean:
        janitor = Janitor()
        
        log.info("System cleaning started...")
        
        # 1. Clipboard Cleaning
        janitor.clean_clipboard()
        
        # 2. Shell History
        janitor.clean_shell_history()
        
        # 3. DNS Cache
        janitor.flush_dns()
        
        # 4. Log Cleaning (Automated only on Windows for now)
        if platform.system() == "Windows":
            confirm = input(f"{Fore.RED}[!] Windows Event Logs will be deleted. This action is irreversible. Continue? (y/n): {Style.RESET_ALL}")
            if confirm.lower() == 'y':
                janitor.wipe_logs()
        
        log.info(f"{Fore.GREEN}Cleaning completed. Traces removed.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Operation interrupted.{Style.RESET_ALL}")
        sys.exit(0)