import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shadowstep.core.memory_cleaner import MemoryCleaner

class TestMemoryCleaner(unittest.TestCase):

    def setUp(self):
        self.cleaner = MemoryCleaner()

    @patch('core.memory_cleaner.psutil')
    def test_wipe_free_ram_success(self, mock_psutil):
        """Test RAM wipe logic without actually filling RAM."""
        # 1. Mock virtual_memory to simulate 1GB free RAM
        mock_mem = MagicMock()
        mock_mem.available = 1024 * 1024 * 1024 # 1 GB
        mock_psutil.virtual_memory.return_value = mock_mem
        
        # 2. Run the function
        result = self.cleaner.wipe_free_ram()
        
        # 3. Assertions
        self.assertTrue(result)
        mock_psutil.virtual_memory.assert_called_once()

    @patch('core.memory_cleaner.psutil')
    def test_wipe_free_ram_low_memory(self, mock_psutil):
        """Test graceful exit if free RAM is too low."""
        # Simulate only 100MB free (Buffer is 500MB, so this should fail safely)
        mock_mem = MagicMock()
        mock_mem.available = 100 * 1024 * 1024 
        mock_psutil.virtual_memory.return_value = mock_mem
        
        result = self.cleaner.wipe_free_ram()
        
        self.assertFalse(result)

    @patch('os.system')
    def test_drop_caches_linux(self, mock_system):
        """Test Linux cache drop command."""
        self.cleaner.os_type = "Linux"
        
        result = self.cleaner.drop_caches()
        
        self.assertTrue(result)
        mock_system.assert_called_with("sync; echo 3 > /proc/sys/vm/drop_caches")

    @patch('os.system')
    def test_drop_caches_macos(self, mock_system):
        """Test macOS purge command."""
        self.cleaner.os_type = "Darwin"
        
        result = self.cleaner.drop_caches()
        
        self.assertTrue(result)
        mock_system.assert_called_with("sync && sudo purge")

    @patch('subprocess.run')
    def test_clear_swap_linux(self, mock_subprocess):
        """Test Linux swap flush sequence."""
        self.cleaner.os_type = "Linux"
        
        result = self.cleaner.clear_swap()
        
        self.assertTrue(result)
        # Check calls (swapoff then swapon)
        self.assertEqual(mock_subprocess.call_count, 2)

if __name__ == '__main__':
    unittest.main()