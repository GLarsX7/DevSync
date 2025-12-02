# DevSync Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     DevSync GUI Application                  │
│                    (devsync_gui.py - Single File)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         Application Entry Point          │
        │              main()                      │
        │  - Initialize QApplication               │
        │  - Check dependencies                    │
        │  - Create main window                    │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │        DevSyncMainWindow                 │
        │  - Menu bar                              │
        │  - Tab widget                            │
        │  - System tray                           │
        │  - Theme management                      │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴──────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────┐                            ┌──────────────┐
│   UI Tabs    │                            │   Managers   │
└──────────────┘                            └──────────────┘
        │                                             │
        ├─ Dashboard                                  ├─ VersionManager
        ├─ Releases                                   ├─ GitManager
        ├─ Changelog                                  ├─ GitHubManager
        ├─ History                                    └─ ChangelogManager
        └─ Settings
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │       Deployment Wizard (QWizard)        │
        │  1. VersionBumpPage                      │
        │  2. ChangelogPage                        │
        │  3. ReviewPage                           │
        │  4. OptionsPage                          │
        │  5. ConfirmationPage                     │
        │  6. ProgressPage                         │
        │  7. ResultsPage                          │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │      DeploymentWorker (QThread)          │
        │  - Background deployment execution       │
        │  - Signals for progress updates          │
        │  - Non-blocking operations               │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴──────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────┐                            ┌──────────────┐
│  Git Ops     │                            │ GitHub API   │
└──────────────┘                            └──────────────┘
        │                                             │
        ├─ Create branch                              ├─ Create release
        ├─ Commit changes                             ├─ Upload assets
        ├─ Push to remote                             └─ List releases
        ├─ Merge to main
        └─ Create tags
```

## Component Architecture

### 1. Data Layer

```
┌─────────────────────────────────────────────────────────────┐
│                      Data Models                             │
├─────────────────────────────────────────────────────────────┤
│  Version                                                     │
│  - major: int                                                │
│  - minor: int                                                │
│  - patch: int                                                │
│  - suffix_type: VersionType                                  │
│  - suffix_number: int                                        │
│  + parse(str) → Version                                      │
│  + bump(type) → Version                                      │
├─────────────────────────────────────────────────────────────┤
│  DeploymentRecord                                            │
│  - version: str                                              │
│  - timestamp: str                                            │
│  - branch: str                                               │
│  - commit_hash: str                                          │
│  - user: str                                                 │
│  - success: bool                                             │
│  - notes: str                                                │
├─────────────────────────────────────────────────────────────┤
│  GitHubRelease                                               │
│  - tag_name: str                                             │
│  - name: str                                                 │
│  - body: str                                                 │
│  - draft: bool                                               │
│  - prerelease: bool                                          │
│  - created_at: str                                           │
│  - html_url: str                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Business Logic Layer

```
┌─────────────────────────────────────────────────────────────┐
│                       Managers                               │
├─────────────────────────────────────────────────────────────┤
│  VersionManager                                              │
│  + read_version() → Version                                  │
│  + write_version(Version)                                    │
│  + add_to_history(DeploymentRecord)                          │
│  + get_history() → List[Dict]                                │
│  + rollback_to_version(str) → bool                           │
├─────────────────────────────────────────────────────────────┤
│  GitManager                                                  │
│  + validate_repo() → bool                                    │
│  + get_current_branch() → str                                │
│  + get_status() → Dict                                       │
│  + create_and_checkout_branch(str) → bool                    │
│  + commit_and_push(str, str) → bool                          │
│  + merge_to_main(str) → bool                                 │
│  + create_tag(str, str)                                      │
│  + get_commit_hash() → str                                   │
├─────────────────────────────────────────────────────────────┤
│  GitHubManager                                               │
│  + create_release(...) → Optional[str]                       │
│  + get_releases() → List[GitHubRelease]                      │
│  + upload_asset(str, Path) → bool                            │
├─────────────────────────────────────────────────────────────┤
│  ChangelogManager                                            │
│  + read_changelog() → str                                    │
│  + add_entry(str, str, str)                                  │
└─────────────────────────────────────────────────────────────┘
```

### 3. Presentation Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Components                             │
├─────────────────────────────────────────────────────────────┤
│  DevSyncMainWindow (QMainWindow)                             │
│  ├─ Menu Bar                                                 │
│  │  ├─ File Menu (Deploy, Exit)                              │
│  │  ├─ View Menu (Refresh)                                   │
│  │  └─ Help Menu (About)                                     │
│  ├─ Tab Widget                                               │
│  │  ├─ Dashboard Tab                                         │
│  │  ├─ Releases Tab                                          │
│  │  ├─ Changelog Tab                                         │
│  │  ├─ History Tab                                           │
│  │  └─ Settings Tab                                          │
│  └─ System Tray Icon                                         │
├─────────────────────────────────────────────────────────────┤
│  DeploymentWizard (QWizard)                                  │
│  ├─ VersionBumpPage                                          │
│  ├─ ChangelogPage                                            │
│  ├─ ReviewPage                                               │
│  ├─ OptionsPage                                              │
│  ├─ ConfirmationPage                                         │
│  ├─ ProgressPage                                             │
│  └─ ResultsPage                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4. Worker Thread

```
┌─────────────────────────────────────────────────────────────┐
│              DeploymentWorker (QThread)                      │
├─────────────────────────────────────────────────────────────┤
│  Signals:                                                    │
│  - progress(int, str)      # Step number and message         │
│  - log(str, str)           # Message and level               │
│  - finished(bool, str)     # Success and message             │
│  - changelog_requested(str) # Version for changelog          │
├─────────────────────────────────────────────────────────────┤
│  Methods:                                                    │
│  + run()                   # Main deployment logic           │
│  + set_changelog(str)      # Set changelog from main thread │
├─────────────────────────────────────────────────────────────┤
│  Deployment Steps:                                           │
│  1. Validate repository                                      │
│  2. Create branch                                            │
│  3. Bump version                                             │
│  4. Get changelog                                            │
│  5. Commit and push                                          │
│  6. Merge to main (optional)                                 │
│  7. Create tag                                               │
│  8. Create GitHub release                                    │
│  9. Save to history                                          │
│  10. Complete                                                │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Deployment Flow

```
User clicks "Deploy Now"
        │
        ▼
DeploymentWizard opens
        │
        ├─ Step 1: User selects version bump
        │           ↓
        │           Config updated
        │
        ├─ Step 2: User writes changelog
        │           ↓
        │           Config updated
        │
        ├─ Step 3: User reviews changes
        │           ↓
        │           Git status displayed
        │
        ├─ Step 4: User sets options
        │           ↓
        │           Config updated
        │
        ├─ Step 5: User confirms
        │           ↓
        │           Summary displayed
        │
        ├─ Step 6: Deployment executes
        │           ↓
        │           DeploymentWorker.run()
        │           ├─ Validate repo
        │           ├─ Create branch
        │           ├─ Bump version
        │           ├─ Update changelog
        │           ├─ Commit & push
        │           ├─ Merge to main
        │           ├─ Create tag
        │           ├─ Create release
        │           └─ Save history
        │           ↓
        │           Signals emitted
        │           ├─ progress(step, msg)
        │           ├─ log(msg, level)
        │           └─ finished(success, msg)
        │
        └─ Step 7: Results displayed
                    ↓
                    User sees success/failure
```

### Version Rollback Flow

```
User opens History tab
        │
        ▼
History tree populated
        │
        ▼
User right-clicks version
        │
        ▼
Context menu appears
        │
        ▼
User selects "Rollback"
        │
        ▼
Confirmation dialog
        │
        ▼
VersionManager.rollback_to_version()
        │
        ├─ Parse version string
        ├─ Write to version.txt
        └─ Return success/failure
        │
        ▼
Dashboard refreshed
        │
        ▼
New version displayed
```

### GitHub Release Flow

```
DeploymentWorker running
        │
        ▼
Step 8: Create GitHub release
        │
        ▼
GitHubManager.create_release()
        │
        ├─ Get GitHub API instance
        ├─ Get repository
        ├─ Create release
        │   ├─ tag: v{version}
        │   ├─ name: Release {version}
        │   ├─ body: changelog
        │   ├─ draft: user option
        │   └─ prerelease: user option
        └─ Return URL
        │
        ▼
URL displayed in results
```

## File System Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                    File System                               │
├─────────────────────────────────────────────────────────────┤
│  version.txt                                                 │
│  - Read by VersionManager.read_version()                     │
│  - Written by VersionManager.write_version()                 │
├─────────────────────────────────────────────────────────────┤
│  version_history.json                                        │
│  - Read by VersionManager.get_history()                      │
│  - Written by VersionManager.add_to_history()                │
├─────────────────────────────────────────────────────────────┤
│  CHANGELOG.md                                                │
│  - Read by ChangelogManager.read_changelog()                 │
│  - Written by ChangelogManager.add_entry()                   │
├─────────────────────────────────────────────────────────────┤
│  QSettings (Registry/Config file)                            │
│  - theme: "light" or "dark"                                  │
│  - git_user: user name                                       │
│  - git_email: user email                                     │
├─────────────────────────────────────────────────────────────┤
│  System Keyring                                              │
│  - devsync/github_token: GitHub access token                 │
└─────────────────────────────────────────────────────────────┘
```

## External Integrations

```
┌─────────────────────────────────────────────────────────────┐
│                  External Systems                            │
├─────────────────────────────────────────────────────────────┤
│  Git (via GitPython)                                         │
│  - Repository operations                                     │
│  - Branch management                                         │
│  - Commit and push                                           │
│  - Tag creation                                              │
├─────────────────────────────────────────────────────────────┤
│  GitHub API (via PyGithub)                                   │
│  - Release creation                                          │
│  - Asset uploads                                             │
│  - Release listing                                           │
├─────────────────────────────────────────────────────────────┤
│  System Keyring (via keyring)                                │
│  - Secure credential storage                                 │
│  - Cross-platform support                                    │
└─────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Security Layers                            │
├─────────────────────────────────────────────────────────────┤
│  1. Input Validation                                         │
│     - Version string validation                              │
│     - Git command sanitization                               │
│     - Path validation                                        │
├─────────────────────────────────────────────────────────────┤
│  2. Credential Management                                    │
│     - System keyring for tokens                              │
│     - Password field masking                                 │
│     - No hardcoded secrets                                   │
│     - Environment variable fallback                          │
├─────────────────────────────────────────────────────────────┤
│  3. Error Handling                                           │
│     - Try-except blocks                                      │
│     - User-friendly error messages                           │
│     - Detailed logging                                       │
│     - Graceful degradation                                   │
└─────────────────────────────────────────────────────────────┘
```

## Thread Safety

```
┌─────────────────────────────────────────────────────────────┐
│                  Threading Model                             │
├─────────────────────────────────────────────────────────────┤
│  Main Thread (GUI)                                           │
│  - UI updates                                                │
│  - User interactions                                         │
│  - Signal reception                                          │
├─────────────────────────────────────────────────────────────┤
│  Worker Thread (Deployment)                                  │
│  - Git operations                                            │
│  - GitHub API calls                                          │
│  - File I/O                                                  │
│  - Signal emission                                           │
├─────────────────────────────────────────────────────────────┤
│  Communication                                               │
│  - Signals/Slots (thread-safe)                               │
│  - QThread.run() for background work                         │
│  - QMetaObject.invokeMethod for UI updates                   │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Package Structure

```
DevSync.exe (or DevSync.app / DevSync)
├─ Python interpreter (embedded)
├─ PyQt6 libraries
├─ Application code (devsync_gui.py)
├─ Dependencies
│  ├─ PyGithub
│  ├─ GitPython
│  ├─ markdown
│  ├─ keyring
│  └─ requests
└─ Data files
   ├─ version.txt
   ├─ CHANGELOG.md
   └─ config.yaml
```

## State Management

```
┌─────────────────────────────────────────────────────────────┐
│                    Application State                         │
├─────────────────────────────────────────────────────────────┤
│  Persistent (QSettings)                                      │
│  - theme: str                                                │
│  - git_user: str                                             │
│  - git_email: str                                            │
├─────────────────────────────────────────────────────────────┤
│  Session (Memory)                                            │
│  - current_version: Version                                  │
│  - git_status: Dict                                          │
│  - deployment_history: List[Dict]                            │
│  - github_releases: List[GitHubRelease]                      │
├─────────────────────────────────────────────────────────────┤
│  Wizard (Temporary)                                          │
│  - config: Dict                                              │
│    ├─ bump_type: str                                         │
│    ├─ custom_version: str                                    │
│    ├─ changelog_entry: str                                   │
│    ├─ auto_merge: bool                                       │
│    ├─ draft_release: bool                                    │
│    └─ prerelease: bool                                       │
└─────────────────────────────────────────────────────────────┘
```

---

**Architecture Notes:**

- **Single File**: All code in one file for easy distribution
- **Clean Separation**: Data, business logic, and UI are separated
- **Thread Safety**: Background operations don't block UI
- **Extensible**: Easy to add new features or tabs
- **Secure**: Credentials stored safely in system keyring
- **Cross-Platform**: Works on Windows, macOS, Linux
