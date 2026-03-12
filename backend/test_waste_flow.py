#!/usr/bin/env python
import requests
import json
import time

BASE_URL = 'http://localhost:8000'

# 1. Reset database
print('1️⃣ Resetting database...')
response = requests.post(f'{BASE_URL}/api/reports/reset')
print(f'   Status: {response.status_code}')
time.sleep(1)

# 2. Create hospitals via API
print('2️⃣ Creating hospitals...')
hospitals_to_create = [
    {'label': 'H1', 'pixel_x': 10, 'pixel_y': 20, 'type': 'hospital', 'waste': 100},
    {'label': 'H2', 'pixel_x': 30, 'pixel_y': 40, 'type': 'hospital', 'waste': 150},
    {'label': 'D1', 'pixel_x': 0, 'pixel_y': 0, 'type': 'disposal', 'waste': 0},
]

hospital_ids = {}
for h in hospitals_to_create:
    response = requests.post(f'{BASE_URL}/api/nodes', json=h)
    if response.status_code == 201:
        data = response.json()
        label = h['label']
        hid = data.get('hospital_id')
        hospital_ids[label] = hid
        print(f'   Created {label} -> hospital_id {hid}')
    else:
        print(f'   Error creating {h["label"]}: {response.status_code} - {response.text}')

# 3. Create edges
print('3️⃣ Creating edges...')
edges_to_create = [
    {'from_hospital_id': 1, 'to_hospital_id': 2, 'distance_m': 100},
    {'from_hospital_id': 1, 'to_hospital_id': 3, 'distance_m': 150},
    {'from_hospital_id': 2, 'to_hospital_id': 3, 'distance_m': 80},
]

for e in edges_to_create:
    response = requests.post(f'{BASE_URL}/api/edges', json=e)
    if response.status_code == 201:
        print(f'   Created edge {e["from_hospital_id"]} -> {e["to_hospital_id"]}')
    else:
        print(f'   Error: {response.status_code}')

# 4. Check hospitals before route
print('4️⃣ Hospitals BEFORE route computation:')
response = requests.get(f'{BASE_URL}/api/nodes')
hospitals_before = response.json()
for h in hospitals_before:
    print(f'   ID {h["hospital_id"]}: {h["name"]} = {h["current_waste_kg"]}kg')

# 5. Compute route
print('5️⃣ Computing route...')
route_payload = {
    'truck_id': 1,
    'targets': [2, 3],
    'disposal_threshold': 0.8,
    'truck_capacity': 500
}
response = requests.post(f'{BASE_URL}/api/route/compute', json=route_payload)
if response.status_code == 200:
    route = response.json()
    print(f'   Route computed successfully')
    print(f'   Total distance: {route.get("total_distance_m")}m')
    print(f'   Total waste collected: {route.get("total_waste_collected_kg")}kg')
    print(f'   Disposal trips: {route.get("disposal_trips")}')
    print(f'   Events:')
    for event in route.get('events', []):
        print(f'      {event["event_type"]} at node {event["node_id"]}: {event["amount_kg"]}kg')
else:
    print(f'   Error: {response.status_code} - {response.text}')
    route = None

# 6. Update waste levels
if route:
    print('6️⃣ Updating waste levels...')
    waste_updates = {'hospitals': {}}
    for event in route.get('events', []):
        if event['event_type'] == 'pickup':
            waste_updates['hospitals'][str(event['node_id'])] = event['amount_kg']
    
    print(f'   Sending to backend: {waste_updates}')
    response = requests.post(f'{BASE_URL}/api/route/update-waste', json=waste_updates)
    if response.status_code == 200:
        result = response.json()
        print(f'   ✅ Response: {result}')
    else:
        print(f'   ❌ Error: {response.status_code} - {response.text}')
    
    # 7. Check hospitals AFTER waste update
    time.sleep(0.5)
    print('7️⃣ Hospitals AFTER waste update:')
    response = requests.get(f'{BASE_URL}/api/nodes')
    hospitals_after = response.json()
    for h in hospitals_after:
        before = next((x for x in hospitals_before if x['hospital_id'] == h['hospital_id']), {})
        before_waste = before.get('current_waste_kg', 0)
        after_waste = h['current_waste_kg']
        change = after_waste - before_waste
        change_str = f"({change:+.1f})" if change != 0 else ""
        print(f'   ID {h["hospital_id"]}: {h["name"]} = {after_waste}kg {change_str}')
