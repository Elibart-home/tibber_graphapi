# Tibber GraphAPI Integration for Home Assistant

Deze custom component voor Home Assistant maakt directe verbinding met de Tibber GraphAPI mogelijk, specifiek gericht op het uitlezen en besturen van elektrische voertuigen. De integratie gebruikt directe authenticatie met je Tibber account, onafhankelijk van de officiële Tibber integratie.

## Functionaliteiten

- Direct verbinding met Tibber GraphAPI via username/password authenticatie
- Automatische token vernieuwing
- Real-time voertuig informatie:
  - Batterijniveau (%)
  - Bereik (km)
  - Laadvermogen (kW)
  - Laadstatus
  - Verbindingsstatus
- Mogelijkheid om SoC (State of Charge) handmatig in te stellen
- Ondersteuning voor meerdere voertuigen

## Installatie

### HACS (aanbevolen)
1. Open HACS in Home Assistant
2. Ga naar "Integraties"
3. Klik op de drie puntjes rechtsboven en kies "Custom repositories"
4. Voeg deze repository URL toe: `https://github.com/Elibart-home/ha-tibber-graphapi`
5. Kies categorie "Integratie"
6. Installeer de "Tibber GraphAPI" integratie
7. Herstart Home Assistant

### Handmatige installatie
1. Download de laatste release van deze repository
2. Kopieer de map `custom_components/tibber_graphapi` naar je Home Assistant config directory
3. Herstart Home Assistant

## Configuratie

1. Ga naar Configuratie > Integraties
2. Klik op "Integratie toevoegen"
3. Zoek naar "Tibber GraphAPI"
4. Vul de volgende gegevens in:
   - Tibber gebruikersnaam (e-mail)
   - Tibber wachtwoord
   - Voertuig index (optioneel, standaard 0)
   - Update interval (optioneel, standaard 60 seconden)

## Sensoren

De integratie maakt drie sensoren aan:

1. **Vehicle Battery Level**
   - Type: Percentage
   - Attributen: charging, connected
   - Eenheid: %

2. **Vehicle Range**
   - Type: Afstand
   - Eenheid: km

3. **Vehicle Charging Power**
   - Type: Vermogen
   - Attributen: charging, connected
   - Eenheid: kW

## Services

### Set Vehicle State of Charge

Met deze service kun je de SoC (State of Charge) van je voertuig instellen in Tibber.

Service: `tibber_graphapi.set_vehicle_soc`

Parameters:
- `vehicle_id`: ID van het voertuig (verplicht)
- `home_id`: ID van je Tibber home (verplicht)
- `battery_level`: Batterijniveau 0-100 (verplicht)

Voorbeeld voor gebruik in een automatisering:
```yaml
service: tibber_graphapi.set_vehicle_soc
data:
  vehicle_id: "jouw-vehicle-id"
  home_id: "jouw-home-id"
  battery_level: 80
```

De vehicle_id en home_id kun je vinden in de attributen van de batterij sensor na installatie.

## Bekende Beperkingen

- Tibber GraphAPI update SoC en bereik alleen als het voertuig verbonden en aan het laden is
- Waarden updaten mogelijk niet direct bij laden op andere locaties
- EVCC laadstatus codes zijn geschat vanwege inconsistente API data

## Probleemoplossing

### Veelvoorkomende problemen

1. **Authenticatie fout**
   - Controleer of je gebruikersnaam en wachtwoord correct zijn
   - Zorg dat je account actief is en toegang heeft tot een voertuig

2. **Geen data updates**
   - Controleer of je voertuig correct is gekoppeld in de Tibber app
   - Verifieer of de voertuig index correct is als je meerdere voertuigen hebt

3. **Service werkt niet**
   - Controleer of je de juiste vehicle_id en home_id gebruikt
   - Kijk in de Home Assistant logs voor specifieke foutmeldingen

### Debug Logging

Om debug logging in te schakelen, voeg het volgende toe aan je `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.tibber_graphapi: debug
```

## Bijdragen

Bijdragen zijn welkom! Als je een bug vindt of een verbetering wilt voorstellen:

1. Open een issue op de [GitHub repository](https://github.com/Elibart-home/ha-tibber-graphapi/issues)
2. Fork de repository
3. Maak je wijzigingen
4. Dien een Pull Request in

## Licentie

Deze integratie is gelicenseerd onder de Apache License 2.0. Zie het LICENSE bestand voor details.

## Disclaimer

Deze integratie is niet officieel en wordt niet ondersteund door Tibber. Gebruik op eigen risico. 