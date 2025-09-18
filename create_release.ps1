# PowerShell script to create GitHub releases
# Usage: .\create_release.ps1 -Version "2.1.2" -Token "YOUR_GITHUB_TOKEN"

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [Parameter(Mandatory=$true)]
    [string]$Token
)

# Repository information
$owner = "Elibart-home"
$repo = "tibber_soc_updater"

# Release notes template
$releaseNotes = @"
## 🚀 New Features & Fixes

### v$Version
- ✅ Update your changes here
- ✅ Add new features
- ✅ Fix bugs

## 📦 Installation
1. Update via HACS
2. Restart Home Assistant
3. Enjoy the improved integration!

## 🔧 Troubleshooting
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed troubleshooting guide.
"@

# Create release body
$body = @{
    tag_name = "v$Version"
    name = "Tibber SOC Updater v$Version"
    body = $releaseNotes
    draft = $false
    prerelease = $false
} | ConvertTo-Json

# Headers for GitHub API
$headers = @{
    Authorization = "token $Token"
    Accept = "application/vnd.github.v3+json"
}

try {
    Write-Host "Creating release v$Version..." -ForegroundColor Green
    
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    
    Write-Host "Release created successfully!" -ForegroundColor Green
    Write-Host "Release URL: $($response.html_url)" -ForegroundColor Cyan
    
} catch {
    Write-Host "Error creating release: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response)" -ForegroundColor Red
}
