"""
Enhanced Settings Manager for DevSync
Handles all user settings, credentials, and GitHub authentication
"""

import os
import json
import webbrowser
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass, asdict
import base64
import hashlib
import platform

from PyQt6.QtCore import QSettings

# Optional dependencies
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


@dataclass
class UserSettings:
    """User configuration"""
    git_user: str = ""
    git_email: str = ""
    github_username: str = ""
    default_branch: str = "main"
    auto_merge: bool = True
    create_release: bool = True
    theme: str = "light"
    auto_refresh: bool = True
    auto_refresh_interval: int = 30


class SecureTokenManager:
    """Enhanced secure token storage with proper encryption"""
    
    def __init__(self):
        self.service_name = "devsync"
        self.username = "github_token"
        self.fallback_file = Path.home() / ".devsync" / "token.enc"
        self.fallback_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _get_machine_key(self) -> bytes:
        """Generate encryption key from machine ID"""
        machine_id = platform.node() + platform.machine()
        return hashlib.sha256(machine_id.encode()).digest()
    
    def _encrypt_token(self, token: str) -> bytes:
        """Encrypt token with Fernet"""
        if not CRYPTO_AVAILABLE:
            # Fallback to simple obfuscation
            return base64.b64encode(token.encode())
        
        key = base64.urlsafe_b64encode(self._get_machine_key())
        f = Fernet(key)
        return f.encrypt(token.encode())
    
    def _decrypt_token(self, encrypted: bytes) -> str:
        """Decrypt token"""
        if not CRYPTO_AVAILABLE:
            # Fallback from simple obfuscation
            return base64.b64decode(encrypted).decode()
        
        key = base64.urlsafe_b64encode(self._get_machine_key())
        f = Fernet(key)
        return f.decrypt(encrypted).decode()
    
    def save_token(self, token: str) -> bool:
        """Save token securely"""
        if not token:
            return False
        
        # Try keyring first (most secure)
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(self.service_name, self.username, token)
                print("✅ Token saved to system keyring")
                return True
            except Exception as e:
                print(f"⚠️  Keyring failed: {e}")
        
        # Fallback to encrypted file
        try:
            encrypted = self._encrypt_token(token)
            self.fallback_file.write_bytes(encrypted)
            
            # Hide file on Windows
            if platform.system() == "Windows":
                import subprocess
                subprocess.run(
                    ["attrib", "+h", str(self.fallback_file)], 
                    check=False,
                    capture_output=True
                )
            
            security_level = "encrypted" if CRYPTO_AVAILABLE else "obfuscated"
            print(f"✅ Token saved to file ({security_level})")
            return True
        except Exception as e:
            print(f"❌ Failed to save token: {e}")
            return False
    
    def get_token(self) -> Optional[str]:
        """Retrieve token"""
        # Try keyring first
        if KEYRING_AVAILABLE:
            try:
                token = keyring.get_password(self.service_name, self.username)
                if token:
                    print("🔑 Token loaded from keyring")
                    return token
            except Exception as e:
                print(f"⚠️  Keyring read failed: {e}")
        
        # Try encrypted file
        if self.fallback_file.exists():
            try:
                encrypted = self.fallback_file.read_bytes()
                token = self._decrypt_token(encrypted)
                print("🔑 Token loaded from file")
                return token
            except Exception as e:
                print(f"⚠️  File read failed: {e}")
        
        # Try environment variable
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            print("🔑 Token loaded from environment")
            return token
        
        return None
    
    def delete_token(self) -> bool:
        """Delete stored token"""
        success = False
        
        # Delete from keyring
        if KEYRING_AVAILABLE:
            try:
                keyring.delete_password(self.service_name, self.username)
                success = True
            except Exception:
                pass
        
        # Delete file
        if self.fallback_file.exists():
            try:
                self.fallback_file.unlink()
                success = True
            except Exception:
                pass
        
        return success


class SettingsManager:
    """Manage all application settings"""
    
    def __init__(self):
        self.qsettings = QSettings("DevSync", "DeploymentTool")
        self.config_file = Path.home() / ".devsync" / "config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.token_manager = SecureTokenManager()
        
    def load_settings(self) -> UserSettings:
        """Load user settings"""
        # Try JSON file first (more reliable than registry)
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text())
                return UserSettings(**data)
            except Exception as e:
                print(f"⚠️  Failed to load config: {e}")
        
        # Fallback to QSettings
        return UserSettings(
            git_user=self.qsettings.value("git_user", ""),
            git_email=self.qsettings.value("git_email", ""),
            github_username=self.qsettings.value("github_username", ""),
            default_branch=self.qsettings.value("default_branch", "main"),
            auto_merge=self.qsettings.value("auto_merge", True, bool),
            create_release=self.qsettings.value("create_release", True, bool),
            theme=self.qsettings.value("theme", "light"),
            auto_refresh=self.qsettings.value("auto_refresh", True, bool),
            auto_refresh_interval=self.qsettings.value("auto_refresh_interval", 30, int),
        )
    
    def save_settings(self, settings: UserSettings) -> bool:
        """Save user settings"""
        try:
            # Save to JSON file
            self.config_file.write_text(json.dumps(asdict(settings), indent=2))
            
            # Also save to QSettings for compatibility
            for key, value in asdict(settings).items():
                self.qsettings.setValue(key, value)
            
            self.qsettings.sync()
            print("✅ Settings saved successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to save settings: {e}")
            return False
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token"""
        return self.token_manager.get_token()
    
    def save_github_token(self, token: str) -> bool:
        """Save GitHub token"""
        return self.token_manager.save_token(token)
    
    def delete_github_token(self) -> bool:
        """Delete GitHub token"""
        return self.token_manager.delete_token()
    
    def get_all_settings(self) -> Dict:
        """Get all settings including token status"""
        settings = self.load_settings()
        return {
            **asdict(settings),
            "has_github_token": self.get_github_token() is not None,
            "token_storage": self._get_token_storage_location(),
        }
    
    def _get_token_storage_location(self) -> str:
        """Get where token is stored"""
        if KEYRING_AVAILABLE:
            try:
                token = keyring.get_password(self.token_manager.service_name, self.token_manager.username)
                if token:
                    return "System Keyring (Secure)"
            except Exception:
                pass
        
        if self.token_manager.fallback_file.exists():
            security = "Encrypted" if CRYPTO_AVAILABLE else "Obfuscated"
            return f"File ({security})"
        
        if os.environ.get("GITHUB_TOKEN"):
            return "Environment Variable"
        
        return "Not Stored"


class GitHubAuthHelper:
    """Helper for GitHub authentication"""
    
    DEVICE_FLOW_URL = "https://github.com/login/device/code"
    CLIENT_ID = "Ov23liIWmVQWVQWVQW"  # Public client ID for DevSync
    
    @staticmethod
    def open_token_creation_page():
        """Open GitHub token creation page"""
        url = "https://github.com/settings/tokens/new?description=DevSync&scopes=repo,workflow"
        webbrowser.open(url)
    
    @staticmethod
    def get_token_help_text() -> str:
        """Get help text for token creation"""
        return """
        📝 How to create a GitHub Personal Access Token:
        
        1. Click "Create Token" button below
        2. GitHub will open in your browser
        3. Set expiration (recommended: 90 days)
        4. Select scopes:
           ✓ repo (Full control of private repositories)
           ✓ workflow (Update GitHub Action workflows)
        5. Click "Generate token"
        6. Copy the token (you won't see it again!)
        7. Paste it here and click "Save"
        
        ⚠️  Keep your token secure! Never share it.
        """
