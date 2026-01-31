#!/usr/bin/env python3
"""
Reprocess extracted vehicles to parse data from URLs.
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.scraper.vehicle_extractor import VehicleExtractor


def reprocess_vehicles():
    """Reprocess vehicles to extract data from URLs."""
    extractor = VehicleExtractor()

    # Load existing extracted vehicles
    with open('logs/extracted_vehicles.json', 'r') as f:
        vehicles = json.load(f)

    print(f"\nReprocessing {len(vehicles)} vehicles...\n")

    # Parse URL data for each vehicle
    for vehicle in vehicles:
        if vehicle.get('detail_page_url'):
            extractor._parse_url_data(vehicle)

    # Save enhanced data
    with open('logs/extracted_vehicles_enhanced.json', 'w') as f:
        json.dump(vehicles, f, indent=2)

    print(f"✅ Saved enhanced data to: logs/extracted_vehicles_enhanced.json\n")

    # Display summary
    print("=" * 80)
    print("ENHANCED VEHICLE DATA SUMMARY")
    print("=" * 80)

    oregon_count = 0
    for i, vehicle in enumerate(vehicles[:5], 1):  # Show first 5
        print(f"\nVehicle {i}:")
        print(f"  Lot #: {vehicle.get('lot_number')}")
        print(f"  Year: {vehicle.get('year')}")
        print(f"  Make: {vehicle.get('make')}")
        print(f"  Model: {vehicle.get('model')}")
        print(f"  Title: {vehicle.get('title_type')}")
        print(f"  Location: {vehicle.get('location')}")
        print(f"  Current Bid: ${vehicle.get('current_bid', 0):,.0f}")
        print(f"  URL: {vehicle.get('detail_page_url')}")

        if vehicle.get('location') and 'OR' in vehicle.get('location', ''):
            oregon_count += 1

    if len(vehicles) > 5:
        print(f"\n... and {len(vehicles) - 5} more vehicles")

    print(f"\n{'=' * 80}")
    print(f"Total vehicles: {len(vehicles)}")
    print(f"Oregon vehicles: {oregon_count}")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    reprocess_vehicles()
