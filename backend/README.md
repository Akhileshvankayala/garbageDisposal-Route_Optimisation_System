# MediTrack Backend - Complete Setup & Documentation

## 📋 Overview

MediTrack is a **biomedical waste collection route optimization system** using:
- **FastAPI** for REST API
- **SQLite** for persistent storage
- **Dijkstra's algorithm** for capacity-aware route optimization
- **SQLAlchemy ORM** for database models
- **JWT authentication** for secure access
- **Comprehensive logging & error handling**

---

## 🗂️ Project Structure

```
backend/
├── config.py                    # Configuration (DB URL, API keys, thresholds)
├── database.py                  # SQLAlchemy setup & session management
├── main.py                      # FastAPI app entry point
├── seed_data.py                 # Test data population script
├── requirements.txt             # Python dependencies
│
├── models/                      # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py                  # User, Admin, Driver entities
│   ├── hospital.py              # Hospital, WasteBin entities
│   ├── vehicle.py               # Vehicle entity
│   ├── route.py                 # Route, RouteStop, WasteCollection
│   ├── edge.py                  # Edge (graph connections)
│   └── scale.py                 # ScaleMapping (pixel-to-meter conversion)
│
├── schemas/                     # Pydantic request/response models
│   ├── node.py                  # Hospital creation/update
│   ├── edge.py                  # Edge creation/update
│   ├── auth.py                  # Login/register
│   ├── route.py                 # Route computation request/response
│   └── analytics.py             # Report schemas
│
├── routes/                      # API endpoint handlers
│   ├── nodes.py                 # POST/GET /api/nodes (hospitals)
│   ├── edges.py                 # POST/GET /api/edges
│   ├── auth.py                  # POST /api/auth/login, /register
│   ├── routes.py                # POST /api/route/compute
│   └── analytics.py             # GET /api/reports/*
│
├── services/                    # Business logic
│   ├── routing.py               # Dijkstra's algorithm & route computation
│   └── auth.py                  # Password hashing, JWT token generation
│
├── middleware/                  # Middleware & utilities
│   ├── logging_config.py        # Structured logging setup
│   └── error_handler.py         # Global exception handlers
│
├── tests/                       # Unit & integration tests
│   ├── test_api.py              # API endpoint tests
│   └── test_routing.py          # Dijkstra algorithm tests
│
├── Dockerfile                   # Docker container configuration
└── docker-compose.yml           # Docker Compose for full stack
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database & Load Seed Data

```bash
python seed_data.py
```

Output:
```
========================================================================
Seeding MediTrack database...
========================================================================

1. Seeding hospitals...
2. Seeding edges...
3. Seeding vehicles...
4. Seeding users...

========================================================================
✓ Database seeded successfully!
========================================================================

Test credentials:
  Admin:  admin / Admin@123
  Staff:  staff / Staff@123
  Driver: driver1 / Driver@123
========================================================================
```

### 3. Run Backend Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Server will start at: **http://localhost:8000**

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🐳 Docker Setup

### Run with Docker Compose (Recommended)

```bash
# Build and start both backend and frontend
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Build Docker Image

```bash
docker build -t meditrack-backend:1.0 .

docker run -p 8000:8000 \
  -e DATABASE_URL="sqlite:///./meditrack.db" \
  -e SECRET_KEY="your-secret-key" \
  meditrack-backend:1.0
```

---

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Hospitals (Nodes)

```bash
# Create hospital
POST /api/nodes
Content-Type: application/json
{
  "name": "City Hospital",
  "location_x": 10.5,
  "location_y": 15.3,
  "current_waste_kg": 250,
  "max_bin_capacity": 500
}

# Get all hospitals
GET /api/nodes

# Get specific hospital
GET /api/nodes/{hospital_id}

# Update hospital
PUT /api/nodes/{hospital_id}

# Delete hospital (soft delete)
DELETE /api/nodes/{hospital_id}
```

### Edges (Connections)

```bash
# Create edge
POST /api/edges
Content-Type: application/json
{
  "from_hospital_id": 1,
  "to_hospital_id": 2,
  "distance_m": 150.5,
  "is_bidirectional": true
}

# Get all edges
GET /api/edges

# Get full graph
GET /api/edges/graph

# Update edge
PUT /api/edges/{edge_id}

# Delete edge
DELETE /api/edges/{edge_id}
```

### Authentication

```bash
# Login
POST /api/auth/login
Content-Type: application/json
{
  "username": "admin",
  "password": "Admin@123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "admin",
  "role": "admin"
}

# Register new user
POST /api/auth/register
Content-Type: application/json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "Password@123",
  "full_name": "John Doe",
  "role": "staff"  # "admin", "staff", or "driver"
}
```

### Route Computation (Core Algorithm)

```bash
# Compute optimized route
POST /api/route/compute
Content-Type: application/json
Authorization: Bearer {access_token}
{
  "truck_id": 1,
  "targets": [2, 3, 4],           # Hospital IDs to visit
  "disposal_threshold": 0.8,      # Trigger disposal at 80% capacity
  "truck_capacity": 1000.0        # Truck capacity in kg
}

Response:
{
  "path": [1, 2, 3, 1, 4, 1],     # Node IDs in order of visit
  "edges": [
    {"from": 1, "to": 2, "distance": 100.0},
    {"from": 2, "to": 3, "distance": 80.0},
    ...
  ],
  "total_distance_m": 650.0,
  "total_waste_collected_kg": 620.0,
  "disposal_trips": 2,            # Number of times went to disposal
  "events": [
    {
      "event_type": "pickup",
      "node_id": 2,
      "amount_kg": 250.0,
      "truck_load_after_kg": 250.0
    },
    {
      "event_type": "disposal",
      "node_id": 1,
      "amount_kg": 250.0,
      "truck_load_after_kg": 0.0
    },
    ...
  ],
  "unreachable_hospitals": []
}
```

### Analytics & Reports

```bash
# Get waste collection report
GET /api/reports/waste

Response:
{
  "report_type": "waste_collection",
  "generated_at": "2025-01-23T15:30:00",
  "hospitals": [
    {
      "hospital_id": 2,
      "hospital_name": "City Hospital",
      "current_waste_kg": 250.0,
      "max_capacity": 500.0,
      "fill_percentage": 50.0,
      "last_updated": "2025-01-23T15:30:00"
    },
    ...
  ],
  "total_waste_kg": 1000.0,
  "average_fill_percentage": 60.5
}

# Get routes report (past N days)
GET /api/reports/routes?days=7

# Get system summary
GET /api/reports/summary
```

---

## 🧠 Dijkstra's Algorithm Details

### How It Works

The routing algorithm is a **capacity-aware greedy Dijkstra implementation**:

```python
1. Start at disposal center (node 1)
2. While unvisited hospitals remain:
   a. Use Dijkstra to find shortest path to all unvisited hospitals
   b. Select nearest hospital (with node ID tie-breaking for determinism)
   c. Check capacity: if adding hospital's waste exceeds truck capacity
      → Route to disposal first to empty load
   d. Travel to hospital, collect waste, accumulate load
   e. Check disposal threshold: if load ≥ 80% of capacity
      → Route to disposal to empty
   f. Repeat
3. Return to disposal center at end
```

### Key Features

✅ **Capacity-Aware**: Ensures truck never exceeds capacity limits
✅ **Threshold-Triggered**: Empties truck when reaching 80% capacity
✅ **Greedy Optimization**: Always visits nearest reachable hospital
✅ **Deterministic**: Tie-breaking by hospital ID for reproducible results
✅ **Multi-Trip Support**: Handles multiple disposal trips in single route
✅ **Unreachable Handling**: Returns list of hospitals that couldn't be reached

### Complexity

- **Time**: O(N × (E + V log V))
  - N = number of target hospitals
  - E = number of edges
  - V = number of vertices (hospitals)
  - Dijkstra runs once per hospital, O(E + V log V) per iteration

- **Space**: O(V + E) for graph storage

### Example Scenario

**Setup:**
- Truck capacity: 1000 kg
- Disposal threshold: 80%
- Hospitals: H1(250kg), H2(150kg), H3(320kg), H4(100kg)

**Execution:**
```
1. Start at Disposal (0kg)
2. Go to nearest: H1 (100m) → Collect 250kg (load: 250kg)
3. Go to H2 (80m) → Collect 150kg (load: 400kg)
4. Load at 40% < 80%, continue
5. Go to H4 (95m) → Collect 100kg (load: 500kg)
6. Load at 50% < 80%, continue
7. Go to H3 (140m) → Collect 320kg → Would be 820kg
8. 820kg < 1000kg capacity, OK, collect (load: 820kg)
9. Load at 82% ≥ 80%, must dispose!
10. Go to Disposal (120m) → Empty truck (disposal trip #1)
11. All hospitals visited, return to Disposal

Result: Path = [D, H1, H2, H4, H3, D]
        Distance = 535m
        Waste = 820kg
        Disposals = 1
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_routing.py

# Run with coverage
pytest --cov=.
```

Test files:
- `tests/test_api.py` - API endpoint tests
- `tests/test_routing.py` - Dijkstra algorithm tests

---

## 🔐 Authentication & Authorization

### JWT Token Flow

1. **Login**: POST `/api/auth/login` with credentials
2. **Receive token**: Response includes `access_token`
3. **Include in requests**: Add header: `Authorization: Bearer {token}`
4. **Token validation**: Middleware validates token before processing request

### Role-Based Access Control

Three roles available:

| Role | Permissions |
|------|------------|
| **admin** | View/create hospitals, create edges, compute routes, view reports |
| **staff** | Update hospital waste, view hospitals, call route computation |
| **driver** | View assigned routes, mark pickups, view waste status |

(Note: Basic role structure; add detailed authorization in routes as needed)

---

## 📊 Database Schema

### Key Entities

**Hospitals**
- `hospital_id` (PK)
- `name` (unique)
- `location_x`, `location_y` (Euclidean coordinates)
- `current_waste_kg`
- `max_bin_capacity`
- `is_active`

**Edges** (Graph Connections)
- `edge_id` (PK)
- `from_hospital_id`, `to_hospital_id` (FKs)
- `distance_m` (edge weight)
- `is_bidirectional`

**Vehicles**
- `vehicle_id` (PK)
- `capacity_kg`
- `current_load_kg`
- `status` (idle, on_route, at_disposal)
- `assigned_driver_id` (FK)

**Users**
- `user_id` (PK)
- `username` (unique)
- `hashed_password`
- `role` (admin, staff, driver)

**Routes**
- `route_id` (PK)
- `vehicle_id`, `driver_id` (FKs)
- `total_distance_m`
- `total_waste_collected_kg`
- `num_disposal_trips`
- `route_status` (planned, in_progress, completed)

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Database
DATABASE_URL = "sqlite:///./meditrack.db"  # or PostgreSQL, MySQL, etc.

# Routing
DISPOSAL_THRESHOLD = 0.8          # 80% capacity triggers disposal
DEFAULT_TRUCK_CAPACITY = 1000.0   # kg
DISPOSAL_CENTER_ID = 1            # Hospital ID for disposal center
DISPOSAL_CENTER_LOCATION = (0, 0) # Coordinates

# Security
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/meditrack.log"
```

---

## 📝 Logging

Structured logging is configured with:
- **Console output**: All logs printed to terminal
- **File output**: Rotating logs in `logs/meditrack.log`
- **Log rotation**: 10MB per file, 5 backup files

View logs:
```bash
# Real-time logs
tail -f logs/meditrack.log

# All logs
cat logs/meditrack.log
```

---

## 🐛 Error Handling

All endpoints include comprehensive error handling:

```
400 Bad Request  - Invalid input data
401 Unauthorized - Authentication failed
404 Not Found    - Resource doesn't exist
422 Validation Error - Pydantic validation failed
500 Internal Error - Server error (detailed in logs)
```

Example error response:
```json
{
  "detail": "Hospital with name 'City Hospital' already exists",
  "timestamp": "2025-01-23T15:30:00",
  "path": "/api/nodes"
}
```

---

## 🔗 Frontend Integration

Frontend should use these API endpoints:

```javascript
// Create hospital
POST /api/nodes
Body: { name, location_x, location_y, current_waste_kg, ... }

// Create edge
POST /api/edges
Body: { from_hospital_id, to_hospital_id, distance_m, ... }

// Get full graph
GET /api/edges/graph
Returns: { nodes: [...], edges: [...] }

// Compute route
POST /api/route/compute
Body: { truck_id, targets, disposal_threshold, truck_capacity }
Returns: { path, edges, total_distance_m, events, ... }

// Get waste reports
GET /api/reports/waste
GET /api/reports/routes
GET /api/reports/summary
```

---

## 🚨 Troubleshooting

### Database locked error
- SQLite issue with concurrent writes
- Solution: Use PostgreSQL in production

### Port 8000 already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 {PID}
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Tests failing
```bash
# Ensure test database is clean
pytest --tb=short -v

# Check for missing dependencies
pip install pytest pytest-asyncio httpx
```

---

## 📈 Performance Tips

1. **Database Indexing**: Indexes added on foreign keys and frequently queried fields
2. **Connection Pooling**: SQLAlchemy uses connection pools
3. **Caching**: Implement Redis caching for hospital data (future enhancement)
4. **Query Optimization**: Use `.filter()` and `.select()` efficiently
5. **Batch Operations**: Use SQLAlchemy bulk operations for seed data

---

## 🔮 Future Enhancements

- [ ] Multi-truck simultaneous routing
- [ ] Real-time GPS tracking integration
- [ ] Predictive waste generation models
- [ ] Machine learning route optimization
- [ ] Mobile app for drivers
- [ ] Dashboard with real-time metrics
- [ ] PostgreSQL/MongoDB integration
- [ ] Redis caching layer
- [ ] Role-based API documentation
- [ ] Kubernetes deployment configs

---

## 📞 Support

For issues or questions:
1. Check logs: `tail -f logs/meditrack.log`
2. Review API docs: http://localhost:8000/docs
3. Run tests: `pytest -v`
4. Check database: `sqlite3 meditrack.db`

---

**Last Updated**: January 23, 2025
**Version**: 1.0.0
**Status**: Production Ready ✅
