import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
from pathlib import Path

# Add parent directory to path to import devsync_gui
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock PyQt6 before importing devsync_gui since we can't run GUI tests in CI easily
sys.modules['PyQt6'] = MagicMock()
sys.modules['PyQt6.QtWidgets'] = MagicMock()
sys.modules['PyQt6.QtCore'] = MagicMock()
sys.modules['PyQt6.QtGui'] = MagicMock()

from devsync_gui import Version, VersionManager, TokenManager

class TestVersion(unittest.TestCase):
    def test_version_parsing(self):
        v = Version.parse("1.0.0")
        self.assertEqual(str(v), "1.0.0")
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 0)
        self.assertEqual(v.patch, 0)
        self.assertEqual(v.suffix, "")

    def test_version_parsing_with_suffix(self):
        v = Version.parse("1.2.3rc1")
        self.assertEqual(str(v), "1.2.3rc1")
        self.assertEqual(v.suffix, "rc1")

    def test_version_parsing_custom_suffix(self):
        v = Version.parse("1.0.2c")
        self.assertEqual(str(v), "1.0.2c")
        self.assertEqual(v.suffix, "c")
        
        v2 = Version.parse("2.0.0-beta")
        self.assertEqual(str(v2), "2.0.0-beta")
        self.assertEqual(v2.suffix, "-beta")

    def test_version_bumping(self):
        v = Version(1, 0, 0)
        
        v_patch = v.bump("patch")
        self.assertEqual(str(v_patch), "1.0.1")
        
        v_minor = v.bump("minor")
        self.assertEqual(str(v_minor), "1.1.0")
        
        v_major = v.bump("major")
        self.assertEqual(str(v_major), "2.0.0")

class TestTokenManager(unittest.TestCase):
    def setUp(self):
        self.token_mgr = TokenManager()
        self.token_mgr.fallback_file = Path("test_token_file")

    def tearDown(self):
        if self.token_mgr.fallback_file.exists():
            os.remove(self.token_mgr.fallback_file)

    @patch('devsync_gui.KEYRING_AVAILABLE', True)
    @patch('keyring.set_password')
    @patch('keyring.get_password')
    def test_keyring_storage(self, mock_get, mock_set):
        mock_get.return_value = "secret_token"
        
        # Test Save
        self.token_mgr.save_token("secret_token")
        mock_set.assert_called_with("devsync", "github_token", "secret_token")
        
        # Test Get
        token = self.token_mgr.get_token()
        self.assertEqual(token, "secret_token")

    @patch('devsync_gui.KEYRING_AVAILABLE', False)
    def test_fallback_storage(self):
        # Test Save
        self.token_mgr.save_token("fallback_token")
        self.assertTrue(self.token_mgr.fallback_file.exists())
        
        # Test Get
        token = self.token_mgr.get_token()
        self.assertEqual(token, "fallback_token")

class TestVersionManager(unittest.TestCase):
    def setUp(self):
        self.vm = VersionManager()
        self.vm.version_file = Path("test_version.txt")
        self.vm.history_file = Path("test_history.json")

    def tearDown(self):
        if self.vm.version_file.exists():
            os.remove(self.vm.version_file)
        if self.vm.history_file.exists():
            os.remove(self.vm.history_file)

    def test_read_write_version(self):
        v = Version(1, 0, 0)
        self.vm.write_version(v)
        
        read_v = self.vm.read_version()
        self.assertEqual(str(read_v), "1.0.0")

if __name__ == '__main__':
    unittest.main()
