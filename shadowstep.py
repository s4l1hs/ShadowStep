#!/usr/bin/env python3
import argparse
import sys
import os
from colorama import Fore, Style
from core.forensic_view import TimeStomper
from core.network_utils import NetworkManager
from utils.shredder import secure_delete
from utils.logger import log
from config import config

def print_banner():
    """Hacker-style ASCII Banner"""
    banner = f"""
{Fore.CYAN}
   _____ __               __          __  __  __
  / ___// /_  ____ ______/ /___ _      / / / / /___  ____ 
  \__ \/ __ \/ __ `/ __  / __ \ | /| / / / / / __ \/ __ \\
 ___/ / / / / /_/ / /_/ / /_/ / |/ |/ / /_/ / /_/ / /_/ /
/____/_/ /_/\__,_/\__,_/\____/|__/|__/\____/ .___/\____/ 
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

    # Ana komut grupları (Subparsers yerine mutually exclusive group kullanıyoruz)
    group = parser.add_mutually_exclusive_group(required=True)
    
    # 1. Modül: Secure Delete (Shredder)
    group.add_argument('--shred', '-s', metavar='FILE', help='Dosyayı güvenli şekilde sil (DoD 5220.22-M)')
    
    # 2. Modül: Timestomp (Metadata)
    group.add_argument('--timestomp', '-ts', metavar='TARGET', help='Hedef dosyanın zaman damgalarını değiştir')
    
    # 3. Modül: Network (Spoof)
    group.add_argument('--spoof', '-m', action='store_true', help='Ağ arayüzünün MAC adresini değiştir')

    # Yardımcı Argümanlar
    parser.add_argument('--ref', '-r', metavar='FILE', help='Timestomp için referans alınacak güvenli dosya')
    parser.add_argument('--passes', '-p', type=int, default=3, help='Shredder için geçiş sayısı (Varsayılan: 3)')
    parser.add_argument('--interface', '-i', default='eth0', help='İşlem yapılacak ağ arayüzü (Varsayılan: eth0)')
    parser.add_argument('--mac', metavar='MAC', help='Manuel atanacak MAC adresi (Örn: 00:11:22:33:44:55)')

    args = parser.parse_args()

    # --- İşlem Mantığı ---

    # 1. SHREDDER MODÜLÜ
    if args.shred:
        if not os.path.exists(args.shred):
            log.error(f"Silinecek dosya bulunamadı: {args.shred}")
            sys.exit(1)
            
        confirm = input(f"{Fore.RED}[!] {args.shred} kalıcı olarak silinecek. Onaylıyor musun? (y/n): {Style.RESET_ALL}")
        if confirm.lower() == 'y':
            secure_delete(args.shred, passes=args.passes)
        else:
            log.warning("İşlem kullanıcı tarafından iptal edildi.")

    # 2. TIMESTOMPER MODÜLÜ
    elif args.timestomp:
        ts = TimeStomper()
        
        if not args.ref:
            log.error("Timestomp işlemi için referans dosya (--ref) belirtmelisiniz.")
            log.info("Örnek: shadowstep --ts malware.exe --ref C:\\Windows\\System32\\calc.exe")
            sys.exit(1)
            
        ts.stomp(target_path=args.timestomp, ref_path=args.ref)

    # 3. NETWORK MODÜLÜ
    elif args.spoof:
        nm = NetworkManager(interface=args.interface)
        
        new_mac = args.mac
        if not new_mac:
            # Eğer manuel verilmediyse otomatik üret
            new_mac = nm.generate_mac()
            log.info(f"Rastgele MAC üretildi: {new_mac}")
            
        nm.change_mac(new_mac)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Operasyon durduruldu.{Style.RESET_ALL}")
        sys.exit(0)