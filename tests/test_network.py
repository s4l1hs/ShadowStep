import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Proje kök dizinini path'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shadowstep.core.network_utils import NetworkManager

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
        # Mock Linux environment
        mock_system.return_value = "Linux"
        
        # --- KRİTİK DÜZELTME ---
        # Nesne setUp'da "Darwin" (Mac) olarak oluştu. 
        # Testin geçmesi için onu manuel olarak Linux'a çeviriyoruz:
        self.nm.os_type = "Linux"
        # -----------------------
        
        # Run function
        result = self.nm.change_mac("00:11:22:33:44:55")
        
        # Should succeed
        self.assertTrue(result)
        
        # Subprocess called 3 times? (down, set, up)
        self.assertEqual(mock_subprocess.call_count, 3)

    @patch('platform.system')
    def test_change_mac_windows_fail(self, mock_system):
        """Linux commands should not run on Windows."""
        mock_system.return_value = "Windows"
        
        # Testin tutarlılığı için burayı da Windows yapalım
        self.nm.os_type = "Windows"
        
        result = self.nm.change_mac("00:11:22:33:44:55")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()