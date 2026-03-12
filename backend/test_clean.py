#!/usr/bin/env python
import requests
import time

BASE_URL = 'http://localhost:8000'

print('=' * 60)
print('WASTE COLLECTION SYSTEM TEST')
print('=' * 60)

# Step 1: Reset
print('\n[1] Resetting database...')
r = requests.post(f'{BASE_URL}/api/reports/reset')
assert r.status_code == 200, f"Reset failed: {r.status_code}"
print('[OK] Database reset')
time.sleep(0.5)

# Step 2: Create hospitals
print('\n[2] Creating hospitals...')
hospitals = [
    {'name': 'Hospital 1', 'location_x': 10, 'location_y': 20, 'current_waste_kg': 100, 'max_bin_capacity': 500},
    {'name': 'Hospital 2', 'location_x': 30, 'location_y': 40, 'current_waste_kg': 150, 'max_bin_capacity': 500},
    {'name': 'Disposal Center A', 'location_x': 0, 'location_y': 0, 'current_waste_kg': 0, 'max_bin_capacity': 10000},
]

hospital_ids = {}
for h in hospitals:
    r = requests.post(f'{BASE_URL}/api/nodes', json=h)
    assert r.status_code == 201, f"Failed to create hospital: {r.status_code} - {r.text}"
    data = r.json()
    hospital_ids[h['name']] = data['hospital_id']
    print(f"  Created: {h['name']} (ID: {data['hospital_id']})")
time.sleep(0.5)

# Step 3: Create edges
print('\n[3] Creating edges...')
edges = [
    {'from_hospital_id': 1, 'to_hospital_id': 2, 'distance_m': 100},
    {'from_hospital_id': 1, 'to_hospital_id': 3, 'distance_m': 150},
    {'from_hospital_id': 2, 'to_hospital_id': 3, 'distance_m': 80},
]

for e in edges:
    r = requests.post(f'{BASE_URL}/api/edges', json=e)
    assert r.status_code == 201, f"Failed to create edge: {r.status_code}"
    print(f"  Created: {e['from_hospital_id']} -> {e['to_hospital_id']}")

# Step 4: Check waste BEFORE
print('\n[4] Waste levels BEFORE collection:')
r = requests.get(f'{BASE_URL}/api/nodes')
hospitals_before = {h['hospital_id']: h for h in r.json()}
for hid, h in sorted(hospitals_before.items()):
    print(f"  ID {hid}: {h['name']} = {h['current_waste_kg']}kg")

# Step 5: Compute route
print('\n[5] Computing route...')
payload = {'truck_id': 1, 'targets': [2], 'disposal_threshold': 0.8, 'truck_capacity': 500}
r = requests.post(f'{BASE_URL}/api/route/compute', json=payload)
assert r.status_code == 200, f"Route compute failed: {r.status_code} - {r.text}"
route = r.json()
print(f"  Distance: {route['total_distance_m']}m")
print(f"  Waste collected: {route['total_waste_collected_kg']}kg")
print(f"  Events:")
for event in route.get('events', []):
    print(f"    {event['event_type']} at node {event['node_id']}: {event['amount_kg']}kg")

# Step 6: Update waste
print('\n[6] Updating waste levels...')
waste_updates = {'hospitals': {}}
for event in route.get('events', []):
    if event['event_type'] == 'pickup':
        waste_updates['hospitals'][str(event['node_id'])] = event['amount_kg']

print(f"  Sending: {waste_updates}")
r = requests.post(f'{BASE_URL}/api/route/update-waste', json=waste_updates)
assert r.status_code == 200, f"Waste update failed: {r.status_code} - {r.text}"
result = r.json()
print(f"  [OK] {result['message']}")
print(f"     Hospitals updated: {result['hospital_ids']}")
print(f"     Total waste: {result['total_waste_collected_kg']}kg")
print(f"     Disposal center: {result.get('disposal_center_name', 'None')}")

# Step 7: Check waste AFTER
print('\n[7] Waste levels AFTER collection:')
r = requests.get(f'{BASE_URL}/api/nodes')
hospitals_after = {h['hospital_id']: h for h in r.json()}
for hid, h in sorted(hospitals_after.items()):
    before = hospitals_before[hid]['current_waste_kg']
    after = h['current_waste_kg']
    change = after - before
    change_str = f"({change:+.1f}kg)" if change != 0 else ""
    print(f"  ID {hid}: {h['name']} = {after}kg {change_str}")

print('\n' + '=' * 60)
print('SUMMARY')
print('=' * 60)
print(f"Hospital 1: {hospitals_before[2]['current_waste_kg']}kg -> {hospitals_after[2]['current_waste_kg']}kg (expected 0)")
print(f"Hospital 2: {hospitals_before[3]['current_waste_kg']}kg -> {hospitals_after[3]['current_waste_kg']}kg (expected 0)")
print(f"Disposal A: {hospitals_before[4]['current_waste_kg']}kg -> {hospitals_after[4]['current_waste_kg']}kg (expected 150)")
print('=' * 60)
