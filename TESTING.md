# DevSync Installation & Testing Guide

## 📦 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- PyQt6 (GUI framework)
- PyGithub (GitHub API)
- GitPython (Git operations)
- PyYAML (Configuration)
- markdown (Preview support)
- keyring (Secure storage)
- requests (HTTP)
- pyinstaller (Executable building)

### Step 2: Verify Installation

```bash
python -c "import PyQt6; print('PyQt6:', PyQt6.__version__)"
python -c "import github; print('PyGithub: OK')"
python -c "import git; print('GitPython: OK')"
```

### Step 3: Launch Application

```bash
python devsync_gui.py
```

## 🧪 Testing

### Manual Testing Checklist

#### ✅ Application Launch
- [ ] Application window opens
- [ ] No errors in console
- [ ] Dashboard loads correctly
- [ ] All tabs are accessible

#### ✅ Dashboard
- [ ] Current version displays correctly
- [ ] Git status shows current branch
- [ ] Git status shows clean/modified state
- [ ] Recent activity list populates (if history exists)

#### ✅ Deployment Wizard
- [ ] "Deploy Now" button opens wizard
- [ ] Step 1: Version bump options work
- [ ] Step 1: Custom version input validates
- [ ] Step 2: Changelog editor accepts text
- [ ] Step 2: Markdown preview works (if markdown installed)
- [ ] Step 3: Review shows git status
- [ ] Step 4: Options checkboxes work
- [ ] Step 5: Confirmation shows summary
- [ ] Step 6: Progress bar updates
- [ ] Step 6: Logs appear in real-time
- [ ] Step 7: Results show success/failure

#### ✅ Releases Tab
- [ ] Refresh button works
- [ ] Releases table populates (if GitHub token set)
- [ ] Release details display correctly

#### ✅ Changelog Tab
- [ ] Editor loads CHANGELOG.md
- [ ] Text editing works
- [ ] Preview updates (if markdown installed)
- [ ] Save button works

#### ✅ History Tab
- [ ] History tree populates (if history exists)
- [ ] Right-click context menu appears
- [ ] Rollback option works

#### ✅ Settings Tab
- [ ] Git user fields editable
- [ ] GitHub token field works
- [ ] Save token button works (if keyring installed)
- [ ] Theme dropdown changes theme
- [ ] Theme persists after restart

#### ✅ System Tray
- [ ] Tray icon appears
- [ ] Right-click shows menu
- [ ] Show action works
- [ ] Deploy action works
- [ ] Quit action works

#### ✅ Themes
- [ ] Light theme displays correctly
- [ ] Dark theme displays correctly
- [ ] Theme change is immediate
- [ ] Theme persists after restart

### Automated Testing

Create `test_devsync_gui.py`:

```python
import sys
import pytest
from PyQt6.QtWidgets import QApplication
from devsync_gui import DevSyncMainWindow, Version, VersionManager

@pytest.fixture
def app():
    """Create QApplication instance"""
    app = QApplication(sys.argv)
    yield app
    app.quit()

def test_version_parsing():
    """Test version parsing"""
    v1 = Version.parse("1.0.0")
    assert v1.major == 1
    assert v1.minor == 0
    assert v1.patch == 0
    
    v2 = Version.parse("2.5.3rc1")
    assert v2.major == 2
    assert v2.minor == 5
    assert v2.patch == 3

def test_version_bumping():
    """Test version bumping"""
    v = Version(1, 0, 0)
    
    # Patch bump
    v_patch = v.bump("patch")
    assert str(v_patch) == "1.0.1"
    
    # Minor bump
    v_minor = v.bump("minor")
    assert str(v_minor) == "1.1.0"
    
    # Major bump
    v_major = v.bump("major")
    assert str(v_major) == "2.0.0"

def test_main_window_creation(app):
    """Test main window can be created"""
    window = DevSyncMainWindow()
    assert window is not None
    assert window.windowTitle() == "DevSync - Deployment Automation"

def test_version_manager():
    """Test version manager"""
    vm = VersionManager()
    current = vm.read_version()
    assert isinstance(current, Version)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Run tests:
```bash
pytest test_devsync_gui.py -v
```

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError: No module named 'PyQt6'

**Solution:**
```bash
pip install PyQt6
```

### Issue: ModuleNotFoundError: No module named 'github'

**Solution:**
```bash
pip install PyGithub
```

### Issue: ModuleNotFoundError: No module named 'git'

**Solution:**
```bash
pip install GitPython
```

### Issue: Application window is blank

**Possible causes:**
1. Theme issue - try changing theme in Settings
2. Qt platform plugin issue - try setting environment variable:
   ```bash
   set QT_QPA_PLATFORM=windows  # Windows
   export QT_QPA_PLATFORM=xcb   # Linux
   ```

### Issue: GitHub token not saving

**Solution:**
```bash
pip install keyring
```

If keyring still doesn't work, use environment variable:
```bash
set GITHUB_TOKEN=your_token_here  # Windows
export GITHUB_TOKEN=your_token_here  # Linux/Mac
```

### Issue: Deployment fails

**Check:**
1. Are you in a git repository? `git status`
2. Is remote configured? `git remote -v`
3. Do you have push access?
4. Is GitHub token valid?
5. Check deployment logs in wizard

### Issue: Can't build executable

**Solution:**
```bash
pip install pyinstaller
```

Then run:
```bash
build.bat  # Windows
```

## 🔍 Debug Mode

Enable debug logging:

```python
# Add to top of devsync_gui.py after imports
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or run with Python debug mode:
```bash
python -v devsync_gui.py
```

## 📊 Performance Testing

### Memory Usage

```bash
# Windows
tasklist | findstr python

# Linux/Mac
ps aux | grep python
```

### Startup Time

```python
import time
start = time.time()
# ... application code ...
print(f"Startup time: {time.time() - start:.2f}s")
```

## ✅ Pre-Release Checklist

Before building final executable:

- [ ] All tests pass
- [ ] No console errors
- [ ] All features work
- [ ] Documentation is complete
- [ ] Version number is correct
- [ ] CHANGELOG is updated
- [ ] README is accurate
- [ ] Dependencies are listed
- [ ] Build script works
- [ ] Executable runs on clean machine

## 🚀 Build Process

### Development Build

```bash
python devsync_gui.py
```

### Production Build

```bash
# Windows
build.bat

# Linux/Mac
pyinstaller --name="DevSync" --windowed --onefile devsync_gui.py
```

### Test Executable

```bash
# Windows
dist\DevSync.exe

# Linux/Mac
dist/DevSync
```

## 📝 Test Results Template

```
DevSync v1.0.0 Test Results
Date: YYYY-MM-DD
Tester: Your Name
Platform: Windows 10 / macOS / Linux

✅ PASS | ❌ FAIL | ⚠️ PARTIAL

[ ] Application Launch
[ ] Dashboard Display
[ ] Deployment Wizard
[ ] Version Management
[ ] Git Operations
[ ] GitHub Integration
[ ] Changelog Editor
[ ] History & Rollback
[ ] Settings
[ ] System Tray
[ ] Themes
[ ] Build Executable

Notes:
- 
- 
- 

Issues Found:
1. 
2. 
3. 
```

## 🎯 Next Steps

After successful testing:

1. ✅ Fix any bugs found
2. ✅ Update documentation
3. ✅ Build final executable
4. ✅ Test on clean machine
5. ✅ Create GitHub release
6. ✅ Distribute to users

---

**Happy Testing! 🧪**
