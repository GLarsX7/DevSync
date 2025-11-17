# Examples

Common usage scenarios for DevSync.

---

## Basic Usage

```bash
# First deployment
echo "0.1.0" > version.txt
python deploy.py

# Minor version bump
python deploy.py --bump minor

# Major version bump
python deploy.py --bump major
```

---

## Pre-release Versions

```bash
# Start with stable
echo "1.0.0" > version.txt

# Alpha release
python deploy.py  # → 1.0.1a

# Continue through beta, rc, stable
python deploy.py  # → 1.0.1b
python deploy.py  # → 1.0.1rc
python deploy.py  # → 1.0.1
```

---

## CI/CD Integration

```bash
# Full deployment with auto-merge
python deploy.py

# Deploy without auto-merge (for manual review)
python deploy.py --no-merge
```

---

## Interactive UI

```bash
python deploy_ui.py
```

Shows real-time deployment progress in the terminal.

---

## Custom Configuration

Edit `config.yaml` to change branch patterns, merge behavior, etc. Most settings are hardcoded for now - config loading is planned.

---

## Troubleshooting

**CI Pipeline Failed**
- Check GitHub Actions for errors
- Fix issues and push again
- CI will re-run automatically

**Merge Conflicts**
- Resolve manually: `git checkout main && git merge develop-{username}`
- Fix conflicts, commit, push
- Create tag manually if needed

**Rollback**
- Manually set version in `version.txt`
- Commit and deploy

---

## Common Workflows

**Python Project**
```bash
# After making changes
pytest  # run tests locally
python deploy.py  # deploy
```

**Multiple Developers**
- Each developer gets their own `develop-{username}` branch
- Versions increment independently
- Merge to main when ready

---

## Debug Mode

```bash
export DEPLOY_DEBUG="true"
python deploy.py
```

Shows detailed error traces when things go wrong.

## Tips

**Quick aliases** (add to `.bashrc` or `.zshrc`):
```bash
# Add to ~/.bashrc or ~/.zshrc
alias deploy='python deploy.py'
alias deploy-minor='python deploy.py --bump minor'
```

**Test version bump without deploying:**
```python
from deploy import Version, VersionManager
vm = VersionManager()
current = vm.read_version()
print(f'Next: {current.bump("minor")}')
```