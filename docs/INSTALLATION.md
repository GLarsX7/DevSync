# 📦 Installation Guide - Deploy Automation Tool

Complete step-by-step guide for installing and configuring the Deploy Automation Tool on Windows, Linux, and macOS.

---

## 📋 Prerequisites

### Required Software

| Software | Minimum Version | Download |
|----------|----------------|----------|
| Python | 3.9+ | [python.org](https://www.python.org/downloads/) |
| Git | 2.0+ | [git-scm.com](https://git-scm.com/downloads) |
| pip | Latest | Included with Python |

### Optional but Recommended

- **GitHub Account** - For CI/CD and releases
- **GitHub Personal Access Token** - For API operations
- **Code Editor** - VS Code, PyCharm, etc.

---

## 🖥️ Platform-Specific Installation

### Windows

#### Step 1: Install Python

```powershell
# Download and install Python from python.org
# OR use Windows Package Manager (winget)
winget install Python.Python.3.12

# Verify installation
python --version
pip --version
```

#### Step 2: Install Git

```powershell
# Download from git-scm.com
# OR use winget
winget install Git.Git

# Verify installation
git --version
```

#### Step 3: Setup Deploy Tool

```powershell
# Navigate to your project directory
cd C:\path\to\your\project

# Download deploy scripts (replace with actual files)
# Copy deploy.py, deploy_ui.py, requirements.txt to project

# Install dependencies
pip install -r requirements.txt

# Create version.txt
echo 0.1.0 > version.txt

# Create workflow directory
mkdir .github\workflows
# Copy deploy.yml to .github\workflows\
```

#### Step 4: Configure Environment

```powershell
# Set GitHub token (Optional)
setx GITHUB_TOKEN "ghp_your_token_here"

# Restart terminal for changes to take effect
```

---

### Linux (Ubuntu/Debian)

#### Step 1: Install Python and Git

```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv git -y

# Verify installation
python3 --version
pip3 --version
git --version
```

#### Step 2: Setup Deploy Tool

```bash
# Navigate to your project
cd /path/to/your/project

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Download deploy scripts
# Copy deploy.py, deploy_ui.py, requirements.txt to project

# Install dependencies
pip install -r requirements.txt

# Create version.txt
echo "0.1.0" > version.txt

# Create workflow directory
mkdir -p .github/workflows
# Copy deploy.yml to .github/workflows/

# Make scripts executable
chmod +x deploy.py deploy_ui.py
```

#### Step 3: Configure Environment

```bash
# Add GitHub token to shell profile
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
source ~/.bashrc

# OR create .env file (add to .gitignore!)
echo "GITHUB_TOKEN=ghp_your_token_here" > .env
```

---

### macOS

#### Step 1: Install Homebrew (if not installed)

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install Python and Git

```bash
# Install Python
brew install python@3.12

# Install Git (usually pre-installed)
brew install git

# Verify installations
python3 --version
pip3 --version
git --version
```

#### Step 3: Setup Deploy Tool

```bash
# Navigate to your project
cd /path/to/your/project

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Download deploy scripts
# Copy deploy.py, deploy_ui.py, requirements.txt to project

# Install dependencies
pip install -r requirements.txt

# Create version.txt
echo "0.1.0" > version.txt

# Create workflow directory
mkdir -p .github/workflows
# Copy deploy.yml to .github/workflows/

# Make scripts executable
chmod +x deploy.py deploy_ui.py
```

#### Step 4: Configure Environment

```bash
# Add GitHub token to shell profile
# For zsh (default on macOS Catalina+)
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bash_profile
source ~/.bash_profile
```

---

## 🔑 GitHub Token Setup

### Creating a GitHub Personal Access Token

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/tokens

2. **Generate New Token**
   - Click "Generate new token (classic)"
   - Give it a descriptive name: "Deploy Automation Tool"

3. **Select Scopes**
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `write:packages` (Upload packages to GitHub Package Registry)

4. **Generate and Copy Token**
   - Click "Generate token"
   - **IMPORTANT**: Copy the token immediately (you won't see it again!)

5. **Save Token Securely**
   ```bash
   # Linux/macOS
   echo 'export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"' >> ~/.bashrc
   
   # Windows PowerShell
   setx GITHUB_TOKEN "ghp_xxxxxxxxxxxx"
   ```

---

## 📁 Project Structure Setup

### Complete File Structure

```
your-project/
├── deploy.py                 # Main deployment script
├── deploy_ui.py             # Interactive UI
├── requirements.txt         # Python dependencies
├── config.yaml              # Configuration (optional)
├── version.txt              # Version tracking
├── setup.py                 # Package setup (optional)
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
├── .github/
│   └── workflows/
│       └── deploy.yml      # CI/CD pipeline
├── tests/                  # Test files (optional)
│   ├── __init__.py
│   └── test_deploy.py
└── .venv/                  # Virtual environment (don't commit)
```

### Essential Files Checklist

- [ ] `deploy.py` - Main script
- [ ] `deploy_ui.py` - UI script (optional)
- [ ] `requirements.txt` - Dependencies
- [ ] `version.txt` - Version file
- [ ] `.github/workflows/deploy.yml` - CI/CD workflow
- [ ] `.gitignore` - Git ignore configuration

---

## ⚙️ Initial Configuration

### 1. Configure Git

```bash
# Set your name and email (if not already set)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

### 2. Initialize Git Repository (if new project)

```bash
# Initialize repository
git init

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/your-repo.git

# Create initial commit
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 3. Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# Deploy Automation
.deploy_cache/
.github_token
.env
deploy.log
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
*.egg-info/
EOF
```

### 4. Test Installation

```bash
# Test deploy script
python deploy.py --version

# Should output something like: "Current version: 0.1.0"
```

---

## 🧪 Verification Tests

### Test 1: Python Environment

```bash
python --version    # Should be 3.9 or higher
pip --version       # Should exist
```

### Test 2: Git Configuration

```bash
git --version       # Should be 2.0 or higher
git config user.name    # Should show your name
git config user.email   # Should show your email
```

### Test 3: Dependencies

```bash
pip list | grep -E "PyYAML|requests"
# Should show installed packages
```

### Test 4: Script Execution

```bash
# Test basic execution (dry run)
python deploy.py --version

# Test with UI
python deploy_ui.py --help
```

### Test 5: GitHub Integration

```bash
# Check if token is set
echo $GITHUB_TOKEN    # Linux/macOS
echo %GITHUB_TOKEN%   # Windows CMD
$env:GITHUB_TOKEN     # Windows PowerShell

# Should display your token (or blank if not set)
```

---

## 🚀 First Run

### Quick Start Deployment

```bash
# 1. Ensure version.txt exists
cat version.txt
# Should show: 0.1.0

# 2. Run deployment (dry run without push)
python deploy.py --no-merge

# 3. Check if branch was created
git branch
# Should show: develop-yourusername

# 4. Full deployment
python deploy.py
```

### Using the Interactive UI

```bash
# Launch interactive interface
python deploy_ui.py

# Follow on-screen prompts
# Watch real-time progress
```

---

## 🔧 Troubleshooting Installation

### Issue: "Python not found"

**Solution (Windows):**
```powershell
# Add Python to PATH
# During installation, check "Add Python to PATH"
# Or manually add: C:\Python312\ and C:\Python312\Scripts\
```

**Solution (Linux/macOS):**
```bash
# Create alias
echo 'alias python=python3' >> ~/.bashrc
echo 'alias pip=pip3' >> ~/.bashrc
source ~/.bashrc
```

### Issue: "pip install fails"

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with user flag
pip install --user -r requirements.txt

# Or use virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Issue: "Permission denied"

**Solution (Linux/macOS):**
```bash
# Make scripts executable
chmod +x deploy.py deploy_ui.py

# Run with python explicitly
python deploy.py
```

**Solution (Windows):**
```powershell
# Run PowerShell as Administrator if needed
# Or use: python deploy.py
```

### Issue: "Module not found"

**Solution:**
```bash
# Ensure you're in the correct directory
pwd  # Linux/macOS
cd   # Windows

# Verify requirements are installed
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Additional Resources

### Documentation
- [Python Documentation](https://docs.python.org/3/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Actions Documentation](https://docs.github.com/actions)

### Community
- GitHub Issues: Report bugs or request features
- Discussions: Ask questions and share ideas
- Wiki: Additional guides and examples

---

## ✅ Installation Checklist

Before your first deployment, verify:

- [ ] Python 3.9+ installed and accessible
- [ ] Git 2.0+ installed and configured
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `version.txt` created with initial version
- [ ] `.github/workflows/deploy.yml` in place
- [ ] GitHub token configured (optional but recommended)
- [ ] `.gitignore` configured properly
- [ ] Git repository initialized and connected to GitHub
- [ ] Test run completed successfully (`python deploy.py --version`)

---

## 🎉 Next Steps

After successful installation:

1. Read the [README.md](README.md) for usage instructions
2. Review [config.yaml](config.yaml) for customization options
3. Run your first deployment: `python deploy.py`
4. Explore the interactive UI: `python deploy_ui.py`
5. Check GitHub Actions for workflow status

**Congratulations! You're ready to deploy! 🚀**