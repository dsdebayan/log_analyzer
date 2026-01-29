"""
Unit tests for the FileValidator class in utils/validator.py
"""
import pytest
from utils.validator import FileValidator


class TestFileValidatorExtension:
    """Tests for file extension validation"""

    def test_valid_log_file_extension(self):
        """Test that .log files are accepted"""
        ext = FileValidator._ext("application.log")
        assert ext == ".log"

    def test_valid_log_file_extension_uppercase(self):
        """Test that .LOG (uppercase) files are accepted"""
        ext = FileValidator._ext("APPLICATION.LOG")
        assert ext == ".log"

    def test_invalid_txt_extension(self):
        """Test that .txt files are rejected"""
        ext = FileValidator._ext("application.txt")
        assert ext != ".log"

    def test_invalid_json_extension(self):
        """Test that .json files are rejected"""
        ext = FileValidator._ext("data.json")
        assert ext != ".log"

    def test_file_without_extension(self):
        """Test that files without extension are rejected"""
        ext = FileValidator._ext("logfile")
        assert ext != ".log"


class TestFileValidatorValidation:
    """Tests for the main validation method"""

    def test_valid_log_file(self):
        """Test validation of a valid log file"""
        result, message = FileValidator.validate("application.log", 1024)
        assert result is True
        assert message is None

    def test_valid_log_file_uppercase(self):
        """Test validation of a valid .LOG file (uppercase)"""
        result, message = FileValidator.validate("APPLICATION.LOG", 1024)
        assert result is True
        assert message is None

    def test_invalid_extension_txt(self):
        """Test validation fails for .txt files"""
        result, message = FileValidator.validate("application.txt", 1024)
        assert result is False
        assert "Upload only valid file format" in message

    def test_invalid_extension_json(self):
        """Test validation fails for .json files"""
        result, message = FileValidator.validate("data.json", 1024)
        assert result is False
        assert "Upload only valid file format" in message

    def test_file_too_large(self):
        """Test validation fails for files exceeding size limit"""
        # 101 MB in bytes
        size = 101 * 1024 * 1024
        result, message = FileValidator.validate("application.log", size)
        assert result is False
        assert "File too large" in message

    def test_file_at_max_size(self):
        """Test validation passes for files at maximum size"""
        # Exactly 100 MB
        size = 100 * 1024 * 1024
        result, message = FileValidator.validate("application.log", size)
        assert result is True
        assert message is None

    def test_file_below_max_size(self):
        """Test validation passes for files below maximum size"""
        # 99 MB
        size = 99 * 1024 * 1024
        result, message = FileValidator.validate("application.log", size)
        assert result is True
        assert message is None

    def test_small_file(self):
        """Test validation of a small file"""
        result, message = FileValidator.validate("application.log", 100)
        assert result is True
        assert message is None

    def test_zero_size_file(self):
        """Test validation of a zero-size file"""
        result, message = FileValidator.validate("application.log", 0)
        assert result is True
        assert message is None

    def test_invalid_extension_with_large_file(self):
        """Test that extension validation happens before size validation"""
        size = 101 * 1024 * 1024
        result, message = FileValidator.validate("application.txt", size)
        assert result is False
        assert "Upload only valid file format" in message


class TestFileValidatorEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_filename_with_multiple_dots(self):
        """Test file with multiple dots in name"""
        result, message = FileValidator.validate("app.test.log", 1024)
        assert result is True
        assert message is None

    def test_filename_with_multiple_dots_wrong_extension(self):
        """Test file with multiple dots but wrong extension"""
        result, message = FileValidator.validate("app.log.txt", 1024)
        assert result is False
        assert "Upload only valid file format" in message

    def test_empty_filename(self):
        """Test validation with empty filename"""
        result, message = FileValidator.validate("", 1024)
        assert result is False
        assert "Upload only valid file format" in message

    def test_special_characters_in_filename(self):
        """Test filename with special characters"""
        result, message = FileValidator.validate("app-2024_01_29.log", 1024)
        assert result is True
        assert message is None

    def test_very_large_file(self):
        """Test validation with a very large file size"""
        size = 1000 * 1024 * 1024  # 1 GB
        result, message = FileValidator.validate("application.log", size)
        assert result is False
        assert "File too large" in message

    def test_max_size_constant(self):
        """Test that MAX_SIZE_BYTES constant is correctly set to 100 MB"""
        assert FileValidator.MAX_SIZE_BYTES == 100 * 1024 * 1024

    def test_allowed_extensions_set(self):
        """Test that ALLOWED_EXTENSIONS contains .log"""
        assert ".log" in FileValidator.ALLOWED_EXTENSIONS
