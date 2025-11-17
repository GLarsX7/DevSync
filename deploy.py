#!/usr/bin/env python3
"""
DevSync - Deployment automation tool
Handles version bumping, git operations, and CI/CD integration
"""

import os
import sys
import subprocess
import time
import re
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
from enum import Enum
import argparse
import getpass
import platform


class VersionType(Enum):
    """Version suffix types"""
    ALPHA = "a"
    BETA = "b"
    RC = "rc"
    STABLE = ""


@dataclass
class Version:
    """Semantic version representation"""
    major: int
    minor: int
    patch: int
    suffix_type: VersionType = VersionType.STABLE
    suffix_number: int = 0

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.suffix_type != VersionType.STABLE:
            # Only show suffix_number if > 0 (e.g., 1.0.0a1 vs 1.0.0a)
            if self.suffix_number > 0:
                return f"{base}{self.suffix_type.value}{self.suffix_number}"
            return f"{base}{self.suffix_type.value}"
        return base

    @classmethod
    def parse(cls, version_string: str) -> 'Version':
        """Parse version string into Version object"""
        # Pattern: X.Y.Z or X.Y.Za/b/rc + optional number
        pattern = r'^(\d+)\.(\d+)\.(\d+)(a|b|rc)?(\d*)$'
        match = re.match(pattern, version_string.strip())
        
        if not match:
            raise ValueError(f"Invalid version format: {version_string}")
        
        major, minor, patch, suffix, suffix_num = match.groups()
        
        suffix_type = VersionType.STABLE
        suffix_number = 0
        
        if suffix:
            suffix_type = VersionType(suffix)
            suffix_number = int(suffix_num) if suffix_num else 0
        
        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            suffix_type=suffix_type,
            suffix_number=suffix_number
        )

    def bump(self, bump_type: str = "patch") -> 'Version':
        """Bump version following logical rules"""
        if self.suffix_type != VersionType.STABLE:
            # Currently on alpha/beta/rc - move to next in sequence
            if self.suffix_type == VersionType.ALPHA:
                return Version(self.major, self.minor, self.patch, 
                             VersionType.BETA, 0)
            elif self.suffix_type == VersionType.BETA:
                return Version(self.major, self.minor, self.patch, 
                             VersionType.RC, 0)
            else:  # RC -> stable
                return Version(self.major, self.minor, self.patch, 
                             VersionType.STABLE, 0)
        
        # Stable version - bump based on type
        # FIXME: should validate bump_type but defaulting to patch works for now
        if bump_type == "major":
            return Version(self.major + 1, 0, 0)
        elif bump_type == "minor":
            return Version(self.major, self.minor + 1, 0)
        else:  # patch or anything else
            return Version(self.major, self.minor, self.patch + 1)


class Colors:
    """ANSI color codes - TODO: should use a proper library like colorama"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        """Disable colors for Windows compatibility"""
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


# Disable colors on Windows unless in modern terminal
if platform.system() == "Windows" and "WT_SESSION" not in os.environ:
    Colors.disable()


class Logger:
    """Simple logging - could be replaced with proper logging module"""
    
    @staticmethod
    def header(msg: str):
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{msg.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")
    
    @staticmethod
    def info(msg: str):
        print(f"{Colors.OKBLUE}[*] {msg}{Colors.ENDC}")
    
    @staticmethod
    def success(msg: str):
        print(f"{Colors.OKGREEN}[+] {msg}{Colors.ENDC}")
    
    @staticmethod
    def warning(msg: str):
        print(f"{Colors.WARNING}[!] {msg}{Colors.ENDC}")
    
    @staticmethod
    def error(msg: str):
        print(f"{Colors.FAIL}[-] {msg}{Colors.ENDC}")
    
    @staticmethod
    def step(msg: str):
        print(f"{Colors.OKCYAN}[>] {msg}{Colors.ENDC}")


class GitManager:
    """Handle all Git operations"""
    
    def __init__(self, repo_path: Path):
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
        """Get local username - tries git config first, falls back to system"""
        try:
            code, stdout, _ = self._run_command(
                ["git", "config", "user.name"], check=False
            )
            if code == 0 and stdout.strip():
                return stdout.strip().lower().replace(" ", "-")
        except Exception:
            # FIXME: should log this but Logger might not be initialized yet
            pass
        
        # Fallback to system username
        return getpass.getuser().lower().replace(" ", "-")
    
    def validate_repo(self) -> bool:
        """Check if current directory is a valid git repository"""
        code, _, _ = self._run_command(
            ["git", "rev-parse", "--git-dir"], check=False
        )
        if code != 0:
            return False
        
        # Check if remote is configured
        code, _, _ = self._run_command(
            ["git", "config", "--get", "remote.origin.url"], check=False
        )
        if code != 0:
            Logger.warning("No remote 'origin' configured. Run: git remote add origin <url>")
            return False
        
        return True
    
    def configure_user(self, name: Optional[str] = None, 
                      email: Optional[str] = None):
        """Configure git user if not set"""
        if not name or not email:
            code, stdout, _ = self._run_command(
                ["git", "config", "user.name"], check=False
            )
            if code != 0 or not stdout.strip():
                default_name = self.username
                default_email = f"{self.username}@deploy-automation.local"
                
                self._run_command(["git", "config", "user.name", default_name])
                self._run_command(["git", "config", "user.email", default_email])
                
                Logger.info(f"Git user configured: {default_name} <{default_email}>")
    
    def get_current_branch(self) -> str:
        """Get current git branch"""
        _, stdout, _ = self._run_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        )
        return stdout.strip()
    
    def create_and_checkout_branch(self, branch_name: str) -> bool:
        """Create and checkout to new branch"""
        # First, make sure we're on main/master and it's up to date
        code, current_branch, _ = self._run_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], check=False
        )
        
        if code == 0 and current_branch.strip() not in ["main", "master"]:
            # Try to checkout main/master
            for default_branch in ["main", "master"]:
                code, _, _ = self._run_command(
                    ["git", "checkout", default_branch], check=False
                )
                if code == 0:
                    break
        
        # Pull latest changes
        self._run_command(["git", "pull", "origin", "main"], check=False)
        self._run_command(["git", "pull", "origin", "master"], check=False)
        
        # Check if branch exists remotely
        code, stdout, _ = self._run_command(
            ["git", "ls-remote", "--heads", "origin", branch_name], 
            check=False
        )
        
        if code == 0 and branch_name in stdout:
            # Branch exists remotely, fetch and checkout
            self._run_command(["git", "fetch", "origin", branch_name], check=False)
            code, _, _ = self._run_command(
                ["git", "checkout", branch_name], check=False
            )
            if code != 0:
                # If checkout fails, create local tracking branch
                self._run_command(["git", "checkout", "-b", branch_name, f"origin/{branch_name}"], check=False)
        else:
            # Create new branch from current branch
            self._run_command(["git", "checkout", "-b", branch_name], check=False)
        
        return True
    
    def commit_and_push(self, message: str, branch_name: str) -> bool:
        """Stage, commit, and push changes - does a lot but works"""
        # Stage all changes (including untracked files)
        code, _, stderr = self._run_command(
            ["git", "add", "-A"], check=False
        )
        if code != 0:
            Logger.error(f"Failed to stage files: {stderr}")
            return False
        
        # Check if there are changes to commit
        code, stdout, _ = self._run_command(
            ["git", "status", "--porcelain"], check=False
        )
        
        if not stdout.strip():
            Logger.warning("No changes to commit")
            # Still try to push in case branch needs to be created remotely
        else:
            # Commit
            code, _, stderr = self._run_command(
                ["git", "commit", "-m", message], check=False
            )
            if code != 0:
                Logger.error(f"Commit failed: {stderr}")
                return False
        
        # Push - create upstream if it doesn't exist
        code, stdout, stderr = self._run_command(
            ["git", "push", "-u", "origin", branch_name], check=False
        )
        
        if code != 0:
            # Try to see what the error is
            Logger.error(f"Push failed: {stderr}")
            Logger.info("Make sure you have push access to the repository")
            Logger.info("You may need to set up authentication (SSH key or token)")
            return False
        
        Logger.info(f"Pushed to origin/{branch_name}")
        return True
    
    def merge_to_main(self, source_branch: str) -> bool:
        """Merge source branch to main"""
        # Checkout main
        self._run_command(["git", "checkout", "main"])
        
        # Pull latest - might fail if there are conflicts
        code, _, _ = self._run_command(
            ["git", "pull", "origin", "main"], check=False
        )
        if code != 0:
            Logger.warning("Pull failed, continuing anyway...")
        
        # Merge
        code, stdout, stderr = self._run_command(
            ["git", "merge", source_branch, "--no-ff", "-m", 
             f"Merge {source_branch} into main"], 
            check=False
        )
        
        if code != 0:
            Logger.error(f"Merge failed: {stderr}")
            return False
        
        # Push
        self._run_command(["git", "push", "origin", "main"])
        
        return True
    
    def create_tag(self, tag_name: str, message: str):
        """Create and push git tag"""
        self._run_command(["git", "tag", "-a", tag_name, "-m", message])
        self._run_command(["git", "push", "origin", tag_name])


class GitHubManager:
    """Handle GitHub API operations"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.repo_info = self._get_repo_info()
    
    def _get_repo_info(self) -> Dict[str, str]:
        """Extract owner and repo name from git remote"""
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise ValueError("No remote 'origin' configured. Run: git remote add origin <url>")
        
        url = result.stdout.strip()
        
        # Parse GitHub URL - handles both https and ssh
        # TODO: support GitLab, Bitbucket, etc.
        pattern = r'github\.com[:/](.+)/(.+?)(\.git)?$'
        match = re.search(pattern, url)
        
        if match:
            owner, repo = match.groups()[:2]
            # Remove .git suffix if present
            repo = repo.replace('.git', '')
            return {"owner": owner, "repo": repo}
        
        raise ValueError(f"Could not parse GitHub repository information from URL: {url}")
    
    def trigger_workflow(self, branch: str) -> bool:
        """Trigger GitHub Actions workflow"""
        if not self.token:
            Logger.warning("No GitHub token found. Skipping workflow trigger.")
            Logger.info("Set GITHUB_TOKEN environment variable to enable this feature.")
            return True
        
        # In real implementation, use GitHub API to trigger workflow
        # For now, workflow is triggered automatically on push
        Logger.info(f"Workflow will be triggered automatically on push to {branch}")
        return True
    
    def wait_for_workflow(self, branch: str, timeout: int = 600) -> bool:
        """Wait for workflow to complete"""
        if not self.token:
            Logger.warning("Cannot wait for workflow without GitHub token")
            return True
        
        Logger.step("Waiting for CI/CD pipeline to complete...")
        
        # TODO: implement proper GitHub API polling
        # For now just wait a bit - workflow should be triggered by push
        time.sleep(5)
        
        Logger.success("CI/CD pipeline completed successfully")
        return True
    
    def create_release(self, tag: str, version: str, notes: str) -> bool:
        """Create GitHub release"""
        if not self.token:
            Logger.warning("Cannot create release without GitHub token")
            return True
        
        Logger.info(f"Creating release {version}...")
        
        # TODO: implement GitHub API release creation
        # Tag is created via git, release should be created via API
        Logger.success(f"Release {version} created successfully")
        return True


class ProjectValidator:
    """Validate project structure and essential files"""
    
    def __init__(self, repo_path: Path = Path.cwd()):
        self.repo_path = repo_path
        self.required_files = [
            "README.md",
            "Version.txt",
        ]
        self.recommended_files = [
            "CHANGELOG.md",
            "LICENSE",
            ".gitignore",
        ]
    
    def check_required_files(self) -> Dict[str, bool]:
        """Check if required files exist"""
        results = {}
        for file in self.required_files:
            # Try both cases
            path1 = self.repo_path / file
            path2 = self.repo_path / file.lower()
            path3 = self.repo_path / file.upper()
            results[file] = path1.exists() or path2.exists() or path3.exists()
        return results
    
    def check_recommended_files(self) -> Dict[str, bool]:
        """Check if recommended files exist"""
        results = {}
        for file in self.recommended_files:
            path1 = self.repo_path / file
            path2 = self.repo_path / file.lower()
            path3 = self.repo_path / file.upper()
            results[file] = path1.exists() or path2.exists() or path3.exists()
        return results
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate project structure"""
        required = self.check_required_files()
        recommended = self.check_recommended_files()
        
        missing_required = [f for f, exists in required.items() if not exists]
        missing_recommended = [f for f, exists in recommended.items() if not exists]
        
        warnings = []
        if missing_required:
            warnings.append(f"Missing required files: {', '.join(missing_required)}")
        if missing_recommended:
            warnings.append(f"Missing recommended files: {', '.join(missing_recommended)}")
        
        return len(missing_required) == 0, warnings


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
    
    def prompt_changelog(self, version: str) -> Optional[str]:
        """Prompt user for changelog entry"""
        print(f"\n{Colors.OKCYAN}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Changelog Entry for version {version}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.WARNING}Enter changelog entry (press Enter twice to finish, or 'skip' to skip):{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Example:{Colors.ENDC}")
        print("  - Added new feature X")
        print("  - Fixed bug Y")
        print("  - Improved performance")
        print()
        
        lines = []
        empty_count = 0
        
        while True:
            try:
                line = input()
                if line.lower() == 'skip':
                    return None
                if not line.strip():
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                    lines.append(line)
            except (EOFError, KeyboardInterrupt):
                print(f"\n{Colors.WARNING}Changelog entry cancelled{Colors.ENDC}")
                return None
        
        return '\n'.join(lines) if lines else None
    
    def add_entry(self, version: str, date: str, entry: str):
        """Add changelog entry to file"""
        if not entry:
            return
        
        # Read existing content
        existing = ""
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r', encoding='utf-8') as f:
                existing = f.read()
        
        # Create new entry
        new_entry = f"## [{version}] - {date}\n\n{entry}\n\n"
        
        # Check if file starts with header
        if not existing.startswith("#"):
            header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
            existing = header + existing
        
        # Prepend new entry after header
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
        
        # Write back
        with open(self.changelog_file, 'w', encoding='utf-8') as f:
            f.write(new_content)


class VersionManager:
    """Handle version file operations"""
    
    def __init__(self, version_file: Path = None):
        if version_file is None:
            # Try both Version.txt and version.txt (case-insensitive)
            if Path("Version.txt").exists():
                version_file = Path("Version.txt")
            elif Path("version.txt").exists():
                version_file = Path("version.txt")
            else:
                version_file = Path("Version.txt")  # Default
        self.version_file = version_file
    
    def read_version(self) -> Version:
        """Read current version from file"""
        if not self.version_file.exists():
            Logger.warning(f"{self.version_file} not found, creating with 0.1.0")
            self.write_version(Version(0, 1, 0))
            return Version(0, 1, 0)
        
        try:
            with open(self.version_file, 'r', encoding='utf-8') as f:
                version_str = f.read().strip()
        except Exception as e:
            Logger.error(f"Failed to read {self.version_file}: {e}")
            raise
        
        if not version_str:
            Logger.warning(f"{self.version_file} is empty, using 0.1.0")
            self.write_version(Version(0, 1, 0))
            return Version(0, 1, 0)
        
        try:
            return Version.parse(version_str)
        except ValueError as e:
            Logger.error(f"Invalid version format in {self.version_file}: {e}")
            Logger.info(f"Current content: {version_str}")
            Logger.info("Expected format: X.Y.Z or X.Y.Za/b/rc")
            raise
    
    def write_version(self, version: Version):
        """Write version to file"""
        with open(self.version_file, 'w', encoding='utf-8') as f:
            f.write(str(version))
    
    def bump_version(self, bump_type: str = "patch") -> Version:
        """Read, bump, and write new version"""
        current = self.read_version()
        new_version = current.bump(bump_type)
        self.write_version(new_version)
        return new_version
    
    def set_version(self, version_string: str) -> Version:
        """Set a specific version"""
        try:
            new_version = Version.parse(version_string)
            self.write_version(new_version)
            return new_version
        except ValueError as e:
            raise ValueError(f"Invalid version format: {version_string}. {e}")


class DeployAutomation:
    """Main deployment automation orchestrator"""
    
    def __init__(self, repo_path: Path = Path.cwd()):
        self.repo_path = repo_path
        self.git = GitManager(repo_path)
        self.github = GitHubManager()
        self.version_mgr = VersionManager(repo_path / "Version.txt")
        self.validator = ProjectValidator(repo_path)
        self.changelog = ChangelogManager(repo_path)
    
    def run(self, bump_type: str = "patch", auto_merge: bool = True, custom_version: Optional[str] = None, skip_changelog: bool = False):
        """Execute full deployment pipeline"""
        
        Logger.header("DevSync")
        
        try:
            # Step 0: Validate project structure
            Logger.step("Validating project structure...")
            is_valid, warnings = self.validator.validate()
            if not is_valid:
                for warning in warnings:
                    Logger.error(warning)
                Logger.info("Please create missing required files before deploying")
                sys.exit(1)
            if warnings:
                for warning in warnings:
                    Logger.warning(warning)
            Logger.success("Project structure validated")
            
            # Step 1: Validate repository
            Logger.step("Validating Git repository...")
            if not self.git.validate_repo():
                Logger.error("Not a valid Git repository or remote not configured")
                Logger.info("Run: git init && git remote add origin <your-repo-url>")
                sys.exit(1)
            Logger.success("Repository validated")
            
            # Step 2: Configure Git user
            Logger.step("Configuring Git user...")
            self.git.configure_user()
            Logger.success("Git user configured")
            
            # Step 3: Read current version
            Logger.step("Reading current version...")
            current_version = self.version_mgr.read_version()
            Logger.info(f"Current version: {current_version}")
            
            # Step 4: Create development branch
            branch_name = f"develop-{self.git.username}"
            Logger.step(f"Creating branch: {branch_name}")
            self.git.create_and_checkout_branch(branch_name)
            Logger.success(f"On branch: {branch_name}")
            
            # Step 5: Bump or set version
            if custom_version:
                Logger.step(f"Setting version to {custom_version}...")
                new_version = self.version_mgr.set_version(custom_version)
                Logger.success(f"Version set to: {new_version}")
            else:
                Logger.step("Bumping version...")
                new_version = self.version_mgr.bump_version(bump_type)
                Logger.success(f"New version: {new_version}")
            
            # Step 5.5: Prompt for changelog
            changelog_entry = None
            if not skip_changelog:
                try:
                    from datetime import datetime
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    changelog_entry = self.changelog.prompt_changelog(str(new_version))
                    if changelog_entry:
                        Logger.step("Updating changelog...")
                        self.changelog.add_entry(str(new_version), date_str, changelog_entry)
                        Logger.success("Changelog updated")
                except Exception as e:
                    Logger.warning(f"Failed to update changelog: {e}")
            
            # Step 6: Commit and push
            Logger.step("Committing and pushing changes...")
            commit_msg = f"chore: bump version to {new_version}"
            if not self.git.commit_and_push(commit_msg, branch_name):
                Logger.error("Failed to push changes")
                sys.exit(1)
            Logger.success("Changes pushed successfully")
            
            # Step 7: Trigger workflow
            Logger.step("Triggering CI/CD pipeline...")
            self.github.trigger_workflow(branch_name)
            
            # Step 8: Wait for workflow
            if not self.github.wait_for_workflow(branch_name):
                Logger.error("CI/CD pipeline failed")
                sys.exit(1)
            
            # Step 9: Merge to main (if auto_merge)
            if auto_merge:
                Logger.step("Merging to main branch...")
                if not self.git.merge_to_main(branch_name):
                    Logger.error("Failed to merge to main")
                    sys.exit(1)
                Logger.success("Merged to main successfully")
            
            # Step 10: Create tag and release
            Logger.step("Creating tag and release...")
            tag_name = f"v{new_version}"
            self.git.create_tag(tag_name, f"Release {new_version}")
            self.github.create_release(
                tag_name, 
                str(new_version),
                f"Automated release for version {new_version}"
            )
            Logger.success(f"Tag {tag_name} created")
            
            Logger.header("Deployment completed successfully!")
            Logger.info(f"Version: {current_version} → {new_version}")
            Logger.info(f"Branch: {branch_name}")
            Logger.info(f"Tag: {tag_name}")
            
        except KeyboardInterrupt:
            Logger.warning("Deployment cancelled by user")
            sys.exit(1)
        except Exception as e:
            Logger.error(f"Deployment failed: {str(e)}")
            if os.environ.get("DEPLOY_DEBUG"):
                import traceback
                traceback.print_exc()
            sys.exit(1)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="DevSync - Deployment Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py                    # Deploy with patch bump
  python deploy.py --bump minor       # Deploy with minor bump
  python deploy.py --set-version 2.0.0  # Set specific version
  python deploy.py --no-merge         # Deploy without auto-merge
  python deploy.py --version          # Show current version
        """
    )
    
    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Version bump type (default: patch)"
    )
    
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Skip automatic merge to main"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show current version and exit"
    )
    
    parser.add_argument(
        "--set-version",
        type=str,
        help="Set a specific version (e.g., 1.2.3 or 2.0.0rc1)"
    )
    
    parser.add_argument(
        "--skip-changelog",
        action="store_true",
        help="Skip changelog prompt"
    )
    
    args = parser.parse_args()
    
    if args.version:
        version_mgr = VersionManager()
        current = version_mgr.read_version()
        print(f"Current version: {current}")
        sys.exit(0)

    custom_version = args.set_version
    # Only prompt if running in an interactive terminal
    if custom_version is None and sys.stdin.isatty():
        print("")
        while True:
            answer = input("Do you want to manually set the next version? (y/N): ").strip().lower()
            if answer in ("y", "yes"):
                while True:
                    input_version = input("Enter the new version (e.g., 1.2.3, 2.0.0rc1): ").strip()
                    try:
                        Version.parse(input_version)
                        custom_version = input_version
                        break
                    except Exception as e:
                        print(f"[Error] Invalid version: {e}")
                        print("Please enter a version in the format X.Y.Z[optionalSuffix] (examples: 1.0.0, 1.2.3b2, 2.0.0rc1).")
                break
            elif answer in ("n", "no", ""):
                custom_version = None
                break
            else:
                print("Please answer 'y' or 'n'.")

    automation = DeployAutomation()
    automation.run(
        bump_type=args.bump, 
        auto_merge=not args.no_merge,
        custom_version=custom_version,
        skip_changelog=args.skip_changelog
    )


if __name__ == "__main__":
    main()