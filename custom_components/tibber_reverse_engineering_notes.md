# Tibber App Reverse Engineering Notes

## Setup Process
1. Requirements:
   - Windows Subsystem for Android (WSA)
   - Magisk (version 28.1)
   - mitmproxy

2. Installation Steps:
   - Enable Zygisk in Magisk settings
   - Install LSPosed via Magisk module
   - Install LSPosed Manager APK
   - Install and enable TrustMeAlready module for com.tibber.android

## API Details
- GraphQL Endpoint: `https://app.tibber.com/v4/gql`
- Authentication Methods:
  1. Direct Authentication (Recommended):
     - Use username/password to get a JWT token
     - Token includes scopes: gw-api-write, gw-api-read, gw-web
  2. Via Home Assistant Integration (Alternative):
     - Uses existing Tibber connection
     - Less control over token management

- Required Headers:
  ```
  accept: application/graphql-response+json, application/json
  content-type: application/json
  x-tibber-new-ui: true
  authorization: Bearer <JWT_TOKEN>
  ```

## Important IDs
```json
{
    "vehicle_id": "a739d722-ae8b-4778-a521-8c93ee509837",
    "charger_id": "71bfe079-205a-4a5b-a264-a251aa61d1e8",
    "home_id": "3c3a7b9c-590e-4000-8046-ef4d12612acd"
}
```

## GraphQL Mutations

### Set Vehicle State of Charge
```graphql
mutation SetVehicleSettings($vehicleId: String!, $homeId: String!, $settings: [SettingsItemInput!]) {
    me {
        setVehicleSettings(id: $vehicleId, homeId: $homeId, settings: $settings) {
            __typename
        }
    }
}
```

Variables:
```json
{
    "vehicleId": "a739d722-ae8b-4778-a521-8c93ee509837",
    "homeId": "3c3a7b9c-590e-4000-8046-ef4d12612acd",
    "settings": [
        {
            "key": "offline.vehicle.batteryLevel",
            "value": 80
        }
    ]
}
```

## Known Limitations
- Tibber GraphAPI only updates SOC and range when vehicle is connected & charging
- Values may not update immediately when charging elsewhere
- EVCC charging status codes are mainly estimated due to inconsistent API data

## Feature Flags
```json
{
    "grid_rewards": true,
    "beta_power_ups": true,
    "csx_platform": true,
    "new_pulse_graph": true,
    "negative_area_price_graph": false,
    "price_timeline_gizmo": false
}
```

## Analytics Endpoints
- Rudderstack: `https://tibbersebwyei.dataplane.rudderstack.com/v1/batch`
- Events tracked:
  - integrations_smart_charging_vehicle_overview_viewed
  - integrations_smart_charging_vehicle_level_set
  - integrations_smart_charging_vehicle_state_set

## Home Assistant Integration Options
1. Custom Direct Authentication Component:
   - Service: `tibber_vehicle.set_vehicle_soc`
   - Parameters:
     - vehicle_id
     - home_id
     - battery_level (0-100)
   - Uses direct authentication with Tibber API
   - Endpoint: `https://app.tibber.com/v4/gql`

2. Via Existing Tibber Integration:
   - Uses the existing Tibber connection
   - Less control but simpler setup

## App Details
- Version: 25.20.0
- Package: com.tibber.android
- Build: 2520004 