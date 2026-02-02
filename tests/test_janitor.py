import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shadowstep.core.janitor import Janitor

class TestJanitor(unittest.TestCase):

    def setUp(self):
        self.janitor = Janitor()

    @patch('os.system')
    def test_clean_clipboard_mac(self, mock_system):
        """Test clipboard cleaning command on macOS."""
        self.janitor.os_type = "Darwin"
        self.janitor.clean_clipboard()
        mock_system.assert_called_with("pbcopy < /dev/null")

    @patch('shutil.which')
    @patch('os.system')
    def test_clean_clipboard_linux(self, mock_system, mock_which):
        """Test clipboard cleaning on Linux."""
        self.janitor.os_type = "Linux"
        mock_which.return_value = True 
        self.janitor.clean_clipboard()
        mock_system.assert_called_with("xsel -bc")

    @patch('subprocess.run')
    def test_flush_dns_windows(self, mock_subprocess):
        """Test DNS flush command on Windows."""
        self.janitor.os_type = "Windows"
        self.janitor.flush_dns()
        mock_subprocess.assert_called_with(
            ["ipconfig", "/flushdns"], 
            stdout=-3, stderr=-3 
        )

    # --- FIX IS HERE ---
    @patch('core.janitor.MemoryCleaner') # We patch where it is IMPORTED, not defined
    def test_nuke_memory_integration(self, MockMemoryCleaner):
        """Test if Janitor correctly triggers MemoryCleaner methods."""
        # Setup mock instance
        mock_instance = MockMemoryCleaner.return_value
        
        # Re-init janitor so it picks up the mocked MemoryCleaner
        janitor = Janitor() 
        janitor.nuke_memory()
        
        # Verify all 3 memory cleaning steps were called
        mock_instance.drop_caches.assert_called_once()
        mock_instance.wipe_free_ram.assert_called_once()
        mock_instance.clear_swap.assert_called_once()

    @patch('subprocess.run')
    def test_wipe_logs_windows(self, mock_subprocess):
        """Test aggressive log wiping on Windows."""
        self.janitor.os_type = "Windows"
        
        # Mock getting log list
        with patch('subprocess.check_output', return_value="Log1\nLog2"):
            self.janitor.wipe_logs()
            
            # Should run 'wevtutil cl' for each log
            self.assertTrue(mock_subprocess.call_count >= 2)

if __name__ == '__main__':
    unittest.main()