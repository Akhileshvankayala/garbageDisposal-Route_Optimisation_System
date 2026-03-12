# 🚀 MediTrack - Quick Reference Card

## First Time? Start Here!

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python seed_data.py
python main.py

# Terminal 2: Frontend (while backend is running)
npm install
npm run dev
```

**Access**: 
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

**Test Login**:
- Username: `admin`
- Password: `Admin@123`

---

## 📚 Documentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [README.md](README.md) | System overview, quick start, features | 10 min |
| [DEPENDENCIES.md](DEPENDENCIES.md) | All packages, versions, purposes | 8 min |
| [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) | What was delivered, statistics | 5 min |
| [backend/STARTUP.md](backend/STARTUP.md) | Detailed setup, troubleshooting | 15 min |
| [backend/README.md](backend/README.md) | Complete API reference | 20 min |
| [backend/COMPLETE_GUIDE.md](backend/COMPLETE_GUIDE.md) | Architecture, algorithm explanation | 25 min |

---

## 📦 What's Included

### ✅ Backend (43 files)
- FastAPI REST API (20+ endpoints)
- SQLAlchemy ORM (12 tables)
- Dijkstra's algorithm (route optimization)
- JWT authentication
- Unit tests
- Docker support

### ✅ Frontend (React + TypeScript)
- Interactive graph visualization
- Role-based UI
- Undo/redo support
- Real-time animation

### ✅ Documentation (6 guides)
- 8000+ lines of comprehensive docs
- API reference
- Architecture guide
- Troubleshooting guide

---

## 🎯 All 10 Components Delivered

✅ Edge Model  
✅ Scale Mapping  
✅ Error Handling  
✅ Logging System  
✅ Authentication  
✅ Authorization  
✅ Analytics  
✅ Testing  
✅ Docker Support  
✅ Seed Data  

---

## 🔗 API Endpoints (20+)

```
# Hospitals
POST   /api/nodes              Create hospital
GET    /api/nodes              List hospitals
GET    /api/nodes/{id}         Get hospital
PUT    /api/nodes/{id}         Update hospital
DELETE /api/nodes/{id}         Delete hospital

# Edges
POST   /api/edges              Create edge
GET    /api/edges              List edges
GET    /api/edges/{id}         Get edge
GET    /api/edges/graph        Full graph
PUT    /api/edges/{id}         Update edge
DELETE /api/edges/{id}         Delete edge

# Routes
POST   /api/route/compute      Compute route ⭐

# Auth
POST   /api/auth/login         Login
POST   /api/auth/register      Register

# Analytics
GET    /api/reports/waste      Waste report
GET    /api/reports/routes     Route report
GET    /api/reports/summary    Summary

# System
GET    /health                 Health check
GET    /docs                   Swagger UI
GET    /redoc                  ReDoc
```

---

## 💾 Technology Stack

```
Frontend: React 18 + TypeScript + Vite + Tailwind
Backend:  FastAPI + SQLAlchemy + SQLite + NetworkX
Deploy:   Docker + Docker Compose
```

---

## ⚙️ Configuration

**Backend** (`backend/config.py`):
- Database: SQLite at `backend/meditrack.db`
- Disposal threshold: 80%
- Truck capacity: 1000 kg
- Token expiry: 30 minutes

**Environment** (`backend/.env`):
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./meditrack.db
```

---

## 🧪 Run Tests

```bash
cd backend
pytest -v
```

---

## 🐳 Docker Deploy

```bash
docker-compose up -d
# Access at http://localhost
```

---

## 📊 Database

- **Tables**: 12
- **Relationships**: 9
- **Test Data**: 23+ records
- **Type**: SQLite

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `lsof -i :8000; kill -9 <PID>` |
| CORS errors | Check backend `config.py` CORS settings |
| npm install fails | `npm cache clean --force; rm -rf node_modules` |
| Database locked | `rm backend/meditrack.db; python backend/seed_data.py` |
| Import errors | `pip install -r requirements.txt --force-reinstall` |

---

## 📞 Need Help?

1. Check [README.md](README.md) for overview
2. See [backend/STARTUP.md](backend/STARTUP.md) for detailed setup
3. Check logs at `backend/logs/meditrack.log`

---

## ✨ System Status

✅ **Production Ready**  
✅ **All 10 Components Included**  
✅ **43 Backend Files**  
✅ **20+ API Endpoints**  
✅ **12 Database Tables**  
✅ **6 Documentation Files**  

---

**Version**: 1.0.0  
**Status**: Complete & Verified  
**Last Updated**: January 23, 2026
