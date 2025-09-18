# Release Guide for Tibber SOC Updater

## 🚀 Creating Releases via PowerShell

### Prerequisites

1. **GitHub Personal Access Token**
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Generate a new token with `repo` permissions
   - Copy the token

2. **Set Environment Variable**
   ```powershell
   $env:GITHUB_TOKEN = "your_token_here"
   ```

### Method 1: Quick Release (Recommended)

```powershell
# Set your token once
$env:GITHUB_TOKEN = "your_token_here"

# Create a release
.\quick_release.ps1 -Version "2.1.2"
```

### Method 2: Full Release Script

```powershell
# Create a release with custom notes
.\create_release.ps1 -Version "2.1.2" -Token "your_token_here"
```

### Method 3: Manual Steps

1. **Update version numbers:**
   ```bash
   # Update VERSION file
   echo "2.1.2" > VERSION
   
   # Update manifest.json
   # Change "version": "2.1.2" in manifest.json
   ```

2. **Commit and push:**
   ```bash
   git add VERSION custom_components/tibber_soc_updater/manifest.json
   git commit -m "Bump version to 2.1.2"
   git push origin main
   ```

3. **Create Git tag:**
   ```bash
   git tag -a v2.1.2 -m "Release version 2.1.2"
   git push origin v2.1.2
   ```

4. **Create GitHub release:**
   ```powershell
   .\quick_release.ps1 -Version "2.1.2"
   ```

## 📋 Release Checklist

- [ ] Update VERSION file
- [ ] Update manifest.json version
- [ ] Update README.md changelog
- [ ] Test the integration
- [ ] Commit and push changes
- [ ] Create Git tag
- [ ] Create GitHub release
- [ ] Test in Home Assistant

## 🎯 Version Numbering

- **Patch** (2.1.1 → 2.1.2): Bug fixes, small improvements
- **Minor** (2.1.1 → 2.2.0): New features, larger improvements
- **Major** (2.1.1 → 3.0.0): Breaking changes, major rewrites

## 🔧 Troubleshooting

### Token Issues
- Make sure your token has `repo` permissions
- Check if the token is not expired
- Verify the environment variable is set correctly

### Script Issues
- Run PowerShell as Administrator if needed
- Check if the repository name is correct
- Verify the tag doesn't already exist

### Home Assistant Issues
- Wait a few minutes after creating the release
- Clear HACS cache if needed
- Restart Home Assistant after updating
