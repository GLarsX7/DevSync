# How to Use DevSync

## How It Works

DevSync automates the version bumping and deployment process:

1. **Reads** your current version from `version.txt`
2. **Creates** a development branch (`develop-{your-username}`)
3. **Bumps** the version (patch/minor/major)
4. **Commits** and **pushes** the changes
5. **Triggers** GitHub Actions workflow (if configured)
6. **Merges** to main branch (optional)
7. **Creates** a git tag for the release

## Quick Setup (Current Project)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Version File

```bash
echo "0.1.0" > version.txt
```

### 3. Make Sure Git is Configured

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 4. Run Deployment

```bash
# Basic deployment (patch bump: 0.1.0 → 0.1.1)
python deploy.py

# Or with UI
python deploy_ui.py
```

## Adding to Other Projects

### Option 1: Copy Files to Your Project

Copy these files to your project root:

```
your-project/
├── deploy.py              # Copy this
├── deploy_ui.py           # Copy this (optional)
├── config.yaml            # Copy this (optional)
├── requirements.txt       # Add dependencies to your existing one
└── version.txt            # Create this file
```

**Steps:**

1. **Copy the deploy scripts:**
   ```bash
   cp deploy.py /path/to/your/project/
   cp deploy_ui.py /path/to/your/project/  # optional
   cp config.yaml /path/to/your/project/   # optional
   ```

2. **Add dependencies to your project:**
   ```bash
   # Add to your requirements.txt or install directly:
   pip install PyYAML requests
   ```

3. **Create version.txt in your project:**
   ```bash
   cd /path/to/your/project
   echo "0.1.0" > version.txt
   ```

4. **Make sure you're in a git repository:**
   ```bash
   git init  # if not already a git repo
   git remote add origin <your-repo-url>  # if needed
   ```

5. **Run it:**
   ```bash
   python deploy.py
   ```

### Option 2: Install as a Package (Advanced)

If you want to use it from anywhere:

1. **Install in development mode:**
   ```bash
   cd /path/to/deployer
   pip install -e .
   ```

2. **Use from any project:**
   ```bash
   cd /path/to/your/project
   echo "0.1.0" > version.txt
   deploy  # or deploy-ui
   ```

## Common Usage Patterns

### Basic Deployment

```bash
# Patch bump (0.1.0 → 0.1.1)
python deploy.py

# Minor bump (0.1.0 → 0.2.0)
python deploy.py --bump minor

# Major bump (0.1.0 → 1.0.0)
python deploy.py --bump major
```

### Without Auto-Merge

If you want to review before merging to main:

```bash
python deploy.py --no-merge
```

This will:
- Create the branch
- Bump version
- Push changes
- **Skip** the automatic merge to main

You can then review and merge manually via GitHub.

### Check Current Version

```bash
python deploy.py --version
```

## GitHub Integration (Optional)

For full GitHub integration (releases, workflow status):

1. **Create a GitHub Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Select scopes: `repo`, `workflow`

2. **Set environment variable:**
   ```bash
   # Linux/macOS
   export GITHUB_TOKEN="ghp_your_token_here"
   
   # Windows PowerShell
   $env:GITHUB_TOKEN="ghp_your_token_here"
   
   # Windows CMD
   set GITHUB_TOKEN=ghp_your_token_here
   ```

3. **Or add to your shell profile** (Linux/macOS):
   ```bash
   echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
   source ~/.bashrc
   ```

**Note:** Without the token, the tool still works but:
- Won't wait for CI/CD pipeline completion
- Won't create GitHub releases (only git tags)

## GitHub Actions Setup

To enable CI/CD, create `.github/workflows/deploy.yml` in your project:

```yaml
name: Deploy

on:
  push:
    branches: [ develop-* ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest  # or your test command
```

## Project Structure After Setup

```
your-project/
├── deploy.py              # Deploy script
├── deploy_ui.py           # UI version (optional)
├── config.yaml            # Config (optional)
├── version.txt            # Current version (required)
├── .github/
│   └── workflows/
│       └── deploy.yml     # CI/CD workflow (optional)
└── ... (your project files)
```

## Troubleshooting

### "Not a valid Git repository"
```bash
git init
git remote add origin <your-repo-url>
```

### "Push failed"
```bash
git pull origin main --rebase
python deploy.py
```

### "Invalid version format"
Make sure `version.txt` contains a valid version:
```bash
echo "0.1.0" > version.txt
```

### "GitHub token not found"
Either:
- Set `GITHUB_TOKEN` environment variable, or
- Use `--no-merge` flag to skip GitHub operations

## Example Workflow

```bash
# 1. Make your code changes
vim src/main.py

# 2. Test locally
pytest

# 3. Deploy (bumps version, creates branch, pushes)
python deploy.py

# 4. Tool automatically:
#    - Creates develop-{username} branch
#    - Bumps version in version.txt
#    - Commits and pushes
#    - Triggers CI/CD
#    - Merges to main (if auto_merge enabled)
#    - Creates tag
```

## Tips

1. **Start with `--no-merge`** until you're comfortable with the workflow
2. **Check your git status** before deploying: `git status`
3. **Use the UI** for visual feedback: `python deploy_ui.py`
4. **Enable debug mode** if something goes wrong: `export DEPLOY_DEBUG="true"`

