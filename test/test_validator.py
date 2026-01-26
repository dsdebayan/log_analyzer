import unittest
from utils.validator import FileValidator


class TestFileValidator(unittest.TestCase):
    """Test cases for FileValidator"""

    def test_valid_log_file(self):
        """Test validation of valid .log file with normal size"""
        ok, msg = FileValidator.validate("test.log", 1024)
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_invalid_file_extension_txt(self):
        """Test validation rejects .txt files"""
        ok, msg = FileValidator.validate("test.txt", 1024)
        self.assertFalse(ok)
        self.assertEqual(msg, "Upload only valid file format (.log)")

    def test_invalid_file_extension_pdf(self):
        """Test validation rejects .pdf files"""
        ok, msg = FileValidator.validate("test.pdf", 1024)
        self.assertFalse(ok)
        self.assertEqual(msg, "Upload only valid file format (.log)")

    def test_invalid_file_extension_no_extension(self):
        """Test validation rejects files without extension"""
        ok, msg = FileValidator.validate("test", 1024)
        self.assertFalse(ok)
        self.assertEqual(msg, "Upload only valid file format (.log)")

    def test_file_size_exceeds_limit(self):
        """Test validation rejects files exceeding 100 MB"""
        size_over_limit = FileValidator.MAX_SIZE_BYTES + 1
        ok, msg = FileValidator.validate("test.log", size_over_limit)
        self.assertFalse(ok)
        self.assertIn("File too large", msg)

    def test_file_size_at_limit(self):
        """Test validation accepts files exactly at 100 MB limit"""
        ok, msg = FileValidator.validate("test.log", FileValidator.MAX_SIZE_BYTES)
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_file_size_below_limit(self):
        """Test validation accepts files below limit"""
        ok, msg = FileValidator.validate("test.log", FileValidator.MAX_SIZE_BYTES - 1)
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_zero_byte_file(self):
        """Test validation accepts zero byte .log files"""
        ok, msg = FileValidator.validate("test.log", 0)
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_case_insensitive_extension(self):
        """Test validation is case-insensitive for extensions"""
        ok, msg = FileValidator.validate("test.LOG", 1024)
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_case_insensitive_extension_upper(self):
        """Test validation accepts uppercase extensions"""
        ok, msg = FileValidator.validate("TEST.LOG", 5000)
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_invalid_extension_uppercase(self):
        """Test validation rejects uppercase invalid extensions"""
        ok, msg = FileValidator.validate("test.TXT", 1024)
        self.assertFalse(ok)
        self.assertEqual(msg, "Upload only valid file format (.log)")


class TestFileValidatorEdgeCases(unittest.TestCase):
    """Edge case tests for FileValidator"""

    def test_large_filename(self):
        """Test validation with very long filename"""
        long_name = "a" * 255 + ".log"
        ok, msg = FileValidator.validate(long_name, 1024)
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_filename_with_multiple_dots(self):
        """Test validation with multiple dots in filename"""
        ok, msg = FileValidator.validate("test.backup.log", 1024)
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_filename_with_spaces(self):
        """Test validation with spaces in filename"""
        ok, msg = FileValidator.validate("my test file.log", 1024)
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_filename_with_special_characters(self):
        """Test validation with special characters in filename"""
        ok, msg = FileValidator.validate("test@#$%.log", 1024)
        self.assertTrue(ok)
        self.assertIsNone(msg)


if __name__ == '__main__':
    unittest.main()
