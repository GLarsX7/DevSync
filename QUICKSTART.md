# DevSync Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- PyQt6 (GUI framework)
- PyGithub (GitHub API)
- GitPython (Git operations)
- markdown (Changelog preview)
- keyring (Secure storage)
- And more...

### Step 2: Launch DevSync

```bash
python devsync_gui.py
```

The application window will open showing the dashboard.

### Step 3: Configure GitHub Token (Optional)

For GitHub release creation:

1. Click the **Settings** tab
2. Enter your GitHub Personal Access Token
3. Click **Save Token**

> **How to get a token:**
> - Go to GitHub → Settings → Developer settings → Personal access tokens
> - Generate new token with `repo` and `workflow` scopes
> - Copy and paste into DevSync

### Step 4: Your First Deployment

1. Click the big **Deploy Now** button
2. Follow the wizard:
   - **Version Bump**: Select Patch/Minor/Major
   - **Changelog**: Write what changed
   - **Review**: Check files to be committed
   - **Options**: Configure settings
   - **Confirm**: Review summary
   - **Deploy**: Watch it happen!
   - **Results**: Get your GitHub release link

### Step 5: Explore Features

- **Dashboard**: See current version and git status
- **Releases**: Manage GitHub releases
- **Changelog**: Edit CHANGELOG.md with live preview
- **History**: View all deployments, rollback if needed
- **Settings**: Configure Git, GitHub, and themes

## 🎯 Common Tasks

### Deploy a Patch Version (1.0.0 → 1.0.1)

1. Click **Deploy Now**
2. Select **Patch**
3. Write changelog
4. Click through wizard
5. Done!

### Deploy a Major Version (1.0.0 → 2.0.0)

1. Click **Deploy Now**
2. Select **Major**
3. Write changelog
4. Click through wizard
5. Done!

### Set a Custom Version (e.g., 2.0.0rc1)

1. Click **Deploy Now**
2. Enter `2.0.0rc1` in custom version field
3. Write changelog
4. Click through wizard
5. Done!

### Rollback to Previous Version

1. Go to **History** tab
2. Right-click on version you want
3. Select **Rollback to this version**
4. Confirm
5. Done!

### Edit Changelog

1. Go to **Changelog** tab
2. Edit in left pane
3. See preview in right pane
4. Click **Save**
5. Done!

### View GitHub Releases

1. Go to **Releases** tab
2. Click **Refresh**
3. See all your releases
4. Click URLs to open in browser

## 🎨 Customization

### Change Theme

1. Go to **Settings** tab
2. Select **Dark** or **Light** from Theme dropdown
3. Theme changes immediately

### Configure Git User

1. Go to **Settings** tab
2. Enter your name and email
3. These will be used for commits

## 🔧 Troubleshooting

### "No module named PyQt6"

```bash
pip install PyQt6
```

### "GitHub API not working"

- Make sure you saved your GitHub token in Settings
- Check token has `repo` and `workflow` scopes
- Token might be expired - generate a new one

### "Git push failed"

- Make sure you have push access to the repository
- Check you're connected to the internet
- Verify remote is configured: `git remote -v`

### "Can't save token"

```bash
pip install keyring
```

## 📦 Building Standalone Executable

### Windows

```bash
# Easy way - use the build script
build.bat

# Manual way
pyinstaller --name="DevSync" --windowed --onefile devsync_gui.py
```

Result: `dist\DevSync.exe`

### macOS / Linux

```bash
pyinstaller --name="DevSync" --windowed --onefile devsync_gui.py
```

Result: `dist/DevSync` or `dist/DevSync.app`

## 💡 Tips & Tricks

### System Tray

- DevSync adds an icon to your system tray
- Right-click for quick actions
- Click to show/hide window

### Keyboard Shortcuts

- `Ctrl+D` - Start deployment (when implemented)
- `Ctrl+R` - Refresh dashboard (when implemented)
- `Ctrl+Q` - Quit application (when implemented)

### Deployment History

- All deployments are saved to `version_history.json`
- You can manually edit this file if needed
- Rollback creates a new deployment record

### Version Format

- `1.0.0` - Stable
- `1.0.0a` - Alpha
- `1.0.0b` - Beta  
- `1.0.0rc1` - Release Candidate 1

Alpha → Beta → RC → Stable (automatic progression)

## 🎓 Best Practices

### Before Deploying

1. ✅ Commit all your changes
2. ✅ Test your code
3. ✅ Write meaningful changelog entries
4. ✅ Review the files that will be committed

### Changelog Writing

Good changelog entry:
```
- Added user authentication system
- Fixed bug in payment processing
- Improved database query performance by 50%
- Updated dependencies to latest versions
```

Bad changelog entry:
```
- Fixed stuff
- Updates
```

### Version Bumping

- **Patch** (1.0.0 → 1.0.1): Bug fixes, small changes
- **Minor** (1.0.0 → 1.1.0): New features, backwards compatible
- **Major** (1.0.0 → 2.0.0): Breaking changes

### GitHub Releases

- Use **Draft** for releases you want to review before publishing
- Use **Pre-release** for beta/RC versions
- Add detailed release notes
- Upload build artifacts if you have them

## 🆘 Getting Help

- Check the main README.md for detailed documentation
- Look at deployment logs in the wizard
- Check version_history.json for past deployments
- Review git log: `git log --oneline`

## 🎉 You're Ready!

You now know everything you need to use DevSync effectively. Happy deploying! 🚀

---

**Need more help?** Check the full README.md or open an issue on GitHub.
