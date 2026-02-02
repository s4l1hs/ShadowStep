import unittest
import os
from utils.shredder import secure_delete

class TestShredder(unittest.TestCase):
    def setUp(self):
        """Create a temporary file before each test."""
        self.test_file = "test_artifact.txt"
        with open(self.test_file, "w") as f:
            f.write("This is highly confidential data.")

    def test_secure_delete_exists(self):
        """File exists and gets deleted."""
        result = secure_delete(self.test_file, passes=1)
        self.assertTrue(result) # Function should return True
        self.assertFalse(os.path.exists(self.test_file)) # File should be gone

    def test_secure_delete_non_existent(self):
        """Attempt to delete a non-existent file."""
        result = secure_delete("nonexistent_file.txt")
        self.assertFalse(result) # Should return False

    def tearDown(self):
        """Cleanup after tests (remove if not deleted)."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

if __name__ == '__main__':
    unittest.main()