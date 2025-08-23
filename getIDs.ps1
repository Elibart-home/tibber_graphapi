# Tibber inloggegevens
$Email = "JOUW_EMAIL"
$Password = "JOUW_WACHTWOORD"

# 1. Login en token ophalen
$loginBody = @{
    email = $Email
    password = $Password
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest `
    -Uri "https://app.tibber.com/login.credentials" `
    -Method Post `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body $loginBody

$loginData = $loginResponse.Content | ConvertFrom-Json
$token = $loginData.token

Write-Host "? Token opgehaald."

# 2. GraphQL query instellen
# (Pas dit aan naar wat je wil opvragen)
$query = @"
{
  me {
    homes {
      id
      electricVehicles {
        id
        shortName
        lastSeen
        battery {
          percent
          isCharging
        }
      }
    }
  }
}
"@

# JSON body maken voor POST
$queryBody = @{ query = $query } | ConvertTo-Json -Compress

# 3. Query uitvoeren
$queryResponse = Invoke-WebRequest `
    -Uri "https://app.tibber.com/v4/gql" `
    -Method Post `
    -Headers @{ 
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $token"
    } `
    -Body $queryBody

# 4. Resultaat tonen (mooi geparsed)
$result = $queryResponse.Content | ConvertFrom-Json
$result.data | ConvertTo-Json -Depth 5 -Compress | Out-String
