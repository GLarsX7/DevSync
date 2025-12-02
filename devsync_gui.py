#!/usr/bin/env python3
"""
DevSync GUI - Single-File Desktop Application
Professional deployment automation with visual interface
"""

import sys
import os
import re
import subprocess
import time
import json
import getpass
import platform
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from threading import Thread

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar, QTabWidget,
    QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QRadioButton, QButtonGroup, QCheckBox, QLineEdit, QFormLayout,
    QGroupBox, QSplitter, QTreeWidget, QTreeWidgetItem, QMessageBox,
    QSystemTrayIcon, QMenu, QComboBox, QSpinBox, QFileDialog,
    QWizard, QWizardPage, QTextBrowser, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QTextCharFormat, QSyntaxHighlighter, QAction

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

try:
    from github import Github, GithubException, Auth
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

try:
    from git import Repo, GitCommandError
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


# ============================================================================
# CORE DATA MODELS
# ============================================================================

class VersionType(Enum):
    """Version suffix types"""
    ALPHA = "a"
    BETA = "b"
    RC = "rc"
    STABLE = ""


@dataclass
class Version:
    """Semantic version representation with custom suffix support"""
    major: int
    minor: int
    patch: int
    suffix: str = ""  # Custom suffix (e.g., 'a', 'b', 'rc', 'c', '-beta', etc.)

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.suffix:
            return f"{base}{self.suffix}"
        return base

    @classmethod
    def parse(cls, version_string: str) -> 'Version':
        """Parse version string into Version object - supports custom suffixes"""
        # Match: major.minor.patch followed by optional custom suffix
        pattern = r'^(\d+)\.(\d+)\.(\d+)(.*)$'
        match = re.match(pattern, version_string.strip())
        
        if not match:
            raise ValueError(f"Invalid version format: {version_string}")
        
        major, minor, patch, suffix = match.groups()
        
        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            suffix=suffix.strip()
        )

    def bump(self, bump_type: str = "patch") -> 'Version':
        """Bump version following logical rules"""
        # If there's a suffix, remove it when bumping
        if self.suffix:
            # Check if it's a known pre-release suffix
            if self.suffix in ['a', 'b', 'rc'] or self.suffix.startswith('a') or self.suffix.startswith('b') or self.suffix.startswith('rc'):
                # Remove suffix and return stable version
                return Version(self.major, self.minor, self.patch, "")
            else:
                # For custom suffixes, just remove them
                return Version(self.major, self.minor, self.patch, "")
        
        if bump_type == "major":
            return Version(self.major + 1, 0, 0, "")
        elif bump_type == "minor":
            return Version(self.major, self.minor + 1, 0, "")
        else:  # patch
            return Version(self.major, self.minor, self.patch + 1, "")



@dataclass
class DeploymentRecord:
    """Record of a deployment"""
    version: str
    timestamp: str
    branch: str
    commit_hash: str
    user: str
    success: bool
    notes: str = ""


@dataclass
class GitHubRelease:
    """GitHub release information"""
    tag_name: str
    name: str
    body: str
    draft: bool
    prerelease: bool
    created_at: str
    html_url: str


# ============================================================================
# VERSION MANAGEMENT
# ============================================================================

class VersionManager:
    """Handle version file operations"""
    
    def __init__(self, version_file: Path = None):
        if version_file is None:
            if Path("Version.txt").exists():
                version_file = Path("Version.txt")
            elif Path("version.txt").exists():
                version_file = Path("version.txt")
            else:
                version_file = Path("version.txt")
        self.version_file = version_file
        self.history_file = Path("version_history.json")
    
    def read_version(self) -> Version:
        """Read current version from file"""
        if not self.version_file.exists():
            self.write_version(Version(0, 1, 0))
            return Version(0, 1, 0)
        
        with open(self.version_file, 'r', encoding='utf-8') as f:
            version_str = f.read().strip()
        
        if not version_str:
            self.write_version(Version(0, 1, 0))
            return Version(0, 1, 0)
        
        return Version.parse(version_str)
    
    def write_version(self, version: Version):
        """Write version to file"""
        with open(self.version_file, 'w', encoding='utf-8') as f:
            f.write(str(version))
    
    def add_to_history(self, record: DeploymentRecord):
        """Add deployment to history"""
        history = self.get_history()
        history.insert(0, asdict(record))
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    
    def get_history(self) -> List[Dict]:
        """Get deployment history"""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def rollback_to_version(self, version_str: str) -> bool:
        """Rollback to a specific version"""
        try:
            version = Version.parse(version_str)
            self.write_version(version)
            return True
        except Exception:
            return False


# ============================================================================
# GIT OPERATIONS
# ============================================================================

class GitManager:
    """Handle all Git operations"""
    
    def __init__(self, repo_path: Path = Path.cwd()):
        self.repo_path = repo_path
        self.username = self._get_username()
    
    def _run_command(self, cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
        """Execute shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
    
    def _get_username(self) -> str:
        """Get local username"""
        try:
            code, stdout, _ = self._run_command(
                ["git", "config", "user.name"], check=False
            )
            if code == 0 and stdout.strip():
                return stdout.strip().lower().replace(" ", "-")
        except Exception:
            pass
        
        return getpass.getuser().lower().replace(" ", "-")
    
    def validate_repo(self) -> bool:
        """Check if current directory is a valid git repository"""
        code, _, _ = self._run_command(
            ["git", "rev-parse", "--git-dir"], check=False
        )
        if code != 0:
            return False
        
        code, _, _ = self._run_command(
            ["git", "config", "--get", "remote.origin.url"], check=False
        )
        return code == 0
    
    def get_current_branch(self) -> str:
        """Get current git branch"""
        _, stdout, _ = self._run_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        )
        return stdout.strip()
    
    def get_status(self) -> Dict[str, any]:
        """Get repository status"""
        status = {
            "branch": self.get_current_branch(),
            "clean": False,
            "ahead": 0,
            "behind": 0,
            "modified": [],
            "untracked": []
        }
        
        # Check if working directory is clean
        code, stdout, _ = self._run_command(
            ["git", "status", "--porcelain"], check=False
        )
        status["clean"] = len(stdout.strip()) == 0
        
        # Parse status
        for line in stdout.strip().split('\n'):
            if not line:
                continue
            state = line[:2]
            filename = line[3:]
            if state.strip() == '??':
                status["untracked"].append(filename)
            else:
                status["modified"].append(filename)
        
        return status
    
    def create_and_checkout_branch(self, branch_name: str) -> bool:
        """Create and checkout to new branch"""
        code, _, _ = self._run_command(
            ["git", "checkout", "-b", branch_name], check=False
        )
        return code == 0
    
    def commit_and_push(self, message: str, branch_name: str) -> bool:
        """Stage, commit, and push changes"""
        # Stage all changes
        code, _, stderr = self._run_command(
            ["git", "add", "-A"], check=False
        )
        if code != 0:
            return False
        
        # Commit
        code, _, stderr = self._run_command(
            ["git", "commit", "-m", message], check=False
        )
        if code != 0 and "nothing to commit" not in stderr:
            return False
        
        # Push
        code, _, _ = self._run_command(
            ["git", "push", "-u", "origin", branch_name], check=False
        )
        
        return code == 0
    
    def merge_to_main(self, source_branch: str) -> bool:
        """Merge source branch to main"""
        self._run_command(["git", "checkout", "main"])
        self._run_command(["git", "pull", "origin", "main"], check=False)
        
        code, _, _ = self._run_command(
            ["git", "merge", source_branch, "--no-ff", "-m", 
             f"Merge {source_branch} into main"], 
            check=False
        )
        
        if code != 0:
            return False
        
        self._run_command(["git", "push", "origin", "main"])
        return True
    
    def create_tag(self, tag_name: str, message: str):
        """Create and push git tag"""
        self._run_command(["git", "tag", "-a", tag_name, "-m", message])
        self._run_command(["git", "push", "origin", tag_name])
    
    def get_commit_hash(self) -> str:
        """Get current commit hash"""
        _, stdout, _ = self._run_command(["git", "rev-parse", "HEAD"])
        return stdout.strip()[:8]


# ============================================================================
# GITHUB INTEGRATION
# ============================================================================

class GitHubManager:
    """Handle GitHub API operations"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.repo_info = self._get_repo_info()
        self.github = None
        
        if GITHUB_AVAILABLE and self.token:
            try:
                # Use modern Auth method to avoid deprecation warning
                auth = Auth.Token(self.token)
                self.github = Github(auth=auth)
                
                # Diagnostic: Print token scopes
                try:
                    user = self.github.get_user()
                    print(f"GitHub Token Scopes: {self.github.oauth_scopes}")
                except Exception as scope_error:
                    print(f"Could not retrieve token scopes: {scope_error}")

            except Exception as e:
                print(f"Failed to initialize GitHub client with Auth: {e}")
                # Fallback for older PyGithub versions
                try:
                    self.github = Github(self.token)
                except:
                    pass
    
    def _get_repo_info(self) -> Dict[str, str]:
        """Extract owner and repo name from git remote"""
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {"owner": "", "repo": ""}
        
        url = result.stdout.strip()
        pattern = r'github\.com[:/](.+)/(.+?)(\.git)?$'
        match = re.search(pattern, url)
        
        if match:
            owner, repo = match.groups()[:2]
            repo = repo.replace('.git', '')
            return {"owner": owner, "repo": repo}
        
        return {"owner": "", "repo": ""}
    
    def create_release(self, tag: str, name: str, body: str, 
                      draft: bool = False, prerelease: bool = False) -> Optional[str]:
        """Create GitHub release"""
        if not self.github:
            return None
        
        try:
            repo = self.github.get_repo(f"{self.repo_info['owner']}/{self.repo_info['repo']}")
            release = repo.create_git_release(
                tag=tag,
                name=name,
                message=body,
                draft=draft,
                prerelease=prerelease
            )
            return release.html_url
        except GithubException as e:
            if e.status == 403:
                print(f"Permission Error: {e}")
                print("Please ensure your GitHub token has 'repo' scope (Classic) or 'contents: write' (Fine-grained).")
            else:
                print(f"Failed to create release: {e}")
            raise e  # Re-raise to show in GUI logs
        except Exception as e:
            print(f"Failed to create release: {e}")
            raise e
    
    def get_releases(self) -> List[GitHubRelease]:
        """Get all releases"""
        if not self.github:
            return []
        
        try:
            repo = self.github.get_repo(f"{self.repo_info['owner']}/{self.repo_info['repo']}")
            releases = []
            for rel in repo.get_releases():
                releases.append(GitHubRelease(
                    tag_name=rel.tag_name,
                    name=rel.name,
                    body=rel.body,
                    draft=rel.draft,
                    prerelease=rel.prerelease,
                    created_at=rel.created_at.isoformat(),
                    html_url=rel.html_url
                ))
            return releases
        except:
            return []
    
    def upload_asset(self, release_tag: str, file_path: Path) -> bool:
        """Upload asset to release"""
        if not self.github:
            return False
        
        try:
            repo = self.github.get_repo(f"{self.repo_info['owner']}/{self.repo_info['repo']}")
            release = repo.get_release(release_tag)
            release.upload_asset(str(file_path))
            return True
        except:
            return False


# ============================================================================
# CHANGELOG MANAGEMENT
# ============================================================================

class ChangelogManager:
    """Manage changelog entries"""
    
    def __init__(self, repo_path: Path = Path.cwd()):
        self.repo_path = repo_path
        self.changelog_file = self._find_changelog()
    
    def _find_changelog(self) -> Path:
        """Find changelog file (case-insensitive)"""
        for name in ["CHANGELOG.md", "changelog.md", "CHANGELOG", "changelog"]:
            path = self.repo_path / name
            if path.exists():
                return path
        return self.repo_path / "CHANGELOG.md"
    
    def read_changelog(self) -> str:
        """Read current changelog"""
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def add_entry(self, version: str, date: str, entry: str):
        """Add changelog entry to file"""
        if not entry:
            return
        
        existing = self.read_changelog()
        
        new_entry = f"## [{version}] - {date}\n\n{entry}\n\n"
        
        if not existing.startswith("#"):
            header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
            existing = header + existing
        
        if existing.startswith("#"):
            lines = existing.split('\n')
            header_end = 0
            for i, line in enumerate(lines):
                if line.startswith("##"):
                    header_end = i
                    break
            if header_end == 0:
                header_end = len([l for l in lines if l.strip()])
            
            new_content = '\n'.join(lines[:header_end]) + '\n\n' + new_entry + '\n'.join(lines[header_end:])
        else:
            new_content = new_entry + existing
        
        with open(self.changelog_file, 'w', encoding='utf-8') as f:
            f.write(new_content)


# ============================================================================
# DEPLOYMENT WORKER THREAD
# ============================================================================

class DeploymentWorker(QThread):
    """Background thread for deployment operations"""
    
    progress = pyqtSignal(int, str)  # step, message
    log = pyqtSignal(str, str)  # message, level
    finished = pyqtSignal(bool, str)  # success, message
    changelog_requested = pyqtSignal(str)  # version
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        self.changelog_entry = None
        self.changelog_ready = False
    
    def set_changelog(self, entry: str):
        """Set changelog entry from main thread"""
        self.changelog_entry = entry
        self.changelog_ready = True
    
    def run(self):
        """Execute deployment process"""
        try:
            version_mgr = VersionManager()
            git_mgr = GitManager()
            github_mgr = GitHubManager(self.config.get('github_token'))
            changelog_mgr = ChangelogManager()
            
            total_steps = 10
            
            # Step 1: Validate repository
            self.progress.emit(1, "Validating Git repository")
            self.log.emit("Validating repository...", "info")
            if not git_mgr.validate_repo():
                raise Exception("Not a valid Git repository")
            time.sleep(0.3)
            
            # Step 2: Create branch
            branch_name = f"develop-{git_mgr.username}"
            self.progress.emit(2, f"Creating branch: {branch_name}")
            self.log.emit(f"Creating branch: {branch_name}", "info")
            git_mgr.create_and_checkout_branch(branch_name)
            time.sleep(0.3)
            
            # Step 3: Bump version
            self.progress.emit(3, "Updating version")
            if self.config.get('custom_version'):
                new_version = Version.parse(self.config['custom_version'])
                version_mgr.write_version(new_version)
                self.log.emit(f"Version set to: {new_version}", "success")
            else:
                current_version = version_mgr.read_version()
                new_version = current_version.bump(self.config.get('bump_type', 'patch'))
                version_mgr.write_version(new_version)
                self.log.emit(f"Version bumped: {current_version} → {new_version}", "success")
            time.sleep(0.3)
            
            # Step 4: Changelog
            if not self.config.get('skip_changelog'):
                self.progress.emit(4, "Waiting for changelog entry")
                self.log.emit("Requesting changelog entry...", "info")
                self.changelog_requested.emit(str(new_version))
                
                # Wait for changelog
                timeout = 300
                elapsed = 0
                while not self.changelog_ready and elapsed < timeout:
                    time.sleep(0.1)
                    elapsed += 0.1
                
                if self.changelog_entry:
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    changelog_mgr.add_entry(str(new_version), date_str, self.changelog_entry)
                    self.log.emit("Changelog updated", "success")
            else:
                self.progress.emit(4, "Skipping changelog")
            time.sleep(0.3)
            
            # Step 5: Commit and push
            self.progress.emit(5, "Committing and pushing changes")
            self.log.emit("Committing changes...", "info")
            commit_msg = f"chore: bump version to {new_version}"
            if not git_mgr.commit_and_push(commit_msg, branch_name):
                raise Exception("Failed to push changes")
            self.log.emit("Changes pushed successfully", "success")
            time.sleep(0.5)
            
            # Step 6: Merge to main
            if self.config.get('auto_merge', True):
                self.progress.emit(6, "Merging to main branch")
                self.log.emit("Merging to main...", "info")
                if not git_mgr.merge_to_main(branch_name):
                    raise Exception("Failed to merge to main")
                self.log.emit("Merged to main successfully", "success")
            else:
                self.progress.emit(6, "Skipping auto-merge")
            time.sleep(0.5)
            
            # Step 7: Create tag
            self.progress.emit(7, "Creating tag")
            tag_name = f"v{new_version}"
            git_mgr.create_tag(tag_name, f"Release {new_version}")
            self.log.emit(f"Tag {tag_name} created", "success")
            time.sleep(0.3)
            
            # Step 8: Create GitHub release
            if github_mgr.github:
                self.progress.emit(8, "Creating GitHub release")
                self.log.emit("Creating GitHub release...", "info")
                
                release_name = self.config.get('release_title') or f"Release {new_version}"
                
                release_url = github_mgr.create_release(
                    tag=tag_name,
                    name=release_name,
                    body=self.changelog_entry or f"Release {new_version}",
                    draft=self.config.get('draft_release', False),
                    prerelease=self.config.get('prerelease', False)
                )
                if release_url:
                    self.log.emit(f"Release created: {release_url}", "success")
            else:
                self.progress.emit(8, "Skipping GitHub release (no token)")
            time.sleep(0.3)
            
            # Step 9: Save to history
            self.progress.emit(9, "Saving deployment record")
            record = DeploymentRecord(
                version=str(new_version),
                timestamp=datetime.now().isoformat(),
                branch=branch_name,
                commit_hash=git_mgr.get_commit_hash(),
                user=git_mgr.username,
                success=True,
                notes=self.changelog_entry or ""
            )
            version_mgr.add_to_history(record)
            time.sleep(0.3)
            
            # Complete
            self.progress.emit(10, "Deployment completed!")
            self.log.emit("=" * 50, "success")
            self.log.emit(f"Deployment completed successfully!", "success")
            self.log.emit(f"Version: {new_version}", "success")
            self.log.emit(f"Tag: {tag_name}", "success")
            
            self.finished.emit(True, f"Successfully deployed version {new_version}")
            
        except Exception as e:
            self.log.emit(f"Deployment failed: {str(e)}", "error")
            self.finished.emit(False, str(e))


# ============================================================================
# DEPLOYMENT WIZARD
# ============================================================================

class DeploymentWizard(QWizard):
    """7-step deployment wizard"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevSync Deployment Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(700, 500)
        
        self.config = {}
        
        # Add pages
        self.addPage(VersionBumpPage(self))
        self.addPage(ChangelogPage(self))
        self.addPage(ReviewPage(self))
        self.addPage(OptionsPage(self))
        self.addPage(ConfirmationPage(self))
        self.addPage(ProgressPage(self))
        self.addPage(ResultsPage(self))


class VersionBumpPage(QWizardPage):
    """Step 1: Version bump selector"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Version Bump")
        self.setSubTitle("Select how to bump the version")
        
        layout = QVBoxLayout()
        
        # Current version
        version_mgr = VersionManager()
        current = version_mgr.read_version()
        
        current_label = QLabel(f"Current Version: <b>{current}</b>")
        current_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(current_label)
        
        # Bump type buttons
        self.bump_group = QButtonGroup()
        
        bump_types = [
            ("patch", "Patch", current.bump("patch")),
            ("minor", "Minor", current.bump("minor")),
            ("major", "Major", current.bump("major"))
        ]
        
        for value, label, next_ver in bump_types:
            radio = QRadioButton(f"{label} ({next_ver})")
            radio.setProperty("bump_type", value)
            self.bump_group.addButton(radio)
            layout.addWidget(radio)
        
        self.bump_group.buttons()[0].setChecked(True)
        
        # Custom version
        layout.addWidget(QLabel("\nOr set custom version:"))
        self.custom_version = QLineEdit()
        self.custom_version.setPlaceholderText("e.g., 2.0.0, 1.5.0rc1")
        layout.addWidget(self.custom_version)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def validatePage(self):
        custom = self.custom_version.text().strip()
        if custom:
            try:
                Version.parse(custom)
                self.wizard().config['custom_version'] = custom
                self.wizard().config['bump_type'] = None
            except:
                QMessageBox.warning(self, "Invalid Version", "Please enter a valid version format (e.g., 1.2.3)")
                return False
        else:
            for btn in self.bump_group.buttons():
                if btn.isChecked():
                    self.wizard().config['bump_type'] = btn.property("bump_type")
                    self.wizard().config['custom_version'] = None
                    break
        return True


class ChangelogPage(QWizardPage):
    """Step 2: Changelog editor"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Changelog Entry")
        self.setSubTitle("Document changes in this release")
        
        layout = QVBoxLayout()
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Enter changelog entries:\n- Added feature X\n- Fixed bug Y\n- Improved performance")
        layout.addWidget(self.editor)
        
        # Preview (if markdown available)
        if MARKDOWN_AVAILABLE:
            splitter = QSplitter(Qt.Orientation.Vertical)
            splitter.addWidget(self.editor)
            
            self.preview = QTextBrowser()
            self.preview.setMaximumHeight(200)
            splitter.addWidget(self.preview)
            
            self.editor.textChanged.connect(self.update_preview)
            
            layout.addWidget(splitter)
        else:
            layout.addWidget(self.editor)
        
        # Skip checkbox
        self.skip_checkbox = QCheckBox("Skip changelog entry")
        layout.addWidget(self.skip_checkbox)
        
        self.setLayout(layout)
    
    def update_preview(self):
        """Update markdown preview"""
        if MARKDOWN_AVAILABLE:
            text = self.editor.toPlainText()
            html = markdown.markdown(text)
            self.preview.setHtml(html)
    
    def validatePage(self):
        if self.skip_checkbox.isChecked():
            self.wizard().config['skip_changelog'] = True
            self.wizard().config['changelog_entry'] = None
        else:
            self.wizard().config['skip_changelog'] = False
            self.wizard().config['changelog_entry'] = self.editor.toPlainText().strip()
        return True


class ReviewPage(QWizardPage):
    """Step 3: Review changes"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Review Changes")
        self.setSubTitle("Review files that will be committed")
        
        layout = QVBoxLayout()
        
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        self.setLayout(layout)
    
    def initializePage(self):
        """Load git status"""
        self.file_list.clear()
        
        git_mgr = GitManager()
        status = git_mgr.get_status()
        
        for file in status['modified']:
            item = QListWidgetItem(f"Modified: {file}")
            item.setForeground(QColor("orange"))
            self.file_list.addItem(item)
        
        for file in status['untracked']:
            item = QListWidgetItem(f"New: {file}")
            item.setForeground(QColor("green"))
            self.file_list.addItem(item)


class OptionsPage(QWizardPage):
    """Step 4: Deployment options"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Deployment Options")
        self.setSubTitle("Configure deployment settings")
        
        layout = QFormLayout()
        
        self.release_title = QLineEdit()
        self.release_title.setPlaceholderText("Auto-generated if empty")
        layout.addRow("Release Title:", self.release_title)
        
        self.auto_merge = QCheckBox("Automatically merge to main branch")
        self.auto_merge.setChecked(True)
        layout.addRow("Auto-merge:", self.auto_merge)
        
        self.draft_release = QCheckBox("Create as draft release")
        layout.addRow("Draft:", self.draft_release)
        
        self.prerelease = QCheckBox("Mark as pre-release")
        layout.addRow("Pre-release:", self.prerelease)
        
        self.setLayout(layout)
    
    def validatePage(self):
        self.wizard().config['release_title'] = self.release_title.text().strip()
        self.wizard().config['auto_merge'] = self.auto_merge.isChecked()
        self.wizard().config['draft_release'] = self.draft_release.isChecked()
        self.wizard().config['prerelease'] = self.prerelease.isChecked()
        return True


class ConfirmationPage(QWizardPage):
    """Step 5: Confirmation summary"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Confirm Deployment")
        self.setSubTitle("Review your deployment configuration")
        
        layout = QVBoxLayout()
        
        self.summary = QTextBrowser()
        layout.addWidget(self.summary)
        
        self.setLayout(layout)
    
    def initializePage(self):
        """Generate summary"""
        config = self.wizard().config
        
        version_mgr = VersionManager()
        current = version_mgr.read_version()
        
        if config.get('custom_version'):
            next_ver = config['custom_version']
        else:
            next_ver = str(current.bump(config.get('bump_type', 'patch')))
        
        summary = f"""
        <h2>Deployment Summary</h2>
        <table>
        <tr><td><b>Current Version:</b></td><td>{current}</td></tr>
        <tr><td><b>Next Version:</b></td><td>{next_ver}</td></tr>
        <tr><td><b>Release Title:</b></td><td>{config.get('release_title') or f"Release {next_ver}"}</td></tr>
        <tr><td><b>Auto-merge:</b></td><td>{'Yes' if config.get('auto_merge') else 'No'}</td></tr>
        <tr><td><b>Draft Release:</b></td><td>{'Yes' if config.get('draft_release') else 'No'}</td></tr>
        <tr><td><b>Pre-release:</b></td><td>{'Yes' if config.get('prerelease') else 'No'}</td></tr>
        </table>
        
        <h3>Changelog:</h3>
        <pre>{config.get('changelog_entry', 'None')}</pre>
        """
        
        self.summary.setHtml(summary)


class ProgressPage(QWizardPage):
    """Step 6: Progress with live logs"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Deploying")
        self.setSubTitle("Deployment in progress...")
        
        layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(10)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Starting deployment...")
        layout.addWidget(self.status_label)
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_view)
        
        self.setLayout(layout)
        
        self.worker = None
    
    def initializePage(self):
        """Start deployment"""
        # Get GitHub token
        token_mgr = TokenManager()
        github_token = token_mgr.get_token() or os.environ.get("GITHUB_TOKEN")
        
        config = self.wizard().config.copy()
        config['github_token'] = github_token
        
        self.worker = DeploymentWorker(config)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.add_log)
        self.worker.finished.connect(self.deployment_finished)
        self.worker.changelog_requested.connect(self.handle_changelog_request)
        self.worker.start()
    
    def update_progress(self, step, message):
        """Update progress bar"""
        self.progress_bar.setValue(step)
        self.status_label.setText(message)
    
    def add_log(self, message, level):
        """Add log entry"""
        colors = {
            "info": "black",
            "success": "green",
            "warning": "orange",
            "error": "red"
        }
        
        color = colors.get(level, "black")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_view.append(f'<span style="color: {color}">[{timestamp}] {message}</span>')
    
    def handle_changelog_request(self, version):
        """Handle changelog request from worker"""
        if self.wizard().config.get('changelog_entry'):
            self.worker.set_changelog(self.wizard().config['changelog_entry'])
    
    def deployment_finished(self, success, message):
        """Handle deployment completion"""
        self.wizard().config['deployment_success'] = success
        self.wizard().config['deployment_message'] = message
        self.wizard().next()


class ResultsPage(QWizardPage):
    """Step 7: Results with GitHub release link"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Deployment Complete")
        
        layout = QVBoxLayout()
        
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-size: 14px; padding: 20px;")
        layout.addWidget(self.result_label)
        
        self.details = QTextBrowser()
        layout.addWidget(self.details)
        
        self.setLayout(layout)
    
    def initializePage(self):
        """Show results"""
        config = self.wizard().config
        success = config.get('deployment_success', False)
        message = config.get('deployment_message', '')
        
        if success:
            self.result_label.setText("✅ Deployment completed successfully!")
            self.result_label.setStyleSheet("font-size: 16px; color: green; padding: 20px;")
            
            version_mgr = VersionManager()
            current = version_mgr.read_version()
            
            details = f"""
            <h2>Deployment Details</h2>
            <p><b>Version:</b> {current}</p>
            <p><b>Tag:</b> v{current}</p>
            <p>{message}</p>
            """
            
            self.details.setHtml(details)
        else:
            self.result_label.setText("❌ Deployment failed")
            self.result_label.setStyleSheet("font-size: 16px; color: red; padding: 20px;")
            self.details.setPlainText(f"Error: {message}")


# ============================================================================
# MAIN WINDOW
# ============================================================================

# ============================================================================
# TOKEN MANAGEMENT
# ============================================================================

class TokenManager:
    """Handle secure token storage with fallback"""
    
    def __init__(self):
        self.service_name = "devsync"
        self.username = "github_token"
        self.fallback_file = Path(".devsync_token")
    
    def save_token(self, token: str) -> bool:
        """Save token to keyring or fallback file"""
        if not token:
            return False
            
        # Try keyring first
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(self.service_name, self.username, token)
                return True
            except Exception as e:
                print(f"Keyring failed: {e}")
        
        # Fallback to file (simple obfuscation)
        try:
            # Simple obfuscation to avoid plain text (not secure encryption)
            obfuscated = "".join([chr(ord(c) + 1) for c in token])
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated)
            # Hide file on Windows
            if platform.system() == "Windows":
                subprocess.run(["attrib", "+h", str(self.fallback_file)], check=False)
            return True
        except Exception as e:
            print(f"Fallback save failed: {e}")
            return False
    
    def get_token(self) -> Optional[str]:
        """Retrieve token from keyring or fallback file"""
        # Try keyring first
        if KEYRING_AVAILABLE:
            try:
                token = keyring.get_password(self.service_name, self.username)
                if token:
                    return token
            except Exception:
                pass
        
        # Try fallback file
        if self.fallback_file.exists():
            try:
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    obfuscated = f.read().strip()
                return "".join([chr(ord(c) - 1) for c in obfuscated])
            except Exception:
                pass
        
        return None


# ============================================================================
# MAIN WINDOW
# ============================================================================

class DevSyncMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevSync - Deployment Automation")
        self.setMinimumSize(1200, 800)
        
        # Settings
        self.settings = QSettings("DevSync", "DeploymentTool")
        
        # Load theme
        self.current_theme = self.settings.value("theme", "light")
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_system_tray()
        
        # Apply theme
        self.apply_theme(self.current_theme)
        
        # Load data
        self.refresh_dashboard()
    
    def setup_ui(self):
        """Create main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("🚀 DevSync")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Quick deploy button
        self.deploy_btn = QPushButton("Deploy Now")
        self.deploy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.deploy_btn.clicked.connect(self.start_deployment_wizard)
        header_layout.addWidget(self.deploy_btn)
        
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Dashboard tab
        self.dashboard_widget = self.create_dashboard()
        self.tabs.addTab(self.dashboard_widget, "Dashboard")
        
        # Releases tab
        self.releases_widget = self.create_releases_tab()
        self.tabs.addTab(self.releases_widget, "Releases")
        
        # Changelog tab
        self.changelog_widget = self.create_changelog_tab()
        self.tabs.addTab(self.changelog_widget, "Changelog")
        
        # History tab
        self.history_widget = self.create_history_tab()
        self.tabs.addTab(self.history_widget, "History")
        
        # Settings tab
        self.settings_widget = self.create_settings_tab()
        self.tabs.addTab(self.settings_widget, "Settings")
        
        layout.addWidget(self.tabs)
    
    def create_dashboard(self) -> QWidget:
        """Create dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Status cards
        cards_layout = QHBoxLayout()
        
        # Version card
        version_card = QGroupBox("Current Version")
        version_layout = QVBoxLayout()
        self.version_label = QLabel("0.0.0")
        self.version_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.version_label.setStyleSheet("color: #2196F3;")
        version_layout.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignCenter)
        version_card.setLayout(version_layout)
        cards_layout.addWidget(version_card)
        
        # Git status card
        git_card = QGroupBox("Git Status")
        git_layout = QVBoxLayout()
        self.branch_label = QLabel("Branch: main")
        self.status_label = QLabel("Status: Clean")
        git_layout.addWidget(self.branch_label)
        git_layout.addWidget(self.status_label)
        git_card.setLayout(git_layout)
        cards_layout.addWidget(git_card)
        
        # Last deployment card
        deploy_card = QGroupBox("Last Deployment")
        deploy_layout = QVBoxLayout()
        self.last_deploy_label = QLabel("Never")
        deploy_layout.addWidget(self.last_deploy_label)
        deploy_card.setLayout(deploy_layout)
        cards_layout.addWidget(deploy_card)
        
        layout.addLayout(cards_layout)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()
        self.activity_list = QListWidget()
        activity_layout.addWidget(self.activity_list)
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        return widget
    
    def create_releases_tab(self) -> QWidget:
        """Create releases management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_releases)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Releases table
        self.releases_table = QTableWidget()
        self.releases_table.setColumnCount(5)
        self.releases_table.setHorizontalHeaderLabels(["Tag", "Name", "Date", "Type", "URL"])
        layout.addWidget(self.releases_table)
        
        return widget
    
    def create_changelog_tab(self) -> QWidget:
        """Create changelog editor tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changelog)
        toolbar.addWidget(save_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Split pane: editor | preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.changelog_editor = QTextEdit()
        splitter.addWidget(self.changelog_editor)
        
        self.changelog_preview = QTextBrowser()
        splitter.addWidget(self.changelog_preview)
        
        if MARKDOWN_AVAILABLE:
            self.changelog_editor.textChanged.connect(self.update_changelog_preview)
        
        layout.addWidget(splitter)
        
        # Load changelog
        self.load_changelog()
        
        return widget
    
    def create_history_tab(self) -> QWidget:
        """Create deployment history tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_history)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # History tree
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Version", "Date", "User", "Status"])
        self.history_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_tree.customContextMenuRequested.connect(self.show_history_context_menu)
        layout.addWidget(self.history_tree)
        
        return widget
    


# ... (inside SettingsTab class methods) ...

    def create_settings_tab(self) -> QWidget:
        """Create settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Git settings
        layout.addRow(QLabel("<h3>Git Settings</h3>"))
        
        self.git_user = QLineEdit()
        layout.addRow("User Name:", self.git_user)
        
        self.git_email = QLineEdit()
        layout.addRow("Email:", self.git_email)
        
        # GitHub settings
        layout.addRow(QLabel("<h3>GitHub Settings</h3>"))
        
        self.github_token = QLineEdit()
        self.github_token.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Access Token:", self.github_token)
        
        btn_layout = QHBoxLayout()
        
        save_token_btn = QPushButton("Save Token")
        save_token_btn.clicked.connect(self.save_github_token)
        btn_layout.addWidget(save_token_btn)
        
        test_token_btn = QPushButton("Test Token")
        test_token_btn.clicked.connect(self.test_github_token)
        btn_layout.addWidget(test_token_btn)
        
        layout.addRow("", btn_layout)
        
        # UI settings
        layout.addRow(QLabel("<h3>UI Settings</h3>"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(self.current_theme.capitalize())
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        layout.addRow("Theme:", self.theme_combo)
        
        return widget
    
    def setup_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        deploy_action = QAction("Deploy", self)
        deploy_action.triggered.connect(self.start_deployment_wizard)
        file_menu.addAction(deploy_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_dashboard)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("DevSync")
        
        # Tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        deploy_action = QAction("Deploy", self)
        deploy_action.triggered.connect(self.start_deployment_wizard)
        tray_menu.addAction(deploy_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def apply_theme(self, theme: str):
        """Apply color theme"""
        if theme.lower() == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #555;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #ffffff;
                }
                QTextEdit, QListWidget, QTreeWidget, QTableWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #555;
                }
            """)
        else:
            self.setStyleSheet("")
    
    def change_theme(self, theme: str):
        """Change application theme"""
        self.current_theme = theme.lower()
        self.settings.setValue("theme", self.current_theme)
        self.apply_theme(self.current_theme)
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Update version
        version_mgr = VersionManager()
        current_version = version_mgr.read_version()
        self.version_label.setText(str(current_version))
        
        # Update git status
        git_mgr = GitManager()
        status = git_mgr.get_status()
        self.branch_label.setText(f"Branch: {status['branch']}")
        self.status_label.setText(f"Status: {'Clean' if status['clean'] else 'Modified'}")
        
        # Update last deployment
        history = version_mgr.get_history()
        if history:
            last = history[0]
            self.last_deploy_label.setText(f"{last['version']} - {last['timestamp'][:10]}")
        
        # Update activity
        self.activity_list.clear()
        for record in history[:10]:
            item = QListWidgetItem(f"{record['version']} - {record['timestamp'][:19]} - {record['user']}")
            self.activity_list.addItem(item)
    
    def refresh_releases(self):
        """Refresh GitHub releases"""
        token_mgr = TokenManager()
        github_token = token_mgr.get_token() or os.environ.get("GITHUB_TOKEN")
        
        github_mgr = GitHubManager(github_token)
        releases = github_mgr.get_releases()
        
        self.releases_table.setRowCount(len(releases))
        for i, release in enumerate(releases):
            self.releases_table.setItem(i, 0, QTableWidgetItem(release.tag_name))
            self.releases_table.setItem(i, 1, QTableWidgetItem(release.name))
            self.releases_table.setItem(i, 2, QTableWidgetItem(release.created_at[:10]))
            type_str = "Draft" if release.draft else ("Pre-release" if release.prerelease else "Release")
            self.releases_table.setItem(i, 3, QTableWidgetItem(type_str))
            self.releases_table.setItem(i, 4, QTableWidgetItem(release.html_url))
    
    def load_changelog(self):
        """Load changelog content"""
        changelog_mgr = ChangelogManager()
        content = changelog_mgr.read_changelog()
        self.changelog_editor.setPlainText(content)
    
    def save_changelog(self):
        """Save changelog content"""
        changelog_mgr = ChangelogManager()
        content = self.changelog_editor.toPlainText()
        
        with open(changelog_mgr.changelog_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        QMessageBox.information(self, "Success", "Changelog saved successfully!")
    
    def update_changelog_preview(self):
        """Update changelog preview"""
        if MARKDOWN_AVAILABLE:
            text = self.changelog_editor.toPlainText()
            html = markdown.markdown(text)
            self.changelog_preview.setHtml(html)
    
    def refresh_history(self):
        """Refresh deployment history"""
        self.history_tree.clear()
        
        version_mgr = VersionManager()
        history = version_mgr.get_history()
        
        for record in history:
            item = QTreeWidgetItem([
                record['version'],
                record['timestamp'][:19],
                record['user'],
                "Success" if record['success'] else "Failed"
            ])
            
            if record['success']:
                item.setForeground(3, QColor("green"))
            else:
                item.setForeground(3, QColor("red"))
            
            self.history_tree.addTopLevelItem(item)
    
    def show_history_context_menu(self, position):
        """Show context menu for history"""
        item = self.history_tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        rollback_action = QAction("Rollback to this version", self)
        rollback_action.triggered.connect(lambda: self.rollback_to_version(item.text(0)))
        menu.addAction(rollback_action)
        
        menu.exec(self.history_tree.viewport().mapToGlobal(position))
    
    def rollback_to_version(self, version: str):
        """Rollback to a specific version"""
        reply = QMessageBox.question(
            self,
            "Confirm Rollback",
            f"Are you sure you want to rollback to version {version}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            version_mgr = VersionManager()
            if version_mgr.rollback_to_version(version):
                QMessageBox.information(self, "Success", f"Rolled back to version {version}")
                self.refresh_dashboard()
            else:
                QMessageBox.warning(self, "Error", "Failed to rollback version")
    
    def save_github_token(self):
        """Save GitHub token"""
        token = self.github_token.text().strip()
        
        if not token:
            QMessageBox.warning(self, "Error", "Please enter a token")
            return
        
        token_mgr = TokenManager()
        if token_mgr.save_token(token):
            QMessageBox.information(self, "Success", "Token saved successfully!")
            self.github_token.clear()
        else:
            QMessageBox.warning(self, "Error", "Failed to save token")

    def test_github_token(self):
        """Test the saved GitHub token"""
        token_mgr = TokenManager()
        token = token_mgr.get_token() or os.environ.get("GITHUB_TOKEN")
        
        if not token:
            QMessageBox.warning(self, "Error", "No token found. Please save one first.")
            return
            
        try:
            if GITHUB_AVAILABLE:
                auth = Auth.Token(token)
                g = Github(auth=auth)
                user = g.get_user()
                login = user.login
                scopes = g.oauth_scopes
                
                msg = f"✅ Authentication Successful!\n\nUser: {login}\nScopes: {scopes}\n\n"
                
                if scopes:
                    if 'repo' in scopes or 'public_repo' in scopes:
                         msg += "Has 'repo' scope: YES"
                    else:
                         msg += "Has 'repo' scope: NO (Releases might fail)"
                else:
                    msg += "Token type: Fine-grained (or no scopes available).\nPermissions cannot be verified via scopes."
                
                QMessageBox.information(self, "Token Valid", msg)
            else:
                QMessageBox.warning(self, "Error", "PyGithub not installed")
        except Exception as e:
            QMessageBox.critical(self, "Token Invalid", f"Authentication failed:\n{str(e)}")
    
    def start_deployment_wizard(self):
        """Launch deployment wizard"""
        wizard = DeploymentWizard(self)
        wizard.exec()
        
        # Refresh after deployment
        self.refresh_dashboard()
        self.refresh_history()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About DevSync",
            """
            <h2>DevSync</h2>
            <p>Professional Deployment Automation Tool</p>
            <p>Version: 1.0.0</p>
            <p>A single-file desktop application for managing deployments,
            version control, and GitHub releases.</p>
            """
        )


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("DevSync")
    app.setOrganizationName("DevSync")
    
    # Check dependencies
    missing_deps = []
    if not GITHUB_AVAILABLE:
        missing_deps.append("PyGithub")
    if not GITPYTHON_AVAILABLE:
        missing_deps.append("GitPython")
    if not YAML_AVAILABLE:
        missing_deps.append("PyYAML")
    if not MARKDOWN_AVAILABLE:
        missing_deps.append("markdown")
    if not KEYRING_AVAILABLE:
        missing_deps.append("keyring")
    
    if missing_deps:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Missing Dependencies")
        msg.setText("Some optional dependencies are missing:")
        msg.setInformativeText("\n".join(f"- {dep}" for dep in missing_deps))
        msg.setDetailedText("Install with: pip install " + " ".join(missing_deps))
        msg.exec()
    
    # Create and show main window
    window = DevSyncMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
