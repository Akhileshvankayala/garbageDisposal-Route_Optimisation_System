#!/usr/bin/env python
"""Test the new endpoints to verify they're working correctly."""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_get_routes():
    """Test getting all routes."""
    print("\n" + "="*80)
    print("TEST: GET /api/routes")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/routes")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        routes = response.json()
        print(f"Found {len(routes)} routes")
        for route in routes:
            print(f"  - Route {route['route_id']}: {route['route_status']} "
                  f"(Vehicle: {route['vehicle_id']}, Driver: {route['driver_id']})")
    else:
        print(f"Error: {response.text}")
    
    return response


def test_get_route_details():
    """Test getting a specific route with all details."""
    print("\n" + "="*80)
    print("TEST: GET /api/routes/{route_id}")
    print("="*80)
    
    # First get a route ID
    routes_response = requests.get(f"{BASE_URL}/routes")
    if routes_response.status_code != 200 or len(routes_response.json()) == 0:
        print("No routes available to test")
        return None
    
    route_id = routes_response.json()[0]['route_id']
    
    response = requests.get(f"{BASE_URL}/routes/{route_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        route = response.json()
        print(f"\nRoute Details:")
        print(f"  Route ID: {route['route_id']}")
        print(f"  Status: {route['route_status']}")
        print(f"  Vehicle: {route['vehicle_id']}")
        print(f"  Driver: {route['driver_id']}")
        print(f"  Start Time: {route['start_time']}")
        print(f"  End Time: {route['end_time']}")
        print(f"  Total Distance: {route['total_distance_m']}m")
        print(f"  Total Waste: {route['total_waste_collected_kg']}kg")
        print(f"  Number of Stops: {len(route['stops'])}")
        
        for stop in route['stops']:
            print(f"\n  Stop {stop['stop_sequence']}: {stop['hospital_name']}")
            print(f"    Arrival: {stop['arrival_time']}")
            print(f"    Departure: {stop['departure_time']}")
            print(f"    Waste Collected: {stop['waste_collected_kg']}kg")
            print(f"    Collections: {len(stop['collections'])}")
            
            for collection in stop['collections']:
                print(f"      - {collection['amount_kg']}kg by {collection['staff_name']} "
                      f"({collection['collection_time']})")
    else:
        print(f"Error: {response.text}")
    
    return response


def test_get_vehicles():
    """Test getting all vehicles."""
    print("\n" + "="*80)
    print("TEST: GET /api/vehicles")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/vehicles")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        vehicles = response.json()
        print(f"Found {len(vehicles)} vehicles")
        for vehicle in vehicles:
            print(f"  - Vehicle {vehicle['vehicle_id']}: {vehicle['vehicle_name']} ({vehicle['status']})")
            print(f"    Location: ({vehicle['current_location_x']}, {vehicle['current_location_y']})")
            print(f"    Load: {vehicle['current_load_kg']}/{vehicle['capacity_kg']}kg")
            if vehicle['last_maintenance']:
                print(f"    Last Maintenance: {vehicle['last_maintenance']}")
    else:
        print(f"Error: {response.text}")
    
    return response


def test_update_vehicle_location():
    """Test updating a vehicle's location."""
    print("\n" + "="*80)
    print("TEST: PUT /api/vehicles/{vehicle_id}/location")
    print("="*80)
    
    # Get first vehicle
    vehicles_response = requests.get(f"{BASE_URL}/vehicles")
    if vehicles_response.status_code != 200 or len(vehicles_response.json()) == 0:
        print("No vehicles available to test")
        return None
    
    vehicle_id = vehicles_response.json()[0]['vehicle_id']
    
    # Update location
    location_data = {
        "x": 25.5,
        "y": 32.3
    }
    
    response = requests.put(
        f"{BASE_URL}/vehicles/{vehicle_id}/location",
        json=location_data
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        vehicle = response.json()
        print(f"Vehicle {vehicle_id} location updated:")
        print(f"  New Location: ({vehicle['current_location_x']}, {vehicle['current_location_y']})")
        print(f"  Updated At: {vehicle['updated_at']}")
    else:
        print(f"Error: {response.text}")
    
    return response


def test_create_route():
    """Test creating a new route."""
    print("\n" + "="*80)
    print("TEST: POST /api/routes")
    print("="*80)
    
    # Get vehicle and driver IDs
    vehicles_response = requests.get(f"{BASE_URL}/vehicles")
    if vehicles_response.status_code != 200 or len(vehicles_response.json()) == 0:
        print("No vehicles available")
        return None
    
    vehicle_id = vehicles_response.json()[0]['vehicle_id']
    
    # We need to know a driver ID - for now use 1 (from seed data)
    driver_id = 3  # driver1 from seed data
    
    route_data = {
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "start_location_x": 0.0,
        "start_location_y": 0.0,
        "end_location_x": None,
        "end_location_y": None,
        "route_status": "planned"
    }
    
    response = requests.post(
        f"{BASE_URL}/routes",
        json=route_data
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        route = response.json()
        print(f"Route created successfully:")
        print(f"  Route ID: {route['route_id']}")
        print(f"  Status: {route['route_status']}")
        print(f"  Start Time: {route['start_time']}")
        print(f"  Vehicle: {route['vehicle_id']}")
        print(f"  Driver: {route['driver_id']}")
    else:
        print(f"Error: {response.text}")
    
    return response


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("MediTrack API Endpoint Testing")
    print("="*80)
    
    try:
        # Test existing endpoints
        test_get_routes()
        test_get_route_details()
        test_get_vehicles()
        test_update_vehicle_location()
        test_create_route()
        
        print("\n" + "="*80)
        print("✓ All tests completed!")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API at http://localhost:8000")
        print("Make sure the backend server is running:")
        print("  cd backend && python -m uvicorn main:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    main()
