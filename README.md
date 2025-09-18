# Tibber SOC Updater for Home Assistant

Deze custom component voor Home Assistant maakt het mogelijk om de State of Charge (SOC) van je elektrische voertuig in te stellen via de Tibber GraphAPI. Deze integratie is gebaseerd op reverse engineering van de officiële Tibber app en gebruikt directe authenticatie met je Tibber account.

## 🚀 Functionaliteiten

- **Service-only integratie** - Geen sensoren, alleen SOC update functionaliteit
- **Automatische token vernieuwing** - Houdt verbinding stabiel via keepalive mechanisme (elke 18 uur)
- **SOC Update Service** - Stel de State of Charge van je voertuig in via `tibber_soc_updater.set_vehicle_soc`
- **Robuuste authenticatie** - Meerdere authenticatie methoden en endpoint fallbacks
- **JWT token validatie** - Controleert automatisch token scopes (gw-api-write, gw-api-read, gw-web)
- **Automatische retry logica** - Exponential backoff bij tijdelijke problemen
- **Uitgebreide error handling** - Detecteert en herstelt van API wijzigingen
- **Debug logging** - Gedetailleerde logging voor troubleshooting

## 📦 Installatie

### HACS (aanbevolen)
1. Open HACS in Home Assistant
2. Ga naar "Integraties"
3. Klik op de drie puntjes rechtsboven en kies "Custom repositories"
4. Voeg deze repository URL toe: `https://github.com/Elibart-home/tibber_soc_updater`
5. Kies categorie "Integratie"
6. Installeer de "Tibber SOC Updater" integratie
7. Herstart Home Assistant

### Handmatige installatie
1. Download de laatste release van deze repository
2. Kopieer de map `custom_components/tibber_soc_updater` naar je Home Assistant config directory
3. Herstart Home Assistant

### Test script
Er is een test script beschikbaar om de integratie te testen:
```bash
# Update credentials in test_integration.py
python test_integration.py
```

## ⚙️ Configuratie

1. Ga naar Configuratie > Integraties
2. Klik op "Integratie toevoegen"
3. Zoek naar "Tibber SOC Updater"
4. Vul de volgende gegevens in:
   - **Tibber gebruikersnaam** (e-mail)
   - **Tibber wachtwoord**

### Debug logging inschakelen
Voor uitgebreide logging voeg dit toe aan je `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.tibber_soc_updater: debug
```

## 🔧 Services

### Set Vehicle State of Charge

Met deze service kun je de SoC (State of Charge) van je voertuig instellen in Tibber.

**Service:** `tibber_soc_updater.set_vehicle_soc`

**Parameters:**
- `vehicle_id`: ID van het voertuig (verplicht)
- `home_id`: ID van je Tibber home (verplicht)
- `battery_level`: Batterijniveau 0-100 (verplicht)

**Voorbeeld met echte IDs:**
```yaml
service: tibber_soc_updater.set_vehicle_soc
data:
  vehicle_id: "a739d722-ae8b-4778-a521-8c93ee509837"
  home_id: "3c3a7b9c-590e-4000-8046-ef4d12612acd"
  battery_level: 80
```

**Voorbeeld met secrets:**
```yaml
service: tibber_soc_updater.set_vehicle_soc
data:
  vehicle_id: !secret tibber_vehicle_id
  home_id: !secret tibber_home_id
  battery_level: 80
```

> **Note:** De vehicle_id en home_id kun je vinden in de Tibber app of via de test script.

## 🤖 Automatiseringen

### Token Vernieuwing en SoC Aanpassing

De integratie heeft automatische token vernieuwing (elke 18 uur), maar hier is een voorbeeld van een automatisering die de SoC aanpast voor laadbeheersing:

```yaml
alias: "Tibber SoC bijwerken bij verbinding"
description: "Verhoogt de SoC met 20% voor Tibber wanneer de auto wordt aangesloten"
trigger:
  - platform: state
    entity_id: sensor.jouw_laadpaal_status
    from: Disconnected
action:
  # Direct de SoC bijwerken (token vernieuwing gebeurt automatisch)
  - service: tibber_soc_updater.set_vehicle_soc
    data:
      vehicle_id: "a739d722-ae8b-4778-a521-8c93ee509837"
      home_id: "3c3a7b9c-590e-4000-8046-ef4d12612acd"
      battery_level: >-
        {% set soc = states('sensor.jouw_auto_soc') | float(default=0) | int %}
        {% set adjusted_soc = (soc + 20) | int %}
        {{ [adjusted_soc, 100] | min }}
mode: single
```

Deze automatisering:
1. Triggert wanneer de auto wordt aangesloten
2. Leest de huidige SoC van je auto
3. Verhoogt deze met 20% (maximum 100%)
4. Stuurt de aangepaste waarde naar Tibber

**Voordelen van de nieuwe versie:**
- ✅ **Geen handmatige token vernieuwing** meer nodig
- ✅ **Automatische retry** bij tijdelijke problemen
- ✅ **Robuuste authenticatie** met fallback endpoints
- ✅ **Betere error handling** en logging

Dit kan worden gebruikt om:
- De maximale laadcapaciteit te beperken (bijv. stoppen bij 80% door 20% op te tellen)
- Laadgedrag te optimaliseren zonder de auto-instellingen aan te passen
- Automatische SOC updates bij het aansluiten van de auto

## ⚠️ Bekende Beperkingen

- **SOC updates werken alleen** wanneer het voertuig verbonden is en laadt
- **Waarden updaten mogelijk niet direct** bij laden op andere locaties
- **Token verloopt na 18 uur** maar wordt automatisch vernieuwd
- **API wijzigingen** kunnen tijdelijk problemen veroorzaken (wordt automatisch opgelost)

> **Note:** Deze integratie is een **service-only integratie** - het maakt geen sensoren aan, alleen de `tibber_soc_updater.set_vehicle_soc` service is beschikbaar.

## 🔧 Probleemoplossing

### Veelvoorkomende problemen

1. **Authenticatie fout (400 Bad Request)**
   - ✅ **Opgelost in v2.1** - Automatische endpoint discovery en retry logica
   - Controleer of je gebruikersnaam en wachtwoord correct zijn
   - Schakel debug logging in voor gedetailleerde informatie

2. **GraphQL 404 errors**
   - ✅ **Opgelost in v2.1** - Geforceerd gebruik van primaire endpoint
   - De integratie gebruikt nu altijd `https://app.tibber.com/v4/gql`

3. **Service werkt niet**
   - Controleer of je de juiste vehicle_id en home_id gebruikt
   - Gebruik de test script om te controleren of authenticatie werkt
   - Kijk in de Home Assistant logs voor specifieke foutmeldingen

4. **Token problemen**
   - ✅ **Opgelost in v2.1** - Automatische token vernieuwing elke 18 uur
   - JWT token validatie controleert automatisch scopes

### Debug Logging

Voor uitgebreide troubleshooting:
```yaml
logger:
  logs:
    custom_components.tibber_soc_updater: debug
```

### Test Script
Gebruik het test script om de integratie te testen:
```bash
python test_integration.py
```

### Belangrijke IDs
```json
{
    "vehicle_id": "a739d722-ae8b-4778-a521-8c93ee509837",
    "charger_id": "71bfe079-205a-4a5b-a264-a251aa61d1e8",
    "home_id": "3c3a7b9c-590e-4000-8046-ef4d12612acd"
}
```

## 🤝 Bijdragen

Bijdragen zijn welkom! Als je een bug vindt of een verbetering wilt voorstellen:

1. Open een issue op de [GitHub repository](https://github.com/Elibart-home/tibber_soc_updater/issues)
2. Fork de repository
3. Maak je wijzigingen
4. Dien een Pull Request in

### Changelog

**v2.1.1 (Latest)**
- ✅ Fix endpoint testing warnings - Geen verwarrende berichten meer
- ✅ Verbeterde GraphQL endpoint testing met POST requests
- ✅ Betere logging op debug level
- ✅ Correcte versie informatie voor Home Assistant
- ✅ Toegevoegd integration_type in manifest.json

**v2.1.0**
- ✅ Geforceerd gebruik van primaire GraphQL endpoint
- ✅ Automatische endpoint discovery
- ✅ Meerdere authenticatie methoden
- ✅ Retry logica met exponential backoff
- ✅ JWT token scope validatie
- ✅ Verbeterde error handling en logging

**v2.0.0**
- ✅ Reverse engineering implementatie
- ✅ Correcte API headers
- ✅ Automatische token vernieuwing
- ✅ Robuuste authenticatie

## 📄 Licentie

Deze integratie is gelicenseerd onder de Apache License 2.0. Zie het [LICENSE](LICENSE) bestand voor details.

## ⚠️ Disclaimer

Deze integratie is niet officieel en wordt niet ondersteund door Tibber. Gebruik op eigen risico.

## 🔗 Links

- [GitHub Repository](https://github.com/Elibart-home/tibber_soc_updater)
- [Issues](https://github.com/Elibart-home/tibber_soc_updater/issues)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Test Script](test_integration.py) 