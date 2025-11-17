# DevSync

A lightweight, developer-friendly automation tool designed to streamline the entire deployment process—from local development to production-ready releases. DevSync automatically uploads your working directory to a dedicated development branch, triggers CI/CD pipelines, tracks versioning, and publishes clean, consistent releases without manual intervention.

DevSync follows smart branching, semantic versioning, and workflow automation to ensure every deployment is predictable, traceable, and effortless. Built for teams and indie developers who want deployment automation without the weight of full DevOps stacks. Think of it as "Git deploy, but smart."

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Core Features

- **Automatic branch creation** - Creates `develop-{username}` branches automatically
- **One-command deployment** - Single command handles the entire workflow
- **CI/CD integration** - Triggers and monitors pipeline status
- **Semantic versioning** - Automatic version bumps using `version.txt`
- **Git tags & releases** - Automatic tag creation and GitHub releases
- **GitHub compatible** - Works with any GitHub repository
- **Optional UI** - Terminal interface for logs, status, and version control
- **Cross-platform** - Works on Windows, Linux, and macOS

---

## Requirements

- Python 3.9+
- Git 2.0+
- GitHub account (optional, for CI/CD)
- GitHub token (optional, for API operations)

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create version file
echo "0.1.0" > version.txt

# Run deployment
python deploy.py

# Or use the UI
python deploy_ui.py
```

Set `GITHUB_TOKEN` environment variable for full GitHub API integration (optional).

**For detailed setup and usage instructions, see [docs/USAGE.md](docs/USAGE.md)**

---

## Usage

```bash
# Basic deployment (patch bump)
python deploy.py

# Version bumps
python deploy.py --bump minor
python deploy.py --bump major

# Set specific version
python deploy.py --set-version 2.0.0

# Skip auto-merge
python deploy.py --no-merge

# Show current version
python deploy.py --version

# Interactive UI
python deploy_ui.py
```

### Version Management

Semantic versioning with pre-release support:

- Standard: `0.1.0` → `0.1.1` (patch), `0.2.0` (minor), `1.0.0` (major)
- Pre-release: `1.0.0` → `1.0.1a` → `1.0.1b` → `1.0.1rc` → `1.0.1`

Pre-release versions must follow the sequence: alpha → beta → rc → stable.

---

## Configuration

Edit `config.yaml` to customize behavior. Main settings:

```yaml
version:
  file: "version.txt"
  bump_type: "patch"

git:
  branch_pattern: "develop-{username}"
  main_branch: "main"
  auto_merge: true

github:
  token_source: "env"
  workflow:
    wait_for_completion: true
    timeout: 600
```

Environment variables:
- `GITHUB_TOKEN` - GitHub API token (optional)
- `DEPLOY_DEBUG` - Enable debug logging (optional)

---

## Workflow

1. Validate git repository
2. Configure git user if needed
3. Read current version from `version.txt`
4. Create development branch (`develop-{username}`)
5. Bump version
6. Commit and push changes
7. Trigger GitHub Actions workflow
8. Wait for CI/CD pipeline (if token provided)
9. Merge to main (if `auto_merge` enabled)
10. Create tag and release

---

## Interactive UI

Run `python deploy_ui.py` for a terminal UI showing real-time deployment progress.

---

## Security

Never commit tokens or secrets. Use environment variables:

```bash
export GITHUB_TOKEN="ghp_xxxx"
```

Add to `.gitignore`:
```
.github_token
.env
deploy.log
.deploy_cache/
```

---

## Troubleshooting

**"Not a valid Git repository"**
```bash
git init
git remote add origin <your-repo-url>
```

**"Push failed"**
```bash
git pull origin main --rebase
python deploy.py
```

**"Invalid version format"**
```bash
echo "0.1.0" > version.txt
```

**"GitHub token not found"**
Set `GITHUB_TOKEN` or use `--no-merge` to skip GitHub operations.

Enable debug logging: `export DEPLOY_DEBUG="true"`

---

## Project Structure

```
deploy.py              # Main script
deploy_ui.py           # Interactive UI
config.yaml            # Configuration
version.txt            # Version file
requirements.txt       # Dependencies
```

---

## Advanced Usage

Customize branch patterns and hooks in `config.yaml`. See `docs/EXAMPLES.md` for more examples.

---

## Testing

```bash
pytest config/test_deploy.py -v
```

---

## CI/CD

GitHub Actions workflow validates, tests, and builds on push. See `.github/workflows/` for configuration.

---

## License

MIT License

## Contributing

Pull requests welcome. See `docs/EXAMPLES.md` for usage examples.