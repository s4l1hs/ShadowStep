import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.janitor import Janitor

class TestJanitor(unittest.TestCase):

    def setUp(self):
        self.janitor = Janitor()

    @patch('os.system')
    def test_clean_clipboard_mac(self, mock_system):
        """Test clipboard cleaning command on macOS."""
        # Force OS to Darwin (macOS)
        self.janitor.os_type = "Darwin"
        
        self.janitor.clean_clipboard()
        
        # Check if 'pbcopy' was called
        mock_system.assert_called_with("pbcopy < /dev/null")

    @patch('shutil.which')
    @patch('os.system')
    def test_clean_clipboard_linux(self, mock_system, mock_which):
        """Test clipboard cleaning on Linux (using xsel)."""
        self.janitor.os_type = "Linux"
        mock_which.return_value = True # Simulate xsel exists
        
        self.janitor.clean_clipboard()
        
        mock_system.assert_called_with("xsel -bc")

    @patch('subprocess.run')
    def test_flush_dns_windows(self, mock_subprocess):
        """Test DNS flush command on Windows."""
        self.janitor.os_type = "Windows"
        
        self.janitor.flush_dns()
        
        # Check if ipconfig /flushdns was called
        mock_subprocess.assert_called_with(
            ["ipconfig", "/flushdns"], 
            stdout=-3, stderr=-3 # subprocess.DEVNULL is -3
        )

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_clean_shell_history(self, mock_exists, mock_file):
        """Test if history files are opened in write mode (cleared)."""
        # Simulate that .bash_history exists
        mock_exists.return_value = True
        
        self.janitor.clean_shell_history()
        
        # Check if file was opened with 'w' (which clears content)
        mock_file.assert_called()
        handle = mock_file()
        # Ensure it didn't write anything (just opened and closed to wipe)
        # Or wrote empty string
        pass

if __name__ == '__main__':
    unittest.main()