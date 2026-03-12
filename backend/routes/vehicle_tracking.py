from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Vehicle, Route
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vehicles", tags=["vehicle-tracking"])


@router.put("/{vehicle_id}/location")
def update_vehicle_location(vehicle_id: int, location: dict, db: Session = Depends(get_db)):
    """Update vehicle's current location (GPS tracking)."""
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        vehicle.current_location_x = location.get("x")
        vehicle.current_location_y = location.get("y")
        vehicle.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(vehicle)
        
        logger.info(f"Vehicle location updated: {vehicle_id} -> ({location.get('x')}, {location.get('y')})")
        
        return {
            "vehicle_id": vehicle_id,
            "location": {
                "x": vehicle.current_location_x,
                "y": vehicle.current_location_y
            },
            "updated_at": vehicle.updated_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating vehicle location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{vehicle_id}/load")
def update_vehicle_load(vehicle_id: int, load_data: dict, db: Session = Depends(get_db)):
    """Update vehicle's current load."""
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        load_kg = load_data.get("load_kg", 0.0)
        
        if load_kg > vehicle.capacity_kg:
            raise HTTPException(status_code=400, detail=f"Load exceeds vehicle capacity ({vehicle.capacity_kg}kg)")
        
        vehicle.current_load_kg = load_kg
        vehicle.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(vehicle)
        
        logger.info(f"Vehicle load updated: {vehicle_id} -> {load_kg}kg")
        
        return {
            "vehicle_id": vehicle_id,
            "current_load_kg": vehicle.current_load_kg,
            "capacity_kg": vehicle.capacity_kg,
            "load_percentage": round((vehicle.current_load_kg / vehicle.capacity_kg) * 100, 2),
            "updated_at": vehicle.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating vehicle load: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{vehicle_id}/status")
def update_vehicle_status(vehicle_id: int, status_data: dict, db: Session = Depends(get_db)):
    """Update vehicle status."""
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        new_status = status_data.get("status")
        valid_statuses = ["idle", "on_route", "at_disposal", "maintenance"]
        
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        vehicle.status = new_status
        vehicle.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(vehicle)
        
        logger.info(f"Vehicle status updated: {vehicle_id} -> {new_status}")
        
        return {
            "vehicle_id": vehicle_id,
            "status": vehicle.status,
            "updated_at": vehicle.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating vehicle status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{vehicle_id}/tracking")
def get_vehicle_tracking(vehicle_id: int, db: Session = Depends(get_db)):
    """Get real-time vehicle tracking data."""
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        # Get current route if any
        current_route = db.query(Route).filter(
            Route.vehicle_id == vehicle_id,
            Route.route_status == "in_progress"
        ).first()
        
        logger.info(f"Retrieved tracking data for vehicle {vehicle_id}")
        
        return {
            "vehicle_id": vehicle.vehicle_id,
            "name": vehicle.vehicle_name,
            "registration": vehicle.registration_number,
            "current_location": {
                "x": vehicle.current_location_x,
                "y": vehicle.current_location_y
            },
            "current_load_kg": vehicle.current_load_kg,
            "capacity_kg": vehicle.capacity_kg,
            "load_percentage": round((vehicle.current_load_kg / vehicle.capacity_kg) * 100, 2) if vehicle.capacity_kg > 0 else 0,
            "status": vehicle.status,
            "current_route_id": current_route.route_id if current_route else None,
            "driver_id": vehicle.driver_id,
            "last_updated": vehicle.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vehicle tracking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def list_all_vehicles(db: Session = Depends(get_db)):
    """Get all vehicles with tracking information."""
    try:
        vehicles = db.query(Vehicle).all()
        
        logger.info(f"Retrieved {len(vehicles)} vehicles")
        
        return {
            "total": len(vehicles),
            "vehicles": [
                {
                    "vehicle_id": v.vehicle_id,
                    "name": v.vehicle_name,
                    "registration": v.registration_number,
                    "status": v.status,
                    "current_load_kg": v.current_load_kg,
                    "capacity_kg": v.capacity_kg,
                    "location": {"x": v.current_location_x, "y": v.current_location_y},
                    "driver_id": v.driver_id
                }
                for v in vehicles
            ]
        }
    except Exception as e:
        logger.error(f"Error listing vehicles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{vehicle_id}/maintenance")
def record_maintenance(vehicle_id: int, maintenance_data: dict, db: Session = Depends(get_db)):
    """Record vehicle maintenance."""
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        vehicle.last_maintenance = datetime.utcnow()
        vehicle.status = "maintenance" if maintenance_data.get("start_maintenance", False) else "idle"
        
        db.commit()
        db.refresh(vehicle)
        
        logger.info(f"Maintenance recorded for vehicle {vehicle_id}")
        
        return {
            "vehicle_id": vehicle_id,
            "last_maintenance": vehicle.last_maintenance.isoformat(),
            "status": vehicle.status
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error recording maintenance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
