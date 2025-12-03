# Changelog

All notable changes to this project will be documented in this file.

## [1.0.3] - 2025-12-03 - "Modernizer"

### ✨ New Features

- **Modern UI**: Implemented a modern, clean, and responsive UI using `tkinter` and `ttkbootstrap`.
- **Dark/Light Theme**: Added support for dark and light themes with system tray integration.
- **System Tray**: Added system tray integration with quick actions (deploy, rollback, settings).
- **Version History**: Added a timeline view of all deployments with deployment details (version, date, user, status).
- **Settings Panel**: Added a settings panel with Git configuration (user name, email), GitHub token management with secure storage, UI theme selection (dark/light), and auto-save preferences.
- **Security**: Added secure token storage using system keyring.

## [1.0.2d] - 2025-12-02 - "Release Master"

### 🎉 Major Achievement

- **GitHub Releases Working**: Successfully resolved all GitHub token authentication issues and confirmed release creation functionality!

### 🐛 Bug Fixes

- **Token Authentication**: Fixed "401 Bad credentials" error by implementing proper token validation and debugging.
- **Token Storage**: Enhanced `TokenManager` with better error handling and validation.
- **Release Creation**: Added comprehensive logging to diagnose and fix release creation issues.
- **Token Validation**: Added token length validation (GitHub tokens are 40+ characters) to prevent invalid tokens.

### 🔧 Improvements

- **Detailed Logging**: Added emoji-based logging for better visibility of deployment steps:
  - 📦 Repository access
  - 🏷️ Tag information
  - ✅ Success indicators
  - ❌ Error details
- **Token Debugging**: Added token preview display (first 8 + last 4 characters) for troubleshooting.
- **Error Messages**: Enhanced error messages with specific HTTP status codes and actionable guidance.

### 📦 Build System

- **MANIFEST.in**: Created manifest file to ensure `version.txt` is included in distribution packages.
- **setup.py**: Added proper setup file in root directory for PyPI distribution.

### 📚 Documentation

- **Token Permissions**: Clarified required permissions for Fine-grained tokens (Contents: Read and write).

## [1.0.2c] - 2025-12-02 - "Customizer"

### ✨ New Features


- **Custom Version Suffixes**: Version system now supports any custom suffix (e.g., `1.0.2c`, `2.0.0-beta`, `1.5.0-alpha.1`), not just predefined `a`, `b`, `rc` types.
- **Test Suite**: Implemented comprehensive unit tests for core functionality (`Version`, `VersionManager`, `TokenManager`).
- **Custom Release Titles**: Added input field in deployment wizard to specify custom release names.

### 🔧 CI/CD Improvements

- **Automated Testing**: Tests now run automatically in CI/CD pipeline across multiple Python versions (3.9-3.12) and operating systems (Ubuntu, Windows, macOS).
- **Test Result Validation**: Enhanced test job with proper error handling and result validation.
- **Coverage Reporting**: Integrated code coverage reporting with Codecov.

### 🐛 Bug Fixes

- **Fine-grained Token Support**: Fixed crash when testing Fine-grained Personal Access Tokens (which return `None` for scopes).
- **Token Scope Detection**: Improved handling of tokens without OAuth scopes.

### 📚 Documentation

- **Confirmation Summary**: Release title now displayed in deployment confirmation step.

## [1.0.0b] - 2025-12-02

### ✨ Enhancements

- **Secure Token Management**: Implemented `TokenManager` with a robust fallback system. Tokens are now stored in the system keyring if available, or securely in a hidden local file (`.devsync_token`) as a backup.
- **Token Verification**: Added a **"Test Token"** button in the Settings tab to instantly verify GitHub authentication and check for required scopes (`repo`).
- **Diagnostic Logging**: Added detailed logging of token scopes to help troubleshoot permission issues.

### 🐛 Bug Fixes

- **Class Scope Issue**: Resolved a critical `AttributeError` caused by incorrect class nesting, restoring functionality to the deployment wizard and main window methods.
- **Import Restoration**: Fixed missing dependency imports that were causing runtime crashes.

### 📚 Documentation

- **Quick Start Guide**: Updated `QUICKSTART.md` with precise instructions on configuring GitHub Personal Access Tokens (Classic vs. Fine-grained) and required permissions.

## [1.0.0a] - 2025-12-02

### 🐛 Bug Fixes

- **GitHub Authentication**: Fixed `DeprecationWarning` by migrating to `github.Auth.Token`.
- **Error Handling**: Added clear error messages for `403 Forbidden` (permission) errors during release creation.
- **Dependencies**: Restored missing imports (`git`, `yaml`, `markdown`) that were causing runtime errors.
- **Code Cleanup**: Removed duplicate `GitHubManager` class definition.

## [1.0.0] - 2025-12-02

### 🎉 Major Release - Complete GUI Transformation

**DevSync is now a professional single-file desktop application!**

#### ✨ New Features

**Single-File Architecture**
- Merged all functionality into `devsync_gui.py` (single Python file)
- Self-contained application with embedded resources
- No CLI mode - everything through beautiful GUI

**7-Step Deployment Wizard**
- Version bump selector with visual preview
- Changelog editor with live markdown preview
- Visual diff of changes to be committed
- Deployment options (auto-merge, draft, pre-release)
- Confirmation summary before deployment
- Real-time progress with live logs
- Results page with GitHub release link

**Main Window Features**
- Dashboard showing current version, git status, deployment history
- One-click "Deploy Now" button
- Real-time progress indicators
- System tray integration with quick actions
- Dark/light theme support

**Releases Manager**
- List and manage all GitHub releases
- View release details (tag, date, type, URL)
- Upload build artifacts (drag & drop)
- Filter and search releases

**Changelog Editor**
- Split-pane interface (edit | preview)
- Live markdown preview
- Syntax highlighting
- Save directly from UI

**Version History**
- Timeline view of all deployments
- Deployment details (version, date, user, status)
- One-click rollback to any version
- Success/failure indicators

**Settings Panel**
- Git configuration (user name, email)
- GitHub token management with secure storage
- UI theme selection (dark/light)
- Auto-save preferences

**Security**
- Secure token storage using system keyring
- No hardcoded credentials
- Environment variable fallback
- Encrypted storage on all platforms

#### 🔧 Technical Improvements

- **PyQt6 Framework**: Modern, professional cross-platform UI
- **Threaded Operations**: Non-blocking deployment process
- **Signal/Slot Architecture**: Responsive UI updates
- **QSettings Integration**: Persistent user preferences
- **System Tray**: Background operation support
- **Error Handling**: Comprehensive error dialogs with retry options
- **Logging**: Detailed logs with color-coded severity levels

#### 📦 Dependencies Added

- PyQt6 >= 6.6.0 (GUI framework)
- PyGithub >= 2.1.1 (GitHub API integration)
- GitPython >= 3.1.40 (Git operations)
- markdown >= 3.5.0 (Changelog preview)
- keyring >= 24.3.0 (Secure token storage)
- pyinstaller >= 6.3.0 (Executable building)

#### 📚 Documentation

- Complete README.md rewrite
- QUICKSTART.md for new users
- PyInstaller spec file for building
- Windows build script (build.bat)
- Comprehensive inline documentation

#### 🎨 UI/UX

- Professional color scheme
- Responsive layouts
- Progress animations
- Status indicators
- Tooltips and help text
- Keyboard navigation
- Context menus

#### 🚀 Deployment

- Single executable build support
- Windows: DevSync.exe
- macOS: DevSync.app
- Linux: DevSync binary
- No Python required on target machines

#### 🔄 Migration from Previous Versions

- `deploy.py` - Legacy CLI (still available)
- `deploy_ui.py` - Legacy TkInter UI (deprecated)
- `devsync_gui.py` - **New PyQt6 GUI (recommended)**

All previous functionality is preserved and enhanced in the new GUI.

#### ⚠️ Breaking Changes

- No CLI mode in `devsync_gui.py` (use `deploy.py` for CLI)
- Configuration now stored in QSettings (not config.yaml)
- GitHub token must be set in Settings or environment variable

#### 🐛 Bug Fixes

- Fixed version parsing for all suffix types
- Improved git branch handling
- Better error messages
- Resolved race conditions in async operations

---

## [0.0.1a] - 2025-11-17

Errors fix:
- "tests folder not found" on MacOS and Windows

## [0.0.1] - 2025-11-17

Base project structure and workflow