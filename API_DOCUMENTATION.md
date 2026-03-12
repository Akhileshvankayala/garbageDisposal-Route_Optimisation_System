# MediTrack API Documentation

## Overview

The MediTrack API provides comprehensive endpoints for managing biomedical waste collection routes, vehicle tracking, and driver operations. All endpoints return JSON responses with ISO-formatted datetime values.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently uses JWT token-based authentication. Include token in Authorization header:

```
Authorization: Bearer {token}
```

## Response Format

All endpoints return standardized JSON responses. Errors include appropriate HTTP status codes:

- **200 OK**: Success
- **201 Created**: Resource created
- **400 Bad Request**: Invalid input
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## Route Management Endpoints

### Routes Collection

#### Create a new route
```
POST /routes
Content-Type: application/json

{
  "vehicle_id": 1,
  "driver_id": 3,
  "start_location_x": 0.0,
  "start_location_y": 0.0,
  "route_status": "planned"
}

Response (200):
{
  "route_id": 1,
  "vehicle_id": 1,
  "driver_id": 3,
  "route_status": "planned",
  "start_time": "2026-01-23T20:45:30.123Z",
  "created_at": "2026-01-23T20:45:30.123Z"
}
```

#### List all routes
```
GET /routes?status=in_progress

Response (200):
[
  {
    "route_id": 1,
    "vehicle_id": 1,
    "driver_id": 3,
    "route_status": "in_progress",
    "total_distance_m": 85.5,
    "total_waste_collected_kg": 650.0,
    "num_disposal_trips": 2,
    "start_time": "2026-01-23T18:45:30.123Z",
    "end_time": null,
    "created_at": "2026-01-23T18:40:00.123Z"
  }
]
```

#### Get route details with all stops
```
GET /routes/{route_id}

Response (200):
{
  "route_id": 1,
  "vehicle_id": 1,
  "driver_id": 3,
  "route_status": "completed",
  "start_location_x": 0.0,
  "start_location_y": 0.0,
  "end_location_x": 0.0,
  "end_location_y": 0.0,
  "total_distance_m": 85.5,
  "total_waste_collected_kg": 650.0,
  "num_disposal_trips": 2,
  "start_time": "2026-01-23T18:45:30.123Z",
  "end_time": "2026-01-23T20:45:30.123Z",
  "stops": [
    {
      "stop_id": 1,
      "hospital_id": 2,
      "hospital_name": "City Hospital",
      "stop_sequence": 1,
      "arrival_time": "2026-01-23T18:52:15.123Z",
      "departure_time": "2026-01-23T19:07:45.123Z",
      "waste_collected_kg": 150.0,
      "vehicle_load_at_stop_kg": 300.0,
      "collections": [
        {
          "collection_id": 1,
          "bin_id": 5,
          "amount_kg": 80.0,
          "collection_time": "2026-01-23T18:55:00.123Z",
          "staff_name": "Staff-1",
          "notes": "Regular collection from City Hospital"
        }
      ]
    }
  ],
  "created_at": "2026-01-23T18:40:00.123Z",
  "updated_at": "2026-01-23T20:45:30.123Z"
}
```

#### Update route
```
PUT /routes/{route_id}
Content-Type: application/json

{
  "route_status": "completed",
  "end_location_x": 0.0,
  "end_location_y": 0.0,
  "total_distance_m": 95.5
}

Response (200):
{
  "route_id": 1,
  "vehicle_id": 1,
  "driver_id": 3,
  "route_status": "completed",
  "total_distance_m": 95.5,
  "total_waste_collected_kg": 650.0,
  "updated_at": "2026-01-23T20:50:00.123Z"
}
```

#### Start a route
```
POST /routes/{route_id}/start

Response (200):
{
  "route_id": 1,
  "route_status": "in_progress",
  "start_time": "2026-01-23T18:45:30.123Z",
  "updated_at": "2026-01-23T18:45:35.123Z"
}
```

#### Complete a route
```
POST /routes/{route_id}/complete

Response (200):
{
  "route_id": 1,
  "route_status": "completed",
  "start_time": "2026-01-23T18:45:30.123Z",
  "end_time": "2026-01-23T20:45:30.123Z",
  "updated_at": "2026-01-23T20:45:30.123Z"
}
```

---

## Route Stops Endpoints

#### Add stop to route
```
POST /routes/{route_id}/stops
Content-Type: application/json

{
  "hospital_id": 2,
  "stop_sequence": 1,
  "waste_collected_kg": 0.0,
  "vehicle_load_at_stop_kg": 0.0
}

Response (200):
{
  "stop_id": 1,
  "route_id": 1,
  "hospital_id": 2,
  "stop_sequence": 1,
  "waste_collected_kg": 0.0,
  "created_at": "2026-01-23T18:50:00.123Z"
}
```

#### List route stops
```
GET /routes/{route_id}/stops

Response (200):
[
  {
    "stop_id": 1,
    "route_id": 1,
    "hospital_id": 2,
    "hospital_name": "City Hospital",
    "stop_sequence": 1,
    "arrival_time": "2026-01-23T18:52:15.123Z",
    "departure_time": "2026-01-23T19:07:45.123Z",
    "waste_collected_kg": 150.0,
    "vehicle_load_at_stop_kg": 300.0
  }
]
```

#### Update stop (add arrival/departure times)
```
PUT /routes/stops/{stop_id}
Content-Type: application/json

{
  "arrival_time": "2026-01-23T18:52:15.123Z",
  "departure_time": "2026-01-23T19:07:45.123Z",
  "waste_collected_kg": 150.0
}

Response (200):
{
  "stop_id": 1,
  "arrival_time": "2026-01-23T18:52:15.123Z",
  "departure_time": "2026-01-23T19:07:45.123Z",
  "waste_collected_kg": 150.0
}
```

---

## Waste Collection Endpoints

#### Record waste collection
```
POST /routes/stops/{stop_id}/collections
Content-Type: application/json

{
  "bin_id": 5,
  "amount_kg": 80.0,
  "staff_name": "Staff-1",
  "notes": "Regular collection"
}

Response (200):
{
  "collection_id": 1,
  "stop_id": 1,
  "bin_id": 5,
  "amount_kg": 80.0,
  "collection_time": "2026-01-23T18:55:00.123Z",
  "staff_name": "Staff-1",
  "notes": "Regular collection",
  "created_at": "2026-01-23T18:55:00.123Z"
}
```

#### List collections for a stop
```
GET /routes/stops/{stop_id}/collections

Response (200):
[
  {
    "collection_id": 1,
    "stop_id": 1,
    "bin_id": 5,
    "amount_kg": 80.0,
    "collection_time": "2026-01-23T18:55:00.123Z",
    "staff_name": "Staff-1",
    "notes": "Regular collection",
    "created_at": "2026-01-23T18:55:00.123Z"
  }
]
```

---

## Vehicle Tracking Endpoints

#### Update vehicle location
```
PUT /vehicles/{vehicle_id}/location
Content-Type: application/json

{
  "x": 25.5,
  "y": 32.3
}

Response (200):
{
  "vehicle_id": 1,
  "current_location_x": 25.5,
  "current_location_y": 32.3,
  "updated_at": "2026-01-23T18:55:00.123Z"
}
```

#### Update vehicle load
```
PUT /vehicles/{vehicle_id}/load
Content-Type: application/json

{
  "load_kg": 500.0
}

Response (200):
{
  "vehicle_id": 1,
  "current_load_kg": 500.0,
  "capacity_kg": 1000.0,
  "load_percentage": 50.0,
  "updated_at": "2026-01-23T18:55:00.123Z"
}
```

#### Update vehicle status
```
PUT /vehicles/{vehicle_id}/status
Content-Type: application/json

{
  "status": "on_route"
}

Response (200):
{
  "vehicle_id": 1,
  "status": "on_route",
  "updated_at": "2026-01-23T18:55:00.123Z"
}
```

#### Get real-time tracking data
```
GET /vehicles/{vehicle_id}/tracking

Response (200):
{
  "vehicle_id": 1,
  "vehicle_name": "Truck-01",
  "status": "on_route",
  "current_location_x": 25.5,
  "current_location_y": 32.3,
  "current_load_kg": 500.0,
  "capacity_kg": 1000.0,
  "load_percentage": 50.0,
  "last_maintenance": "2025-12-24T10:30:00.123Z",
  "current_route_id": 1,
  "current_route_status": "in_progress"
}
```

#### List all vehicles with tracking
```
GET /vehicles

Response (200):
[
  {
    "vehicle_id": 1,
    "vehicle_name": "Truck-01",
    "status": "on_route",
    "current_location_x": 25.5,
    "current_location_y": 32.3,
    "current_load_kg": 500.0,
    "capacity_kg": 1000.0,
    "load_percentage": 50.0,
    "last_maintenance": "2025-12-24T10:30:00.123Z",
    "current_route_id": 1,
    "current_route_status": "in_progress"
  }
]
```

#### Record maintenance
```
POST /vehicles/{vehicle_id}/maintenance
Content-Type: application/json

{
  "notes": "Regular service"
}

Response (200):
{
  "vehicle_id": 1,
  "last_maintenance": "2026-01-23T18:55:00.123Z",
  "notes": "Regular service"
}
```

---

## Driver Operations Endpoints

#### Get assigned routes
```
GET /drivers/{driver_id}/assigned-routes

Response (200):
[
  {
    "route_id": 1,
    "vehicle_id": 1,
    "route_status": "in_progress",
    "start_time": "2026-01-23T18:45:30.123Z",
    "end_time": null
  }
]
```

#### Get current active route
```
GET /drivers/{driver_id}/current-route

Response (200):
{
  "route_id": 1,
  "vehicle_id": 1,
  "route_status": "in_progress",
  "start_time": "2026-01-23T18:45:30.123Z",
  "end_time": null
}
```

#### Confirm arrival at stop
```
POST /drivers/routes/{route_id}/stops/{stop_id}/confirm-arrival

Response (200):
{
  "stop_id": 1,
  "arrival_time": "2026-01-23T18:52:15.123Z",
  "status": "Arrival confirmed"
}
```

#### Confirm departure from stop
```
POST /drivers/routes/{route_id}/stops/{stop_id}/confirm-departure

Response (200):
{
  "stop_id": 1,
  "departure_time": "2026-01-23T19:07:45.123Z",
  "status": "Departure confirmed"
}
```

#### Record waste collection
```
POST /drivers/routes/{route_id}/stops/{stop_id}/record-collection
Content-Type: application/json

{
  "bin_id": 5,
  "amount_kg": 80.0,
  "staff_name": "Staff-1",
  "notes": "Regular collection"
}

Response (200):
{
  "collection_id": 1,
  "stop_id": 1,
  "amount_kg": 80.0,
  "collection_time": "2026-01-23T18:55:00.123Z",
  "staff_name": "Staff-1",
  "notes": "Regular collection"
}
```

#### Get route summary
```
GET /drivers/routes/{route_id}/summary

Response (200):
{
  "route_id": 1,
  "vehicle_id": 1,
  "driver_id": 3,
  "route_status": "in_progress",
  "total_duration_minutes": 120,
  "stops": [
    {
      "stop_id": 1,
      "hospital_name": "City Hospital",
      "stop_sequence": 1,
      "arrival_time": "2026-01-23T18:52:15.123Z",
      "departure_time": "2026-01-23T19:07:45.123Z",
      "stop_duration_minutes": 15,
      "waste_collected_kg": 150.0
    }
  ],
  "total_waste_collected_kg": 650.0,
  "collections_count": 6
}
```

---

## Data Types

### Route Status
- `planned`: Route created but not started
- `in_progress`: Route is currently active
- `completed`: Route finished successfully
- `cancelled`: Route was cancelled

### Vehicle Status
- `idle`: Vehicle is idle and available
- `on_route`: Vehicle is currently executing a route
- `at_disposal`: Vehicle at disposal center
- `maintenance`: Vehicle in maintenance

---

## Error Handling

All errors include an error message. Common error responses:

### 404 Not Found
```json
{
  "detail": "Route not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Cannot start route with status completed"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message describing the server error"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. Future implementations may include rate limiting.

---

## Datetime Format

All datetime values are in ISO 8601 format with UTC timezone:
```
2026-01-23T20:45:30.123456Z
```

When sending datetime values, use the same format or standard RFC 3339 format.

---

## Examples

### Complete Route Workflow

1. **Create Route**
   ```
   POST /routes → route_id: 1
   ```

2. **Add Stops**
   ```
   POST /routes/1/stops → stop_id: 1
   POST /routes/1/stops → stop_id: 2
   ```

3. **Start Route**
   ```
   POST /routes/1/start
   ```

4. **Confirm Arrival**
   ```
   POST /drivers/routes/1/stops/1/confirm-arrival
   ```

5. **Record Collection**
   ```
   POST /drivers/routes/1/stops/1/record-collection
   ```

6. **Confirm Departure**
   ```
   POST /drivers/routes/1/stops/1/confirm-departure
   ```

7. **Complete Route**
   ```
   POST /routes/1/complete
   ```

8. **View Summary**
   ```
   GET /drivers/routes/1/summary
   ```

---

## Frontend Integration Examples

### React Hook for Route Fetching
```typescript
const [route, setRoute] = useState(null);

useEffect(() => {
  fetch(`http://localhost:8000/api/routes/${routeId}`)
    .then(r => r.json())
    .then(data => setRoute(data));
}, [routeId]);
```

### Vehicle Tracking Update
```typescript
const updateVehicleLocation = async (vehicleId, x, y) => {
  const response = await fetch(
    `http://localhost:8000/api/vehicles/${vehicleId}/location`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x, y })
    }
  );
  return response.json();
};
```

---

**Last Updated**: January 23, 2026  
**API Version**: 1.0.0  
**Status**: Production Ready
