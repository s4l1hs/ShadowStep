import unittest
import os
from utils.shredder import secure_delete

class TestShredder(unittest.TestCase):
    def setUp(self):
        """Her testten önce geçici bir dosya oluştur."""
        self.test_file = "test_artifact.txt"
        with open(self.test_file, "w") as f:
            f.write("Bu çok gizli bir veridir.")

    def test_secure_delete_exists(self):
        """Dosya var ve siliniyor mu?"""
        result = secure_delete(self.test_file, passes=1)
        self.assertTrue(result) # Fonksiyon True dönmeli
        self.assertFalse(os.path.exists(self.test_file)) # Dosya artık olmamalı

    def test_secure_delete_non_existent(self):
        """Olmayan dosya silinmeye çalışılırsa?"""
        result = secure_delete("hayali_dosya.txt")
        self.assertFalse(result) # False dönmeli

    def tearDown(self):
        """Test sonrası temizlik (eğer silinememişse sil)."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

if __name__ == '__main__':
    unittest.main()