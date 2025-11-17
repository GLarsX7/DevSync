#!/usr/bin/env python3
"""
Unit tests for Deploy Automation Tool
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from deploy import Version, VersionType, VersionManager


class TestVersion:
    """Test cases for Version class"""
    
    def test_parse_stable_version(self):
        """Test parsing stable versions"""
        v = Version.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.suffix_type == VersionType.STABLE
        assert str(v) == "1.2.3"
    
    def test_parse_alpha_version(self):
        """Test parsing alpha versions"""
        v = Version.parse("1.0.0a")
        assert v.major == 1
        assert v.minor == 0
        assert v.patch == 0
        assert v.suffix_type == VersionType.ALPHA
        assert str(v) == "1.0.0a0"
    
    def test_parse_beta_version(self):
        """Test parsing beta versions"""
        v = Version.parse("2.1.0b")
        assert v.major == 2
        assert v.minor == 1
        assert v.patch == 0
        assert v.suffix_type == VersionType.BETA
        assert str(v) == "2.1.0b0"
    
    def test_parse_rc_version(self):
        """Test parsing release candidate versions"""
        v = Version.parse("3.0.0rc")
        assert v.major == 3
        assert v.minor == 0
        assert v.patch == 0
        assert v.suffix_type == VersionType.RC
        assert str(v) == "3.0.0rc0"
    
    def test_parse_invalid_version(self):
        """Test that invalid versions raise ValueError"""
        with pytest.raises(ValueError):
            Version.parse("invalid")
        
        with pytest.raises(ValueError):
            Version.parse("1.2")
        
        with pytest.raises(ValueError):
            Version.parse("1.2.3.4")
    
    def test_bump_stable_patch(self):
        """Test bumping stable version (patch)"""
        v = Version.parse("1.0.0")
        v_next = v.bump("patch")
        assert str(v_next) == "1.0.1"
    
    def test_bump_stable_minor(self):
        """Test bumping stable version (minor)"""
        v = Version.parse("1.0.5")
        v_next = v.bump("minor")
        assert str(v_next) == "1.1.0"
    
    def test_bump_stable_major(self):
        """Test bumping stable version (major)"""
        v = Version.parse("1.2.3")
        v_next = v.bump("major")
        assert str(v_next) == "2.0.0"
    
    def test_bump_alpha_to_beta(self):
        """Test bumping from alpha to beta"""
        v = Version.parse("1.0.0a")
        v_next = v.bump()
        assert str(v_next) == "1.0.0b0"
    
    def test_bump_beta_to_rc(self):
        """Test bumping from beta to release candidate"""
        v = Version.parse("1.0.0b")
        v_next = v.bump()
        assert str(v_next) == "1.0.0rc0"
    
    def test_bump_rc_to_stable(self):
        """Test bumping from release candidate to stable"""
        v = Version.parse("1.0.0rc")
        v_next = v.bump()
        assert str(v_next) == "1.0.0"
    
    def test_version_sequence(self):
        """Test complete version sequence"""
        versions = [
            "1.0.0a",
            "1.0.0b",
            "1.0.0rc",
            "1.0.0",
            "1.0.1"
        ]
        
        current = Version.parse(versions[0])
        for expected in versions[1:]:
            current = current.bump("patch" if current.suffix_type == VersionType.STABLE else None)
            assert str(current) == expected


class TestVersionManager:
    """Test cases for VersionManager class"""
    
    def test_read_write_version(self, tmp_path):
        """Test reading and writing version file"""
        version_file = tmp_path / "Version.txt"
        manager = VersionManager(version_file)
        
        # Write version
        v = Version(1, 2, 3)
        manager.write_version(v)
        
        # Read version
        v_read = manager.read_version()
        assert str(v_read) == "1.2.3"
    
    def test_bump_version_file(self, tmp_path):
        """Test bumping version in file"""
        version_file = tmp_path / "Version.txt"
        version_file.write_text("1.0.0")
        
        manager = VersionManager(version_file)
        new_version = manager.bump_version("patch")
        
        assert str(new_version) == "1.0.1"
        assert version_file.read_text().strip() == "1.0.1"
    
    def test_create_version_file_if_missing(self, tmp_path):
        """Test that version file is created if missing"""
        version_file = tmp_path / "Version.txt"
        manager = VersionManager(version_file)
        
        v = manager.read_version()
        assert str(v) == "0.1.0"
        assert version_file.exists()


class TestVersionLogic:
    """Test cases for version logic and edge cases"""
    
    def test_zero_version(self):
        """Test handling of 0.0.0 version"""
        v = Version.parse("0.0.0")
        v_next = v.bump("patch")
        assert str(v_next) == "0.0.1"
    
    def test_large_numbers(self):
        """Test handling of large version numbers"""
        v = Version.parse("999.999.999")
        assert v.major == 999
        assert v.minor == 999
        assert v.patch == 999
    
    def test_version_comparison(self):
        """Test version comparison logic"""
        v1 = Version.parse("1.0.0")
        v2 = Version.parse("1.0.1")
        v3 = Version.parse("1.1.0")
        v4 = Version.parse("2.0.0")
        
        # Basic numerical comparison
        assert (v1.major, v1.minor, v1.patch) < (v2.major, v2.minor, v2.patch)
        assert (v2.major, v2.minor, v2.patch) < (v3.major, v3.minor, v3.patch)
        assert (v3.major, v3.minor, v3.patch) < (v4.major, v4.minor, v4.patch)
    
    def test_prerelease_versions(self):
        """Test pre-release version handling"""
        versions = [
            "1.0.0a",
            "1.0.0b",
            "1.0.0rc",
            "1.0.0"
        ]
        
        for i in range(len(versions) - 1):
            v_current = Version.parse(versions[i])
            v_next = Version.parse(versions[i + 1])
            
            # Verify that bumping moves to next in sequence
            bumped = v_current.bump()
            assert str(bumped) == versions[i + 1]


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_bump_type(self):
        """Test invalid bump type handling"""
        v = Version.parse("1.0.0")
        # Should default to patch for unknown bump types
        v_next = v.bump("invalid")
        assert str(v_next) == "1.0.1"
    
    def test_whitespace_handling(self):
        """Test version parsing with whitespace"""
        v = Version.parse("  1.0.0  \n")
        assert str(v) == "1.0.0"
    
    def test_version_string_formats(self):
        """Test various version string formats"""
        valid_formats = [
            "0.0.1",
            "1.0.0",
            "10.20.30",
            "1.0.0a",
            "1.0.0b",
            "1.0.0rc",
            "2.3.4a0",
            "2.3.4b5",
            "2.3.4rc99"
        ]
        
        for fmt in valid_formats:
            v = Version.parse(fmt)
            assert v is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])