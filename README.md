# DevSync - Desktop Deployment Automation

🚀 **Professional single-file desktop GUI application for automated deployments**

DevSync is a comprehensive deployment automation tool with a modern PyQt6 interface that handles version management, Git operations, GitHub releases, and CI/CD integration—all from a beautiful desktop application.

## ✨ Features

### 🎯 Core Functionality
- **Single-File Architecture**: Everything in one Python file (`devsync_gui.py`)
- **7-Step Deployment Wizard**: Guided deployment process with visual feedback
- **Version Management**: Semantic versioning with alpha/beta/RC support
- **Git Integration**: Automated branching, committing, and merging
- **GitHub Releases**: Create releases with changelogs and assets
- **Deployment History**: Track all deployments with rollback capability
- **Real-time Progress**: Live logs and progress indicators

### 🖥️ User Interface
- **Dashboard**: Current version, git status, and recent activity at a glance
- **Releases Manager**: View and manage GitHub releases
- **Changelog Editor**: Split-pane editor with live markdown preview
- **Version History**: Timeline view with one-click rollback
- **Settings Panel**: Configure Git, GitHub, and UI preferences
- **System Tray**: Quick access from system tray icon
- **Dark/Light Themes**: Professional themes for any preference

### 🔒 Security
- **Secure Token Storage**: GitHub tokens stored in system keyring
- **No Hardcoded Credentials**: All sensitive data stored securely
- **Environment Variables**: Fallback to environment variables

### 📦 Deployment Wizard Steps

1. **Version Bump Selector**: Choose Major/Minor/Patch or set custom version
2. **Changelog Editor**: Write release notes with live markdown preview
3. **Review Changes**: Visual diff of files to be committed
4. **Options**: Configure auto-merge, draft release, pre-release flags
5. **Confirmation**: Review deployment summary before proceeding
6. **Progress**: Real-time deployment with live logs
7. **Results**: Success confirmation with GitHub release link

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/devsync.git
cd devsync

# Install dependencies
pip install -r requirements.txt
```

### First Run

```bash
# Launch the GUI
python devsync_gui.py
```

### Initial Setup

1. **Configure Git** (if not already configured):
   - Go to Settings tab
   - Enter your name and email
   
2. **Add GitHub Token** (optional but recommended):
   - Go to Settings tab
   - Enter your GitHub Personal Access Token
   - Click "Save Token" (stored securely in system keyring)
   
3. **Start Deploying**:
   - Click "Deploy Now" button
   - Follow the 7-step wizard
   - Done! 🎉

## 📋 Requirements

### Required
- Python 3.8+
- PyQt6 >= 6.6.0
- GitPython >= 3.1.40
- PyYAML >= 6.0.1

### Optional (but recommended)
- PyGithub >= 2.1.1 (for GitHub releases)
- markdown >= 3.5.0 (for changelog preview)
- keyring >= 24.3.0 (for secure token storage)

## 🎨 Screenshots

### Dashboard
The main dashboard shows your current version, git status, and recent deployment activity.

### Deployment Wizard
Step-by-step guided deployment with visual feedback at every stage.

### Changelog Editor
Split-pane editor with live markdown preview for writing release notes.

### Version History
Complete deployment history with one-click rollback to any previous version.

## 📦 Building Standalone Executable

### Windows
```bash
pyinstaller --name="DevSync" --windowed --onefile devsync_gui.py
```

Result: `dist/DevSync.exe` (single executable, no Python required)

### macOS
```bash
pyinstaller --name="DevSync" --windowed --onefile devsync_gui.py
```

Result: `dist/DevSync.app`

### Linux
```bash
pyinstaller --name="DevSync" --windowed --onefile devsync_gui.py
```

Result: `dist/DevSync`

## 🔧 Configuration

### Project Files

DevSync expects the following files in your project:

**Required:**
- `version.txt` - Current version (created automatically if missing)

**Recommended:**
- `CHANGELOG.md` - Changelog (created automatically)
- `README.md` - Project documentation
- `LICENSE` - License file

### Version Format

Versions follow semantic versioning with optional suffixes:
- `1.0.0` - Stable release
- `1.0.0a` - Alpha release
- `1.0.0b` - Beta release
- `1.0.0rc1` - Release candidate

### Version Bumping Logic

- **Alpha → Beta → RC → Stable**: Automatic progression
- **Stable → Patch**: `1.0.0` → `1.0.1`
- **Stable → Minor**: `1.0.0` → `1.1.0`
- **Stable → Major**: `1.0.0` → `2.0.0`

## 🎯 Usage Examples

### Basic Deployment

1. Click "Deploy Now"
2. Select version bump type (Patch/Minor/Major)
3. Write changelog entry
4. Review changes
5. Configure options
6. Confirm and deploy
7. View results with GitHub release link

### Custom Version

1. Click "Deploy Now"
2. Enter custom version (e.g., `2.0.0rc1`)
3. Continue with wizard

### Rollback

1. Go to History tab
2. Right-click on version
3. Select "Rollback to this version"
4. Confirm

### Managing Releases

1. Go to Releases tab
2. Click "Refresh" to load from GitHub
3. View all releases with details
4. Upload assets (drag & drop)

## 🔐 GitHub Token Setup

### Creating a Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Action workflows)
4. Generate and copy token
5. Paste into DevSync Settings → GitHub Token
6. Click "Save Token"

Token is stored securely in your system keyring.

## 📊 Features Comparison

| Feature | CLI (`deploy.py`) | TkInter UI (`deploy_ui.py`) | PyQt6 GUI (`devsync_gui.py`) |
|---------|-------------------|------------------------------|------------------------------|
| Version Management | ✅ | ✅ | ✅ |
| Git Operations | ✅ | ✅ | ✅ |
| GitHub Releases | ⚠️ Basic | ⚠️ Basic | ✅ Full |
| Changelog Editor | ❌ | ❌ | ✅ |
| Deployment History | ❌ | ❌ | ✅ |
| Rollback | ❌ | ❌ | ✅ |
| Release Manager | ❌ | ❌ | ✅ |
| System Tray | ❌ | ❌ | ✅ |
| Themes | ❌ | ❌ | ✅ |
| Secure Storage | ❌ | ❌ | ✅ |
| Deployment Wizard | ❌ | ⚠️ Basic | ✅ 7-Step |
| Live Preview | ❌ | ❌ | ✅ |

## 🛠️ Development

### Project Structure

```
devsync/
├── devsync_gui.py          # Single-file GUI application (MAIN)
├── deploy.py               # Legacy CLI tool
├── deploy_ui.py            # Legacy TkInter UI
├── version.txt             # Current version
├── version_history.json    # Deployment history
├── CHANGELOG.md            # Changelog
├── config.yaml             # Configuration (optional)
├── requirements.txt        # Dependencies
└── README.md               # This file
```

### Code Organization (within devsync_gui.py)

- **Data Models**: Version, DeploymentRecord, GitHubRelease
- **Core Managers**: VersionManager, GitManager, GitHubManager, ChangelogManager
- **Worker Thread**: DeploymentWorker (background operations)
- **Wizard Pages**: 7 wizard pages for deployment
- **Main Window**: DevSyncMainWindow with tabs
- **Entry Point**: main() function

## 🐛 Troubleshooting

### "No module named PyQt6"
```bash
pip install PyQt6
```

### "GitHub token not working"
- Ensure token has `repo` and `workflow` scopes
- Check token hasn't expired
- Try re-saving in Settings

### "Git operations failing"
- Ensure you're in a git repository
- Check remote is configured: `git remote -v`
- Verify you have push access

### "Keyring not available"
```bash
pip install keyring
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/devsync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/devsync/discussions)

## 🎉 Acknowledgments

Built with:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API
- [GitPython](https://github.com/gitpython-developers/GitPython) - Git integration
- [keyring](https://github.com/jaraco/keyring) - Secure storage

---

**Made with ❤️ for developers who love automation**