#!/usr/bin/env python3
"""
Test script for Tibber SOC Updater integration
Uses the real IDs from the reverse engineering notes
"""

import asyncio
import aiohttp
import logging
from custom_components.tibber_soc_updater import TibberGraphAPI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Real IDs from reverse engineering
VEHICLE_ID = "a739d722-ae8b-4778-a521-8c93ee509837"
HOME_ID = "3c3a7b9c-590e-4000-8046-ef4d12612acd"
CHARGER_ID = "71bfe079-205a-4a5b-a264-a251aa61d1e8"

async def test_authentication():
    """Test authentication with Tibber API"""
    print("Testing Tibber authentication...")
    
    # You'll need to replace these with your actual credentials
    USERNAME = "your_email@example.com"  # Replace with your Tibber email
    PASSWORD = "your_password"           # Replace with your Tibber password
    
    async with aiohttp.ClientSession() as session:
        api = TibberGraphAPI(session, USERNAME, PASSWORD)
        
        try:
            await api.authenticate()
            print("✅ Authentication successful!")
            print(f"Token: {api._token[:50]}...")
            print(f"Token expires at: {api._token_expires_at}")
            return api
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return None

async def test_graphql_query(api):
    """Test a simple GraphQL query"""
    print("\nTesting GraphQL query...")
    
    query = """
    query {
        me {
            homes {
                id
                address {
                    address1
                }
            }
        }
    }
    """
    
    try:
        result = await api.execute_gql(query)
        print("✅ GraphQL query successful!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ GraphQL query failed: {e}")
        return False

async def test_vehicle_soc_update(api):
    """Test setting vehicle SOC"""
    print("\nTesting vehicle SOC update...")
    
    # Test with a safe battery level (80%)
    battery_level = 80
    
    try:
        await api.execute_gql(
            """
            mutation SetVehicleSettings($vehicleId: String!, $homeId: String!, $settings: [SettingsItemInput!]) {
                me {
                    setVehicleSettings(id: $vehicleId, homeId: $homeId, settings: $settings) {
                        __typename
                    }
                }
            }
            """,
            {
                "vehicleId": VEHICLE_ID,
                "homeId": HOME_ID,
                "settings": [
                    {
                        "key": "offline.vehicle.batteryLevel",
                        "value": battery_level
                    }
                ]
            }
        )
        print(f"✅ Vehicle SOC update successful! Set to {battery_level}%")
        return True
    except Exception as e:
        print(f"❌ Vehicle SOC update failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚗 Tibber SOC Updater Integration Test")
    print("=" * 50)
    
    # Test authentication
    api = await test_authentication()
    if not api:
        print("❌ Cannot continue without authentication")
        return
    
    # Test GraphQL query
    if not await test_graphql_query(api):
        print("❌ GraphQL query failed, but continuing...")
    
    # Test vehicle SOC update
    await test_vehicle_soc_update(api)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Update USERNAME and PASSWORD in this script before running!")
    print("⚠️  This script will attempt to set your vehicle SOC to 80%")
    
    response = input("\nDo you want to continue? (y/N): ")
    if response.lower() == 'y':
        asyncio.run(main())
    else:
        print("Test cancelled.")
