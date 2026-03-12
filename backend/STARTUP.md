# 🚀 MediTrack - Complete Startup Guide

This guide will help you get the MediTrack system up and running in minutes.

## ⚡ Quick Start (5 minutes)

### Windows PowerShell

```powershell
# 1. Navigate to backend directory
cd "c:\Users\HP\Desktop\currently working projects\error_there\ip-2\backend"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create and seed the database
python seed_data.py

# 4. Start the backend server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 📖 In another terminal - Start frontend

```powershell
# Navigate to project root
cd "c:\Users\HP\Desktop\currently working projects\error_there\ip-2"

# Install dependencies (if not already done)
npm install

# Start frontend development server
npm run dev
```

**Backend**: http://localhost:8000
**Frontend**: http://localhost:5173

---

## 🔓 Test Login Credentials

After running `seed_data.py`, use these credentials:

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `Admin@123` |
| Staff | `staff` | `Staff@123` |
| Driver | `driver1` | `Driver@123` |

---

## 📋 Full Setup Instructions

### Step 1: Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

**Required packages:**
- fastapi (web framework)
- uvicorn (ASGI server)
- sqlalchemy (ORM)
- pydantic (data validation)
- networkx (graph algorithms)
- python-jose (JWT tokens)
- passlib (password hashing)
- pytest (testing)

### Step 2: Initialize Database

```powershell
python seed_data.py
```

This will:
1. Create all database tables (SQLite)
2. Populate test hospitals (6 hospitals + disposal center)
3. Create edges/connections between hospitals (12 edges)
4. Create test vehicles (3 trucks)
5. Create test users (admin, staff, 2 drivers)

**Database location**: `./meditrack.db` (SQLite file)

### Step 3: Start Backend Server

**Option A: Direct Python execution**
```powershell
python main.py
```

**Option B: Using uvicorn directly**
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Option C: Using Docker**
```powershell
docker-compose up -d
```

### Step 4: Verify Backend is Running

Open in browser: **http://localhost:8000/health**

Expected response:
```json
{
  "status": "healthy",
  "service": "MediTrack API",
  "version": "1.0.0"
}
```

Or access Swagger documentation: **http://localhost:8000/docs**

### Step 5: Start Frontend

```powershell
# In project root directory
npm run dev
```

Visit: **http://localhost:5173**

---

## 🧪 Testing the System

### Test API Endpoints with curl

```powershell
# 1. Health check
curl http://localhost:8000/health

# 2. Get all hospitals
curl http://localhost:8000/api/nodes

# 3. Get all edges
curl http://localhost:8000/api/edges

# 4. Login to get token
$loginResponse = curl -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "username": "admin",
    "password": "Admin@123"
  }'

# Extract token from response
$token = ($loginResponse | ConvertFrom-Json).access_token

# 5. Compute route (with authentication)
curl -X POST http://localhost:8000/api/route/compute `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $token" `
  -d '{
    "truck_id": 1,
    "targets": [2, 3, 4],
    "disposal_threshold": 0.8,
    "truck_capacity": 1000.0
  }'
```

### Run Unit Tests

```powershell
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_routing.py -v

# Run with coverage report
pytest --cov=.
```

---

## 🐳 Using Docker & Docker Compose

### Prerequisites
- Docker Desktop installed
- docker-compose available

### Run Full Stack

```powershell
# From backend directory
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Build Custom Docker Image

```powershell
# Build image
docker build -t meditrack-backend:1.0 .

# Run container
docker run -p 8000:8000 `
  -e DATABASE_URL="sqlite:///./meditrack.db" `
  -e SECRET_KEY="your-secret-key" `
  meditrack-backend:1.0

# Access logs
docker logs <container-id>
```

---

## 📊 Accessing API Documentation

After backend is running, visit:

1. **Swagger UI**: http://localhost:8000/docs
   - Interactive API explorer
   - Try requests directly in browser
   - See responses in real-time

2. **ReDoc**: http://localhost:8000/redoc
   - Alternative API documentation view
   - Better for reading

3. **Raw Specification**: http://localhost:8000/openapi.json
   - OpenAPI 3.0 schema
   - For client code generation

---

## 🔧 Common Commands

### Database Management

```powershell
# Reset database
rm meditrack.db
python seed_data.py

# View database (requires sqlite3 or DB browser)
# Install sqlite3: choco install sqlite
sqlite3 meditrack.db

# List tables
# In sqlite3 prompt:
.tables

# Query hospitals
SELECT * FROM hospitals;

# Exit sqlite
.exit
```

### Development

```powershell
# Install additional dev dependencies
pip install black flake8 mypy

# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

### Troubleshooting

```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process on port 8000
taskkill /PID <PID> /F

# Clear Python cache
Remove-Item -Recurse __pycache__

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version
```

---

## 📁 File Locations

After initialization, you'll have:

```
backend/
├── meditrack.db          # SQLite database (created after seed_data.py)
├── logs/                 # Log files directory
│   └── meditrack.log     # Application logs
├── __pycache__/          # Python cache
└── [all source files]
```

---

## 🎯 Next Steps

### 1. Explore API with Swagger
- Navigate to http://localhost:8000/docs
- Try each endpoint with the examples

### 2. Create Hospitals
```bash
POST /api/nodes
{
  "name": "Your Hospital",
  "location_x": 25.5,
  "location_y": 18.3,
  "current_waste_kg": 300
}
```

### 3. Create Edges
```bash
POST /api/edges
{
  "from_hospital_id": 1,
  "to_hospital_id": 2,
  "distance_m": 150.5
}
```

### 4. Compute Route
```bash
POST /api/route/compute
{
  "truck_id": 1,
  "targets": [2, 3, 4],
  "disposal_threshold": 0.8,
  "truck_capacity": 1000
}
```

### 5. View in Frontend
- Switch to Admin role
- Create nodes in playground
- Connect nodes with edges
- Click "View Optimized Route"
- Watch truck animation!

---

## 🚨 Troubleshooting

### ❌ Port 8000 Already in Use
```powershell
# Find what's using port 8000
netstat -ano | findstr LISTENING | findstr ":8000"

# Kill the process
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

### ❌ Database Locked Error
```
sqlite3.OperationalError: database is locked
```
**Solution**: Close any other connections to the database and try again.

### ❌ Import Errors
```python
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**:
```powershell
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### ❌ Tests Failing
```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests with verbose output
pytest -v --tb=short
```

### ❌ Frontend Can't Reach Backend
**Issue**: CORS error in browser console

**Solution**: Check that:
1. Backend is running on http://localhost:8000
2. Frontend is configured with correct API URL
3. CORS middleware is enabled (it is by default)

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Install deps | `pip install -r requirements.txt` |
| Seed database | `python seed_data.py` |
| Start backend | `python main.py` |
| Start frontend | `npm run dev` |
| Run tests | `pytest -v` |
| View logs | `tail -f logs/meditrack.log` |
| API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| Reset DB | `rm meditrack.db && python seed_data.py` |

---

## 🎓 Understanding the Architecture

```
Frontend (React + TypeScript)
        ↓ (HTTP REST API calls)
Backend (FastAPI)
        ↓ (SQLAlchemy ORM)
Database (SQLite)
```

**Data Flow Example**:
1. User clicks "Compute Route" in frontend
2. Frontend calls `POST /api/route/compute` with hospitals to visit
3. Backend receives request, validates with Pydantic schema
4. RoutingService.compute_route() runs Dijkstra algorithm
5. Results returned as JSON to frontend
6. Frontend animates truck following the path

---

## ✅ Verification Checklist

- [ ] Dependencies installed (`pip list` shows fastapi, uvicorn, etc.)
- [ ] Database created (`ls meditrack.db` shows file)
- [ ] Backend running (http://localhost:8000/health returns 200)
- [ ] Swagger docs accessible (http://localhost:8000/docs)
- [ ] Test data loaded (GET /api/nodes returns hospitals)
- [ ] Login works (/api/auth/login returns token)
- [ ] Frontend starts (http://localhost:5173 loads)
- [ ] Frontend can reach backend (no CORS errors in console)
- [ ] Can create hospitals in playground
- [ ] Can compute routes successfully
- [ ] Route animation plays correctly

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **NetworkX Docs**: https://networkx.org/
- **Dijkstra's Algorithm**: https://en.wikipedia.org/wiki/Dijkstra's_algorithm
- **Docker Docs**: https://docs.docker.com/

---

**Happy coding! 🎉**

If you encounter any issues, check the logs at `logs/meditrack.log` for detailed error messages.
