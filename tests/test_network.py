# tests/test_network.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Proje kök dizinini path'e ekle ki modülleri bulabilsin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.network_utils import NetworkManager

class TestNetworkManager(unittest.TestCase):

    def setUp(self):
        """Her testten önce çalışır."""
        self.nm = NetworkManager(interface="eth0")

    def test_generate_mac_format(self):
        """Üretilen MAC adresi XX:XX:XX:XX:XX:XX formatında mı?"""
        mac = self.nm.generate_mac()
        self.assertEqual(len(mac.split(':')), 6)
        self.assertEqual(len(mac), 17)

    @patch('subprocess.run')
    @patch('platform.system')
    def test_change_mac_linux(self, mock_system, mock_subprocess):
        """Linux üzerinde MAC değişimi subprocess çağırıyor mu?"""
        # Ortamı Linux gibi göster
        mock_system.return_value = "Linux"
        
        # Fonksiyonu çalıştır
        result = self.nm.change_mac("00:11:22:33:44:55")
        
        # Başarılı dönmeli
        self.assertTrue(result)
        
        # Subprocess 3 kere çağrıldı mı? (down, set, up)
        self.assertEqual(mock_subprocess.call_count, 3)

    @patch('platform.system')
    def test_change_mac_windows_fail(self, mock_system):
        """Windows'ta Linux komutları çalışmamalı."""
        mock_system.return_value = "Windows"
        result = self.nm.change_mac("00:11:22:33:44:55")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()