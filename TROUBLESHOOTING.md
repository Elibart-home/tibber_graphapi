# Tibber SOC Updater - Troubleshooting

## Authenticatiefout: 400 Bad Request

### Probleem
Je krijgt de volgende foutmelding:
```
Failed to set vehicle [vehicle-id] SoC: Authentication failed: 400 - <!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <title>Error</title> </head> <body> <pre>Bad Request</pre> </body> </html>
```

### Belangrijke IDs (uit reverse engineering)
```json
{
    "vehicle_id": "a739d722-ae8b-4778-a521-8c93ee509837",
    "charger_id": "71bfe079-205a-4a5b-a264-a251aa61d1e8", 
    "home_id": "3c3a7b9c-590e-4000-8046-ef4d12612acd"
}
```

### Oorzaken
1. **API endpoint wijzigingen**: Tibber heeft mogelijk hun API endpoints gewijzigd
2. **Rate limiting**: Te veel requests in korte tijd
3. **Verlopen token**: Het authenticatietoken is verlopen
4. **Netwerkproblemen**: Problemen met de verbinding naar Tibber's servers

### Oplossingen

#### 1. Controleer de logs
Met de verbeterde logging kun je nu meer details zien:
- Ga naar Home Assistant → Settings → System → Logs
- Zoek naar entries van `custom_components.tibber_soc_updater`
- Kijk naar debug-level logs voor meer details

#### 2. Herstart de integratie
1. Ga naar Home Assistant → Settings → Devices & Services
2. Zoek de Tibber SOC Updater integratie
3. Klik op "Reload" of herstart Home Assistant

#### 3. Controleer je credentials
1. Verifieer dat je Tibber gebruikersnaam en wachtwoord correct zijn
2. Test of je kunt inloggen op de Tibber app/website

#### 4. Update de integratie
Deze versie bevat verbeteringen gebaseerd op reverse engineering:
- **Correcte API headers**: Gebruikt exact dezelfde headers als de Tibber app
- **JWT token validatie**: Controleert of het token de juiste scopes heeft (gw-api-write, gw-api-read, gw-web)
- **Betere error handling**: Detecteert HTML error pages en probeert alternatieve endpoints
- **Automatische endpoint discovery**: Test verschillende Tibber API endpoints
- **Verbeterde GraphQL requests**: Gebruikt `application/graphql-response+json` accept header
- **Battery level validatie**: Controleert dat de waarde tussen 0-100 ligt
- **Meerdere authenticatie methoden**: Probeert form data, JSON payload en andere formaten
- **Uitgebreide endpoint lijst**: Test 5 verschillende login endpoints en 4 GraphQL endpoints
- **Retry logica met exponential backoff**: Probeert automatisch opnieuw met toenemende delays
- **Betere logging**: Gedetailleerde debug informatie voor troubleshooting

#### 5. Handmatige endpoint test
Als het probleem aanhoudt, kun je de endpoints handmatig testen:

```bash
# Test login endpoint
curl -X POST "https://app.tibber.com/login.credentials" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: Tibber/25.20.0 (versionCode: 2520004Dalvik/2.1.0 (Linux; U; Android 10; Android SDK built for x86_64 Build/QSR1.211112.011))" \
  -d "email=YOUR_EMAIL&password=YOUR_PASSWORD"

# Test GraphQL endpoint
curl -X POST "https://app.tibber.com/v4/gql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "query { me { homes { id } } }"}'
```

### Testen met echte IDs
Gebruik de volgende service call met de echte IDs:

```yaml
service: tibber_soc_updater.set_vehicle_soc
data:
  vehicle_id: "a739d722-ae8b-4778-a521-8c93ee509837"
  home_id: "3c3a7b9c-590e-4000-8046-ef4d12612acd"
  battery_level: 80
```

### Debugging
Om meer debug informatie te krijgen:

1. Voeg dit toe aan je `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.tibber_soc_updater: debug
```

2. Herstart Home Assistant
3. Probeer de service opnieuw aan te roepen
4. Bekijk de logs voor gedetailleerde informatie

### Test script
Er is een test script beschikbaar (`test_integration.py`) om de integratie te testen:
1. Update de USERNAME en PASSWORD in het script
2. Run: `python test_integration.py`
3. Het script test authenticatie, GraphQL queries en SOC updates

### Nieuwe endpoints die worden getest
De integratie test nu automatisch deze endpoints:

**Login endpoints:**
- `https://app.tibber.com/login.credentials` (primair)
- `https://api.tibber.com/v1-beta/login`
- `https://api.tibber.com/v1/login`
- `https://app.tibber.com/login`
- `https://api.tibber.com/login`

**GraphQL endpoints:**
- `https://app.tibber.com/v4/gql` (primair)
- `https://api.tibber.com/v1-beta/gql`
- `https://api.tibber.com/v1/gql`
- `https://app.tibber.com/v3/gql`

### Authenticatie methoden
De integratie probeert nu 3 verschillende authenticatie methoden:
1. **Form data** (origineel): `email=...&password=...`
2. **JSON payload**: `{"email": "...", "password": "..."}`
3. **Form data dict**: `{"email": "...", "password": "..."}`

### Bekende problemen
- **HTML error pages**: Dit gebeurt vaak wanneer Tibber hun API wijzigt
- **Timeout errors**: Kan duiden op netwerkproblemen of server overbelasting
- **401 Unauthorized**: Token is verlopen, de integratie probeert automatisch opnieuw te authenticeren
- **Rate limiting**: De integratie gebruikt nu exponential backoff om rate limiting te voorkomen
- **404 GraphQL errors**: De integratie gebruikt nu alleen het primaire endpoint `https://app.tibber.com/v4/gql`

### Recente fixes (v2.1)
- **GraphQL endpoint fix**: Geforceerd gebruik van het primaire endpoint om 404 errors te voorkomen
- **Endpoint validatie**: Controleert of het juiste endpoint wordt gebruikt
- **Betere logging**: Toont welk endpoint wordt gebruikt voor GraphQL queries

### Contact
Als het probleem aanhoudt na het proberen van deze oplossingen, maak dan een issue aan in de GitHub repository met:
- Volledige foutmelding
- Home Assistant versie
- Logs (debug level)
- Beschrijving van wat je hebt geprobeerd
