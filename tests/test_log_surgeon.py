import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.log_surgeon import LogSurgeon

class TestLogSurgeon(unittest.TestCase):

    def setUp(self):
        self.surgeon = LogSurgeon()

    def test_linux_sanitize_real_file(self):
        """
        Create a real temporary file, write data, sanitize it, 
        and check if keywords are removed.
        """
        # Force Linux mode for this test
        self.surgeon.os_type = "Linux"
        
        # 1. Create a temp log file
        with tempfile.NamedTemporaryFile(delete=False, mode='w+') as tmp:
            tmp.write("Feb 02 12:00:01 host sshd[123]: Failed password for root from 192.168.1.5 port 22\n")
            tmp.write("Feb 02 12:00:02 host systemd: Started Session 1 of user root.\n")
            tmp.write("Feb 02 12:00:03 host sudo: admin : TTY=pts/0 ; PWD=/home ; USER=root ; COMMAND=/bin/bash\n")
            tmp_path = tmp.name

        try:
            # 2. Define keywords to remove
            keywords = ["192.168.1.5", "admin"]
            
            # 3. Run Sanitization
            result = self.surgeon.sanitize(tmp_path, keywords, inject_fake=True)
            
            # 4. Verify Result
            self.assertTrue(result)
            
            with open(tmp_path, 'r') as f:
                content = f.read()
            
            # Keywords should be gone
            self.assertNotIn("192.168.1.5", content)
            self.assertNotIn("admin", content)
            
            # Safe lines should remain
            self.assertIn("Started Session 1", content)
            
            # Decoy should be present (we check for CRON or systemd or kernel from templates)
            # Since it's random, we just check if line count is preserved (3 lines)
            lines = content.strip().split('\n')
            self.assertEqual(len(lines), 3)

        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @patch('subprocess.run')
    def test_windows_sanitize_command(self, mock_subprocess):
        """Test if correct PowerShell command is constructed on Windows."""
        # Force Windows mode
        self.surgeon.os_type = "Windows"
        
        # Mock sys.modules to pretend pywin32 is installed (to bypass check)
        with patch.dict(sys.modules, {'win32evtlog': MagicMock()}):
             # Mock inject_fake to do nothing (we only test PowerShell here)
            with patch.object(self.surgeon, '_inject_windows_decoy'):
                mock_subprocess.return_value.returncode = 0
                
                self.surgeon.sanitize("dummy", ["malware.exe", "10.0.0.1"], inject_fake=True)
                
                # Check if PowerShell was called
                self.assertTrue(mock_subprocess.called)
                
                # Check arguments
                args, _ = mock_subprocess.call_args
                command_str = args[0] # The list ["powershell", ...]
                
                # Verify our keywords are in the script
                self.assertIn("malware.exe", command_str[5]) 
                self.assertIn("10.0.0.1", command_str[5])

if __name__ == '__main__':
    unittest.main()