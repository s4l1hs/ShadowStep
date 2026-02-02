import os
import json
import random
import subprocess
import platform
from shadowstep.utils.logger import log

class NetworkManager:
    """
    Manages network interfaces and identity (MAC/Hostname).
    Uses 'ip' on Linux and 'getmac' on Windows.
    """
    
    def __init__(self, interface="eth0"):
        self.interface = interface
        self.os_type = platform.system()
        self.oui_list = self._load_oui_list()

    def _load_oui_list(self):
        """Load the vendor list from data/oui_list.json."""
        # Note: resolve paths dynamically to avoid packaging issues
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_path, 'data', 'oui_list.json')
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                return data.get('vendors', []) # May vary by JSON schema
        except FileNotFoundError:
            log.warning("OUI list not found; a random MAC will be generated.")
            return []

    def generate_mac(self, vendor_filter=None):
        """
        Generate a valid and realistic MAC address.
        vendor_filter: filters like 'Intel', 'Realtek'.
        """
        prefix = [0x00, 0x16, 0x3E] # Default (Xen Source)
        
        if self.oui_list:
            # Pick a random vendor (customize based on your JSON schema)
            # Placeholder for now
            pass 

        # Randomize the last 3 octets
        suffix = [random.randint(0x00, 0xff) for _ in range(3)]
        mac = prefix + suffix
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def change_mac(self, new_mac):
        """Change MAC address (Linux-focused)."""
        if self.os_type != "Linux":
            log.error("MAC changing is currently supported on Linux only.")
            return False

        log.info(f"[{self.interface}] Changing MAC address -> {new_mac}")
        
        try:
            # 1. Bring interface down
            subprocess.run(["ip", "link", "set", "dev", self.interface, "down"], check=True)
            # 2. Change MAC
            subprocess.run(["ip", "link", "set", "dev", self.interface, "address", new_mac], check=True)
            # 3. Bring interface up
            subprocess.run(["ip", "link", "set", "dev", self.interface, "up"], check=True)
            
            log.info("MAC address changed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            log.error(f"MAC change error: {e}")
            return False
        except PermissionError:
            log.error("Root privileges are required for this operation.")
            return False