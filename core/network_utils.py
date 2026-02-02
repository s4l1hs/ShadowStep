import os
import json
import random
import subprocess
import platform
from utils.logger import log

class NetworkManager:
    """
    Ağ arayüzlerini ve kimlik bilgilerini (MAC/Hostname) yönetir.
    Linux üzerinde 'ip' komutlarını, Windows üzerinde 'getmac' kullanır.
    """
    
    def __init__(self, interface="eth0"):
        self.interface = interface
        self.os_type = platform.system()
        self.oui_list = self._load_oui_list()

    def _load_oui_list(self):
        """data/oui_list.json dosyasından üretici listesini çeker."""
        # Not: Paketlenmiş uygulamada path sorunu yaşamamak için dinamik path bulma
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_path, 'data', 'oui_list.json')
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                return data.get('vendors', []) # JSON yapısına göre değişebilir
        except FileNotFoundError:
            log.warning("OUI listesi bulunamadı, rastgele MAC üretilecek.")
            return []

    def generate_mac(self, vendor_filter=None):
        """
        Geçerli ve gerçekçi bir MAC adresi üretir.
        vendor_filter: 'Intel', 'Realtek' gibi filtreler.
        """
        prefix = [0x00, 0x16, 0x3E] # Varsayılan (Xen Source)
        
        if self.oui_list:
            # Listeden rastgele bir vendor seç (Burayı JSON yapına göre özelleştir)
            # Şimdilik basit random mantığı
            pass 

        # Son 3 okteti rastgele üret
        suffix = [random.randint(0x00, 0xff) for _ in range(3)]
        mac = prefix + suffix
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def change_mac(self, new_mac):
        """MAC adresini değiştirir (Linux odaklı)."""
        if self.os_type != "Linux":
            log.error("MAC değiştirme şu an sadece Linux'ta destekleniyor.")
            return False

        log.info(f"[{self.interface}] MAC adresi değiştiriliyor -> {new_mac}")
        
        try:
            # 1. Arayüzü kapat
            subprocess.run(["ip", "link", "set", "dev", self.interface, "down"], check=True)
            # 2. MAC'i değiştir
            subprocess.run(["ip", "link", "set", "dev", self.interface, "address", new_mac], check=True)
            # 3. Arayüzü aç
            subprocess.run(["ip", "link", "set", "dev", self.interface, "up"], check=True)
            
            log.info("MAC adresi başarıyla değiştirildi.")
            return True
        except subprocess.CalledProcessError as e:
            log.error(f"MAC değiştirme hatası: {e}")
            return False
        except PermissionError:
            log.error("Bu işlem için ROOT yetkisi gerekir.")
            return False