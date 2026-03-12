# 🎬 MediTrack - Complete System Walkthrough

Welcome to MediTrack! This guide walks you through the complete system architecture and how to use it.

---

## 📺 System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│          - Hospital playground visualization           │
│          - Edge creation & management                  │
│          - Role-based login (Admin/Staff/Driver)      │
│          - Route animation                             │
│          - Undo/Redo support                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ HTTP REST API
                  │ (JSON over HTTPS)
                  ↓
┌─────────────────────────────────────────────────────────┐
│                 BACKEND (FastAPI)                       │
│  ┌───────────────────────────────────────────────────┐ │
│  │           20+ API Endpoints                      │ │
│  │  - /api/nodes (hospitals CRUD)                  │ │
│  │  - /api/edges (connections CRUD)               │ │
│  │  - /api/route/compute (Dijkstra)              │ │
│  │  - /api/auth (login/register)                 │ │
│  │  - /api/reports (analytics)                   │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │    Business Logic Services                      │ │
│  │  - Dijkstra's Algorithm (routing.py)           │ │
│  │  - Authentication (auth.py)                    │ │
│  │  - Logging & Error Handling                    │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ SQLAlchemy ORM
                  ↓
┌─────────────────────────────────────────────────────────┐
│                 DATABASE (SQLite)                       │
│  ┌───────────────────────────────────────────────────┐ │
│  │  12 Tables (Entities & Relationships)           │ │
│  │  - hospitals, vehicles, routes, edges...        │ │
│  │  - users, admins, drivers (auth)               │ │
│  │  - waste_collections, pickup_records           │ │
│  │  - scale_mappings (pixel-meter conversion)     │ │
│  └───────────────────────────────────────────────────┘ │
│  meditrack.db (SQLite file)                             │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Complete Getting Started Guide

### Step 1: Install Everything

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt
```

**What gets installed:**
- FastAPI (web framework)
- SQLAlchemy (ORM)
- NetworkX (graph algorithms)
- JWT & Password hashing
- Testing frameworks
- Docker support

### Step 2: Initialize the Database

```bash
python seed_data.py
```

**This creates:**
- SQLite database (`meditrack.db`)
- 6 hospitals + 1 disposal center
- 12 edges (connections)
- 3 test vehicles
- 4 test users

**Test credentials:**
```
Admin:  username=admin,  password=Admin@123
Staff:  username=staff,  password=Staff@123
Driver: username=driver1, password=Driver@123
```

### Step 3: Start the Backend Server

```bash
python main.py
```

Expected output:
```
================================================================================
MediTrack API Starting...
================================================================================
✓ Database initialized
✓ Database tables created successfully
✓ Application ready to serve requests

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Backend is now at**: http://localhost:8000
**API Documentation**: http://localhost:8000/docs

### Step 4: Start the Frontend

In a new terminal:
```bash
npm run dev
```

**Frontend is now at**: http://localhost:5173

### Step 5: Test the System

1. **Open frontend**: http://localhost:5173
2. **Login as Admin**: admin / Admin@123
3. **Create hospitals** in the playground (click "Build Playground" → "Add Node")
4. **Connect hospitals** with edges (click "Connect Nodes" → select 2 nodes)
5. **Compute route**: Click "View Optimized Route" to run Dijkstra's algorithm
6. **Watch animation**: See truck visiting hospitals in order

---

## 🎯 Feature Walkthrough

### Feature 1: Hospital Management (Admin)

**Create Hospital**
```bash
POST /api/nodes
{
  "name": "City Hospital",
  "location_x": 10.5,
  "location_y": 15.3,
  "current_waste_kg": 250,
  "max_bin_capacity": 500
}
```

**Update Hospital Waste (Staff)**
```bash
PUT /api/nodes/2
{
  "current_waste_kg": 350
}
```

**Get All Hospitals**
```bash
GET /api/nodes
```

### Feature 2: Edge Creation (Admin)

**Create Edge/Connection**
```bash
POST /api/edges
{
  "from_hospital_id": 1,
  "to_hospital_id": 2,
  "distance_m": 150.5,
  "is_bidirectional": true
}
```

**Get Full Graph**
```bash
GET /api/edges/graph
```

Returns:
```json
{
  "nodes": [
    {"hospital_id": 1, "name": "Disposal", "x": 0, "y": 0, "waste": 0},
    {"hospital_id": 2, "name": "City Hospital", "x": 10.5, "y": 15.3, "waste": 250}
  ],
  "edges": [
    {"edge_id": 1, "from": 1, "to": 2, "distance_m": 150.5}
  ]
}
```

### Feature 3: Route Optimization (All Roles)

**Compute Optimal Route**
```bash
POST /api/route/compute
{
  "truck_id": 1,
  "targets": [2, 3, 4],      # Hospitals to visit
  "disposal_threshold": 0.8,  # 80% = empty truck
  "truck_capacity": 1000.0    # kg
}
```

**Response with Complete Route Plan:**
```json
{
  "path": [1, 2, 3, 1, 4, 1],
  "edges": [
    {"from": 1, "to": 2, "distance": 100},
    {"from": 2, "to": 3, "distance": 80}
  ],
  "total_distance_m": 650,
  "total_waste_collected_kg": 620,
  "disposal_trips": 2,
  "events": [
    {
      "event_type": "pickup",
      "node_id": 2,
      "amount_kg": 250,
      "truck_load_after_kg": 250
    },
    {
      "event_type": "disposal",
      "node_id": 1,
      "amount_kg": 250,
      "truck_load_after_kg": 0
    }
  ],
  "unreachable_hospitals": []
}
```

### Feature 4: Analytics & Reporting (Admin)

**Waste Collection Report**
```bash
GET /api/reports/waste
```

**Route Summary (past 7 days)**
```bash
GET /api/reports/routes?days=7
```

**System Overview**
```bash
GET /api/reports/summary
```

---

## 🧠 How Dijkstra's Algorithm Works in MediTrack

### The Algorithm Step-by-Step

Imagine you have:
- 🏥 Hospital A (250kg waste), 100m from disposal
- 🏥 Hospital B (150kg waste), 80m from Hospital A
- 🏥 Hospital C (320kg waste), 140m from Hospital B
- 🚚 Truck capacity: 1000kg
- 📊 Disposal threshold: 80% (800kg)

**Execution:**

```
Step 1: Start at Disposal (0kg load)
        Location: Disposal Center
        Load: 0kg

Step 2: Find nearest hospital
        Option A: 100m away, has 250kg
        Option B: 170m away (100+80), has 150kg
        Option C: 240m away, has 320kg
        → Choose A (nearest)

Step 3: Travel to A and collect waste
        Location: Hospital A
        Load: 250kg (added 250kg)
        Load%: 250/1000 = 25% < 80% threshold
        → No disposal needed

Step 4: Find next nearest hospital (from A)
        Option B: 80m away, has 150kg
        Option C: 240m away, has 320kg
        → Choose B (nearest)

Step 5: Travel to B and collect
        Location: Hospital B
        Load: 400kg (added 150kg)
        Load%: 400/1000 = 40% < 80%
        → No disposal needed

Step 6: Find next hospital (from B)
        Option C: 140m away, has 320kg
        Check capacity: 400 + 320 = 720kg < 1000kg ✓
        → Go to C

Step 7: Travel to C and collect
        Location: Hospital C
        Load: 720kg (added 320kg)
        Load%: 720/1000 = 72% < 80%
        → No disposal needed

Step 8: All hospitals visited
        Load is 720kg < 800kg
        But we've collected all waste
        → Return to Disposal

Step 9: Travel back to Disposal
        Location: Disposal Center
        Load: 720kg → 0kg (emptied)
        Disposal trips: 1

Final Route: [Disposal, A, B, C, Disposal]
Total Distance: 100 + 80 + 140 + 140 = 460m
Total Waste: 720kg
Disposal Trips: 1
```

### Key Points

✅ **Greedy Nearest-Neighbor**: Always picks closest unvisited hospital
✅ **Capacity Constraint**: Never exceeds truck capacity
✅ **Disposal Threshold**: Empties truck at 80% capacity
✅ **Deterministic**: Same results every time (tie-breaking by node ID)
✅ **Multi-Trip**: Can make multiple disposal trips if needed
✅ **Unreachable Tracking**: Reports hospitals that can't be reached

---

## 🔐 Authentication Flow

### Login Process

```
1. User enters credentials
   ↓
2. Frontend: POST /api/auth/login
   {
     "username": "admin",
     "password": "Admin@123"
   }
   ↓
3. Backend:
   - Hash password using bcrypt
   - Compare with stored hash
   - If match: Create JWT token
   ↓
4. Response:
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "bearer",
     "user_id": 1,
     "username": "admin",
     "role": "admin"
   }
   ↓
5. Frontend stores token in localStorage
   ↓
6. All API requests include token:
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ↓
7. Backend validates token before processing request
```

### Creating New User

```bash
POST /api/auth/register
{
  "username": "newuser",
  "email": "user@hospital.com",
  "password": "SecurePass123",
  "full_name": "Dr. John Doe",
  "role": "staff"  # "admin", "staff", or "driver"
}
```

---

## 📊 Database Schema Visualization

### Simplified Data Model

```
                Users
                 / \
                /   \
            Admin   Driver
                     |
                     |
              Vehicles (Trucks)
                     |
                     |
              Routes & RouteStops
                    / \
                   /   \
            Hospitals  WasteBins
                |
            WasteCollections
            
Edges connect:
Hospitals ←→ Hospitals (graph connections)
```

### Key Tables

**hospitals**
```
hospital_id | name           | location_x | location_y | current_waste_kg
1           | Disposal       | 0          | 0          | 0
2           | City Hospital  | 10.5       | 15.3       | 250
3           | Central Clinic | 20         | 10         | 180
...
```

**edges**
```
edge_id | from_hospital_id | to_hospital_id | distance_m | is_bidirectional
1       | 1                | 2              | 100.0      | true
2       | 2                | 3              | 80.0       | true
...
```

**users**
```
user_id | username | email              | role   | is_active
1       | admin    | admin@meditrack    | admin  | true
2       | staff    | staff@meditrack    | staff  | true
3       | driver1  | driver1@meditrack  | driver | true
```

---

## 🧪 Testing the System

### Automated Tests

```bash
# Run all tests
pytest -v

# Test specific module
pytest tests/test_routing.py -v

# Test with coverage
pytest --cov=.
```

### Manual Testing with Swagger

1. Navigate to: http://localhost:8000/docs
2. Click "Authorize" button
3. Login with test credentials
4. Try endpoints interactively
5. View responses in real-time

### Curl Examples

```bash
# Create hospital
curl -X POST http://localhost:8000/api/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Hospital",
    "location_x": 25,
    "location_y": 30,
    "current_waste_kg": 200
  }'

# Get all hospitals
curl http://localhost:8000/api/nodes

# Compute route (need token first)
RESPONSE=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')

curl -X POST http://localhost:8000/api/route/compute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "truck_id": 1,
    "targets": [2, 3, 4],
    "disposal_threshold": 0.8,
    "truck_capacity": 1000
  }'
```

---

## 🐛 Troubleshooting

### Issue: "Database is locked"
**Solution**: Close other connections and restart backend

### Issue: "Port 8000 already in use"
**Solution**: 
```bash
# Kill process on port 8000
lsof -i :8000  # Find PID
kill -9 <PID>
```

### Issue: "CORS error" in frontend
**Solution**: Ensure backend is running and CORS is configured (it is by default)

### Issue: "No module named 'fastapi'"
**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: Tests failing
**Solution**: 
```bash
# Make sure pytest is installed
pip install pytest pytest-asyncio httpx

# Run with verbose output
pytest -v --tb=short
```

---

## 📈 Performance Considerations

### Database
- Indexes on all foreign keys ✅
- Indexes on frequently queried columns ✅
- Connection pooling ✅
- Query optimization ✅

### API
- Async endpoints ✅
- Fast JSON validation (Pydantic) ✅
- Pagination on list endpoints ✅
- Efficient query filtering ✅

### Algorithm
- Single-source Dijkstra O(E + V log V) ✅
- Greedy nearest-neighbor ✅
- No redundant computations ✅

---

## 🎓 Learning Resources

### For Dijkstra's Algorithm:
- Wikipedia: https://en.wikipedia.org/wiki/Dijkstra's_algorithm
- Visualization: https://www.freecodecamp.org/news/dijkstras-algorithm-explained/

### For FastAPI:
- Official docs: https://fastapi.tiangolo.com/

### For SQLAlchemy:
- Official docs: https://docs.sqlalchemy.org/

### For GraphQL/NetworkX:
- NetworkX docs: https://networkx.org/

---

## 🚀 Deployment Checklist

Before going to production:

- [ ] Change SECRET_KEY in config.py
- [ ] Set DATABASE_URL to production database
- [ ] Enable HTTPS/SSL
- [ ] Set secure CORS origins
- [ ] Enable logging to file system
- [ ] Set up database backups
- [ ] Test all endpoints
- [ ] Load test the system
- [ ] Monitor logs and errors
- [ ] Set up alerting

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Install deps | `pip install -r requirements.txt` |
| Seed DB | `python seed_data.py` |
| Run backend | `python main.py` |
| Run tests | `pytest -v` |
| API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| Start frontend | `npm run dev` |
| Reset DB | `rm meditrack.db && python seed_data.py` |
| View logs | `tail -f logs/meditrack.log` |
| Docker start | `docker-compose up -d` |
| Docker stop | `docker-compose down` |

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Backend starts without errors
- [ ] Database created with test data
- [ ] Health check returns 200 ✓
- [ ] Swagger docs accessible
- [ ] Can login with test credentials
- [ ] Can create hospitals
- [ ] Can create edges
- [ ] Route computation works
- [ ] Reports generate successfully
- [ ] Frontend connects to backend
- [ ] Can select role and login
- [ ] Can build playground
- [ ] Can animate route
- [ ] Tests pass successfully

---

## 🎉 Final Steps

**You now have a complete, production-ready biomedical waste collection optimization system!**

### What You Have:
✅ Full REST API (20+ endpoints)
✅ Dijkstra's algorithm implementation
✅ SQLite database with 12 tables
✅ JWT authentication
✅ Comprehensive error handling
✅ Structured logging
✅ Full test suite
✅ Docker support
✅ Complete documentation

### Get Started:
1. `python seed_data.py`
2. `python main.py`
3. `npm run dev`
4. Visit http://localhost:5173
5. Login with admin/Admin@123
6. Start optimizing waste collection! 🚀

---

**Happy routing! 🎯**
