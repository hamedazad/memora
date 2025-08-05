# Versioning Guide for Memora Memory Assistant

This guide explains how to manage versions for the Memora Memory Assistant project.

## 📋 Version Structure

We use **Semantic Versioning (SemVer)** with the format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes, incompatible API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## 🛠️ Version Management Tools

### 1. Version File (`version.py`)
Central location for version information:
```python
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
VERSION_HISTORY = [
    "1.0.0 - Initial release with voice memory creation and search functionality",
]
```

### 2. Version Management Script (`manage_version.py`)
Command-line tool for version operations:

```bash
# Show current version
python manage_version.py show

# Update versions
python manage_version.py patch   # 1.0.0 -> 1.0.1
python manage_version.py minor   # 1.0.0 -> 1.1.0
python manage_version.py major   # 1.0.0 -> 2.0.0
```

## 📝 Version Update Process

### 1. Development Workflow
```bash
# 1. Make your changes
git checkout -b feature/new-feature

# 2. Test your changes
python manage.py test

# 3. Update version (if needed)
python manage_version.py patch

# 4. Update changelog
# Edit CHANGELOG.md with your changes

# 5. Commit changes
git add .
git commit -m "feat: add new feature (v1.0.1)"

# 6. Create pull request
git push origin feature/new-feature
```

### 2. Release Process
```bash
# 1. Merge to main branch
git checkout main
git merge feature/new-feature

# 2. Update version for release
python manage_version.py minor

# 3. Update documentation
# - Update README.md if needed
# - Update CHANGELOG.md
# - Update DEPLOYMENT.md if needed

# 4. Create release tag
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# 5. Deploy to production
# Follow DEPLOYMENT.md guide
```

## 📊 Version History Tracking

### 1. Version History in `version.py`
```python
VERSION_HISTORY = [
    "1.0.0 - Initial release with voice memory creation and search functionality",
    "1.0.1 - Fixed time-based search filtering",
    "1.1.0 - Added advanced voice search features",
]
```

### 2. Changelog (`CHANGELOG.md`)
Detailed change log following [Keep a Changelog](https://keepachangelog.com/) format:
```markdown
## [1.1.0] - 2025-08-03

### Added
- Advanced voice search with contextual filtering
- Time-aware search capabilities

### Fixed
- Search results not displaying correctly
- Time-based filtering issues

### Changed
- Improved search relevance scoring
```

## 🔄 Version Integration

### 1. Django Settings
Version is automatically loaded in `settings.py`:
```python
from version import get_version
APP_VERSION = get_version()
```

### 2. Templates
Display version in templates:
```html
<footer>
    <small>Memora v{{ app_version }}</small>
</footer>
```

### 3. API Responses
Include version in API responses:
```python
return JsonResponse({
    'success': True,
    'version': get_version(),
    'data': result
})
```

## 🏷️ Git Tagging

### Create Release Tags
```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0"

# Push tag to remote
git push origin v1.0.0

# List all tags
git tag -l

# Show tag details
git show v1.0.0
```

### Tag Naming Convention
- Use semantic versioning: `v1.0.0`
- Include 'v' prefix for clarity
- Use descriptive commit messages

## 📦 Package Distribution

### 1. Setup.py Configuration
```python
from version import get_version

setup(
    name="memora",
    version=get_version(),
    description="A Django-based memory management application",
    # ... other configuration
)
```

### 2. Build Distribution
```bash
# Build source distribution
python setup.py sdist

# Build wheel distribution
python setup.py bdist_wheel

# Install in development mode
pip install -e .
```

## 🔍 Version Checking

### 1. Runtime Version Check
```python
from version import get_version, get_version_info

# Get version string
version = get_version()  # "1.0.0"

# Get version tuple
major, minor, patch = get_version_info()  # (1, 0, 0)
```

### 2. Version Comparison
```python
from version import get_version_info

current = get_version_info()
required = (1, 0, 0)

if current >= required:
    print("Version is compatible")
else:
    print("Version is too old")
```

## 🚀 Release Checklist

Before releasing a new version:

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Changelog is updated
- [ ] Version is incremented
- [ ] Git tag is created
- [ ] Release notes are written
- [ ] Deployment is tested
- [ ] Monitoring is configured

## 📈 Version Strategy

### Development Versions
- Use patch increments for bug fixes
- Use minor increments for new features
- Use major increments for breaking changes

### Release Frequency
- **Patch releases**: As needed for critical fixes
- **Minor releases**: Monthly for new features
- **Major releases**: Quarterly for significant changes

### Long-term Support
- Maintain compatibility for at least 2 major versions
- Provide migration guides for breaking changes
- Support multiple Python versions

## 🛡️ Version Security

### 1. Version Validation
```python
import re

def validate_version(version_string):
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version_string))
```

### 2. Dependency Version Pinning
```txt
# requirements.txt
Django==5.2.4
openai==1.3.0
python-dotenv==1.0.0
```

## 📞 Support

For version-related issues:
1. Check the current version: `python manage_version.py show`
2. Review the changelog: `CHANGELOG.md`
3. Check version history: `version.py`
4. Create an issue on GitHub

---

**Remember**: Always test version changes in a development environment before applying to production! 