import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path so modules can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.network_utils import NetworkManager

class TestNetworkManager(unittest.TestCase):

    def setUp(self):
        """Run before each test."""
        self.nm = NetworkManager(interface="eth0")

    def test_generate_mac_format(self):
        """Generated MAC address matches XX:XX:XX:XX:XX:XX format."""
        mac = self.nm.generate_mac()
        self.assertEqual(len(mac.split(':')), 6)
        self.assertEqual(len(mac), 17)

    @patch('subprocess.run')
    @patch('platform.system')
    def test_change_mac_linux(self, mock_system, mock_subprocess):
        """On Linux, MAC change calls subprocess."""
        # Mock Linux environment
        mock_system.return_value = "Linux"
        
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
        result = self.nm.change_mac("00:11:22:33:44:55")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()