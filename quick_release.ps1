# Quick release script for Tibber SOC Updater
# Usage: .\quick_release.ps1 -Version "2.1.2"

param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

# You need to set your GitHub token here or as environment variable
$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Host "Please set GITHUB_TOKEN environment variable or edit this script" -ForegroundColor Red
    Write-Host "Example: `$env:GITHUB_TOKEN = 'your_token_here'" -ForegroundColor Yellow
    exit 1
}

# Repository information
$owner = "Elibart-home"
$repo = "tibber_soc_updater"

# Simple release notes
$releaseNotes = @"
## 🚀 Tibber SOC Updater v$Version

### Changes
- Update your changes here
- Add new features
- Fix bugs

## 📦 Installation
1. Update via HACS
2. Restart Home Assistant

## 🔧 Troubleshooting
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed troubleshooting guide.
"@

# Create release
$body = @{
    tag_name = "v$Version"
    name = "Tibber SOC Updater v$Version"
    body = $releaseNotes
} | ConvertTo-Json

$headers = @{
    Authorization = "token $token"
    Accept = "application/vnd.github.v3+json"
}

try {
    Write-Host "Creating release v$Version..." -ForegroundColor Green
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "✅ Release created: $($response.html_url)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
