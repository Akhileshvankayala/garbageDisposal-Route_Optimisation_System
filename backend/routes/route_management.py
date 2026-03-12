from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from database import get_db
from models import Route, RouteStop, WasteCollection, Vehicle, Hospital, WasteBin
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["routes-management"])


# ============================================================================
# ROUTE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/routes", status_code=status.HTTP_201_CREATED)
def create_route(route_data: dict, db: Session = Depends(get_db)):
    """Create a new route."""
    try:
        # Validate vehicle exists
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == route_data.get("vehicle_id")).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        # Create route
        db_route = Route(
            vehicle_id=route_data.get("vehicle_id"),
            driver_id=route_data.get("driver_id"),
            start_location_x=route_data.get("start_location_x", 0.0),
            start_location_y=route_data.get("start_location_y", 0.0),
            end_location_x=route_data.get("end_location_x"),
            end_location_y=route_data.get("end_location_y"),
            route_status=route_data.get("route_status", "planned")
        )
        
        db.add(db_route)
        db.commit()
        db.refresh(db_route)
        
        logger.info(f"Route created: route_id={db_route.route_id}, vehicle={route_data.get('vehicle_id')}, driver={route_data.get('driver_id')}")
        
        return {
            "route_id": db_route.route_id,
            "vehicle_id": db_route.vehicle_id,
            "driver_id": db_route.driver_id,
            "route_status": db_route.route_status,
            "created_at": db_route.created_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routes")
def list_routes(status_filter: str = None, db: Session = Depends(get_db)):
    """List all routes with optional status filter."""
    try:
        query = db.query(Route).order_by(desc(Route.created_at))
        
        if status_filter:
            query = query.filter(Route.route_status == status_filter)
        
        routes = query.all()
        logger.info(f"Retrieved {len(routes)} routes")
        
        return {
            "total": len(routes),
            "routes": [
                {
                    "route_id": r.route_id,
                    "vehicle_id": r.vehicle_id,
                    "driver_id": r.driver_id,
                    "route_status": r.route_status,
                    "start_time": r.start_time.isoformat() if r.start_time else None,
                    "end_time": r.end_time.isoformat() if r.end_time else None,
                    "total_distance_m": r.total_distance_m,
                    "total_waste_collected_kg": r.total_waste_collected_kg,
                    "num_disposal_trips": r.num_disposal_trips,
                    "stops_count": len(r.route_stops)
                }
                for r in routes
            ]
        }
        
    except Exception as e:
        logger.error(f"Error listing routes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routes/{route_id}")
def get_route(route_id: int, db: Session = Depends(get_db)):
    """Get a specific route with all details."""
    try:
        route = db.query(Route).filter(Route.route_id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        logger.info(f"Retrieved route: {route_id}")
        
        return {
            "route_id": route.route_id,
            "vehicle_id": route.vehicle_id,
            "driver_id": route.driver_id,
            "start_location": {"x": route.start_location_x, "y": route.start_location_y},
            "end_location": {"x": route.end_location_x, "y": route.end_location_y},
            "route_status": route.route_status,
            "start_time": route.start_time.isoformat() if route.start_time else None,
            "end_time": route.end_time.isoformat() if route.end_time else None,
            "total_distance_m": route.total_distance_m,
            "total_waste_collected_kg": route.total_waste_collected_kg,
            "num_disposal_trips": route.num_disposal_trips,
            "stops": [
                {
                    "stop_id": s.stop_id,
                    "hospital_id": s.hospital_id,
                    "hospital_name": s.hospital.name if s.hospital else None,
                    "stop_sequence": s.stop_sequence,
                    "arrival_time": s.arrival_time.isoformat() if s.arrival_time else None,
                    "departure_time": s.departure_time.isoformat() if s.departure_time else None,
                    "waste_collected_kg": s.waste_collected_kg,
                    "vehicle_load_at_stop_kg": s.vehicle_load_at_stop_kg
                }
                for s in sorted(route.route_stops, key=lambda x: x.stop_sequence)
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/routes/{route_id}")
def update_route(route_id: int, route_update: dict, db: Session = Depends(get_db)):
    """Update route status and details."""
    try:
        route = db.query(Route).filter(Route.route_id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Update fields
        if "route_status" in route_update:
            route.route_status = route_update["route_status"]
        if "end_location_x" in route_update and route_update["end_location_x"] is not None:
            route.end_location_x = route_update["end_location_x"]
        if "end_location_y" in route_update and route_update["end_location_y"] is not None:
            route.end_location_y = route_update["end_location_y"]
        if "total_distance_m" in route_update and route_update["total_distance_m"] is not None:
            route.total_distance_m = route_update["total_distance_m"]
        if "total_waste_collected_kg" in route_update and route_update["total_waste_collected_kg"] is not None:
            route.total_waste_collected_kg = route_update["total_waste_collected_kg"]
        if "num_disposal_trips" in route_update and route_update["num_disposal_trips"] is not None:
            route.num_disposal_trips = route_update["num_disposal_trips"]
        if "end_time" in route_update and route_update["end_time"]:
            route.end_time = route_update["end_time"]
        
        route.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(route)
        
        logger.info(f"Route updated: {route_id}, status={route.route_status}")
        return {"status": "updated", "route_id": route.route_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/routes/{route_id}/start")
def start_route(route_id: int, db: Session = Depends(get_db)):
    """Start a route (change status to in_progress)."""
    try:
        route = db.query(Route).filter(Route.route_id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        if route.route_status != "planned":
            raise HTTPException(status_code=400, detail="Only planned routes can be started")
        
        route.route_status = "in_progress"
        route.start_time = datetime.utcnow()
        
        # Update vehicle status
        vehicle = route.vehicle
        vehicle.status = "on_route"
        vehicle.current_load_kg = 0.0
        
        db.commit()
        db.refresh(route)
        
        logger.info(f"Route started: {route_id}")
        return {"status": "started", "route_id": route.route_id, "start_time": route.start_time.isoformat()}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error starting route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/routes/{route_id}/complete")
def complete_route(route_id: int, db: Session = Depends(get_db)):
    """Complete a route (change status to completed)."""
    try:
        route = db.query(Route).filter(Route.route_id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        if route.route_status != "in_progress":
            raise HTTPException(status_code=400, detail="Only in-progress routes can be completed")
        
        route.route_status = "completed"
        route.end_time = datetime.utcnow()
        
        # Update vehicle status
        vehicle = route.vehicle
        vehicle.status = "idle"
        vehicle.current_load_kg = 0.0
        
        db.commit()
        db.refresh(route)
        
        logger.info(f"Route completed: {route_id}")
        return {"status": "completed", "route_id": route.route_id, "end_time": route.end_time.isoformat()}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error completing route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROUTE STOPS ENDPOINTS
# ============================================================================

@router.post("/routes/{route_id}/stops", status_code=status.HTTP_201_CREATED)
def create_route_stop(route_id: int, stop_data: dict, db: Session = Depends(get_db)):
    """Add a stop to a route."""
    try:
        # Validate route exists
        route = db.query(Route).filter(Route.route_id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Validate hospital exists
        hospital = db.query(Hospital).filter(Hospital.hospital_id == stop_data.get("hospital_id")).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        # Create route stop
        db_stop = RouteStop(
            route_id=route_id,
            hospital_id=stop_data.get("hospital_id"),
            stop_sequence=stop_data.get("stop_sequence", 0),
            waste_collected_kg=stop_data.get("waste_collected_kg", 0.0),
            vehicle_load_at_stop_kg=stop_data.get("vehicle_load_at_stop_kg", 0.0)
        )
        
        db.add(db_stop)
        db.commit()
        db.refresh(db_stop)
        
        logger.info(f"Route stop created: route={route_id}, hospital={stop_data.get('hospital_id')}, sequence={stop_data.get('stop_sequence')}")
        
        return {
            "stop_id": db_stop.stop_id,
            "route_id": db_stop.route_id,
            "hospital_id": db_stop.hospital_id,
            "stop_sequence": db_stop.stop_sequence,
            "created_at": db_stop.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating route stop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routes/{route_id}/stops")
def list_route_stops(route_id: int, db: Session = Depends(get_db)):
    """Get all stops for a route (in sequence order)."""
    try:
        # Validate route exists
        route = db.query(Route).filter(Route.route_id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        stops = db.query(RouteStop).filter(RouteStop.route_id == route_id).order_by(RouteStop.stop_sequence).all()
        logger.info(f"Retrieved {len(stops)} stops for route {route_id}")
        
        return {
            "total": len(stops),
            "stops": [
                {
                    "stop_id": s.stop_id,
                    "hospital_id": s.hospital_id,
                    "hospital_name": s.hospital.name if s.hospital else None,
                    "stop_sequence": s.stop_sequence,
                    "arrival_time": s.arrival_time.isoformat() if s.arrival_time else None,
                    "departure_time": s.departure_time.isoformat() if s.departure_time else None,
                    "waste_collected_kg": s.waste_collected_kg,
                    "vehicle_load_at_stop_kg": s.vehicle_load_at_stop_kg
                }
                for s in stops
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing route stops: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/stops/{stop_id}")
def update_route_stop(stop_id: int, stop_update: dict, db: Session = Depends(get_db)):
    """Update route stop with arrival/departure times."""
    try:
        stop = db.query(RouteStop).filter(RouteStop.stop_id == stop_id).first()
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found")
        
        # Update fields
        if "arrival_time" in stop_update and stop_update["arrival_time"]:
            stop.arrival_time = datetime.fromisoformat(stop_update["arrival_time"]) if isinstance(stop_update["arrival_time"], str) else stop_update["arrival_time"]
        if "departure_time" in stop_update and stop_update["departure_time"]:
            stop.departure_time = datetime.fromisoformat(stop_update["departure_time"]) if isinstance(stop_update["departure_time"], str) else stop_update["departure_time"]
        if "waste_collected_kg" in stop_update:
            stop.waste_collected_kg = stop_update["waste_collected_kg"]
        if "vehicle_load_at_stop_kg" in stop_update:
            stop.vehicle_load_at_stop_kg = stop_update["vehicle_load_at_stop_kg"]
        
        db.commit()
        db.refresh(stop)
        
        logger.info(f"Route stop updated: {stop_id}")
        return {"status": "updated", "stop_id": stop_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating route stop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WASTE COLLECTION ENDPOINTS
# ============================================================================

@router.post("/stops/{stop_id}/collections", status_code=status.HTTP_201_CREATED)
def create_waste_collection(stop_id: int, collection: dict, db: Session = Depends(get_db)):
    """Record waste collection at a stop."""
    try:
        # Validate stop exists
        stop = db.query(RouteStop).filter(RouteStop.stop_id == stop_id).first()
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found")
        
        # Validate bin exists
        bin_obj = db.query(WasteBin).filter(WasteBin.bin_id == collection.get("bin_id")).first()
        if not bin_obj:
            raise HTTPException(status_code=404, detail="Waste bin not found")
        
        # Create waste collection record
        db_collection = WasteCollection(
            stop_id=stop_id,
            bin_id=collection.get("bin_id"),
            amount_kg=collection.get("amount_kg", 0.0),
            staff_name=collection.get("staff_name", "Unknown"),
            notes=collection.get("notes", "")
        )
        
        # Update bin's current fill
        bin_obj.current_fill_kg -= collection.get("amount_kg", 0.0)
        if bin_obj.current_fill_kg < 0:
            bin_obj.current_fill_kg = 0.0
        bin_obj.last_emptied = datetime.utcnow()
        
        # Update hospital waste
        hospital = bin_obj.hospital
        hospital.current_waste_kg -= collection.get("amount_kg", 0.0)
        if hospital.current_waste_kg < 0:
            hospital.current_waste_kg = 0.0
        
        # Update route stop totals
        stop.waste_collected_kg += collection.get("amount_kg", 0.0)
        
        # Update route totals
        route = stop.route
        route.total_waste_collected_kg += collection.get("amount_kg", 0.0)
        
        db.add(db_collection)
        db.commit()
        db.refresh(db_collection)
        
        logger.info(f"Waste collection recorded: stop={stop_id}, bin={collection.get('bin_id')}, amount={collection.get('amount_kg')}kg")
        
        return {
            "collection_id": db_collection.collection_id,
            "stop_id": db_collection.stop_id,
            "bin_id": db_collection.bin_id,
            "amount_kg": db_collection.amount_kg,
            "staff_name": db_collection.staff_name,
            "collection_time": db_collection.collection_time.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating waste collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stops/{stop_id}/collections")
def list_waste_collections(stop_id: int, db: Session = Depends(get_db)):
    """Get all waste collections for a stop."""
    try:
        # Validate stop exists
        stop = db.query(RouteStop).filter(RouteStop.stop_id == stop_id).first()
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found")
        
        collections = db.query(WasteCollection).filter(WasteCollection.stop_id == stop_id).all()
        logger.info(f"Retrieved {len(collections)} waste collections for stop {stop_id}")
        
        return {
            "total": len(collections),
            "collections": [
                {
                    "collection_id": c.collection_id,
                    "bin_id": c.bin_id,
                    "amount_kg": c.amount_kg,
                    "staff_name": c.staff_name,
                    "notes": c.notes,
                    "collection_time": c.collection_time.isoformat()
                }
                for c in collections
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing waste collections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
