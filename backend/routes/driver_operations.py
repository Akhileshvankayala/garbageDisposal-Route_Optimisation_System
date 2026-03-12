from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Driver, Route, RouteStop, WasteCollection
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/drivers", tags=["driver-operations"])


@router.get("/{driver_id}/assigned-routes")
def get_assigned_routes(driver_id: int, db: Session = Depends(get_db)):
    """Get all routes assigned to a driver."""
    try:
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        routes = db.query(Route).filter(Route.driver_id == driver_id).all()
        
        logger.info(f"Retrieved {len(routes)} routes for driver {driver_id}")
        
        return {
            "driver_id": driver_id,
            "driver_name": driver.user.username if driver.user else "Unknown",
            "total_routes": len(routes),
            "routes": [
                {
                    "route_id": r.route_id,
                    "vehicle_id": r.vehicle_id,
                    "status": r.route_status,
                    "hospitals_count": len(r.route_stops),
                    "total_waste_kg": r.total_waste_collected_kg,
                    "total_distance_m": r.total_distance_m,
                    "start_time": r.start_time.isoformat() if r.start_time else None,
                    "end_time": r.end_time.isoformat() if r.end_time else None
                }
                for r in routes
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting driver routes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{driver_id}/current-route")
def get_current_route(driver_id: int, db: Session = Depends(get_db)):
    """Get the current in-progress route for a driver."""
    try:
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        current_route = db.query(Route).filter(
            Route.driver_id == driver_id,
            Route.route_status == "in_progress"
        ).first()
        
        if not current_route:
            return {"message": "No active route"}
        
        logger.info(f"Retrieved current route {current_route.route_id} for driver {driver_id}")
        
        return {
            "route_id": current_route.route_id,
            "vehicle_id": current_route.vehicle_id,
            "status": current_route.route_status,
            "start_time": current_route.start_time.isoformat() if current_route.start_time else None,
            "total_distance_m": current_route.total_distance_m,
            "total_waste_collected_kg": current_route.total_waste_collected_kg,
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
                for s in sorted(current_route.route_stops, key=lambda x: x.stop_sequence)
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/routes/{route_id}/stops/{stop_id}/confirm-arrival")
def confirm_arrival(route_id: int, stop_id: int, db: Session = Depends(get_db)):
    """Confirm driver arrival at a hospital stop."""
    try:
        stop = db.query(RouteStop).filter(
            RouteStop.stop_id == stop_id,
            RouteStop.route_id == route_id
        ).first()
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found")
        
        stop.arrival_time = datetime.utcnow()
        
        db.commit()
        db.refresh(stop)
        
        logger.info(f"Driver arrival confirmed: route={route_id}, stop={stop_id}")
        
        return {
            "status": "confirmed",
            "stop_id": stop_id,
            "arrival_time": stop.arrival_time.isoformat(),
            "hospital_id": stop.hospital_id,
            "hospital_name": stop.hospital.name if stop.hospital else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error confirming arrival: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/routes/{route_id}/stops/{stop_id}/confirm-departure")
def confirm_departure(route_id: int, stop_id: int, db: Session = Depends(get_db)):
    """Confirm driver departure from a hospital stop."""
    try:
        stop = db.query(RouteStop).filter(
            RouteStop.stop_id == stop_id,
            RouteStop.route_id == route_id
        ).first()
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found")
        
        stop.departure_time = datetime.utcnow()
        
        db.commit()
        db.refresh(stop)
        
        logger.info(f"Driver departure confirmed: route={route_id}, stop={stop_id}")
        
        return {
            "status": "confirmed",
            "stop_id": stop_id,
            "departure_time": stop.departure_time.isoformat(),
            "hospital_id": stop.hospital_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error confirming departure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/routes/{route_id}/stops/{stop_id}/record-collection")
def record_collection(route_id: int, stop_id: int, collection_data: dict, db: Session = Depends(get_db)):
    """Record waste collection at a stop with staff details."""
    try:
        stop = db.query(RouteStop).filter(
            RouteStop.stop_id == stop_id,
            RouteStop.route_id == route_id
        ).first()
        if not stop:
            raise HTTPException(status_code=404, detail="Stop not found")
        
        # Record waste collection
        waste_collection = WasteCollection(
            stop_id=stop_id,
            bin_id=collection_data.get("bin_id"),
            amount_kg=collection_data.get("amount_kg", 0.0),
            staff_name=collection_data.get("staff_name", "Unknown"),
            notes=collection_data.get("notes", "")
        )
        
        db.add(waste_collection)
        db.commit()
        
        logger.info(f"Collection recorded: route={route_id}, stop={stop_id}, amount={collection_data.get('amount_kg')}kg")
        
        return {
            "status": "recorded",
            "collection_id": waste_collection.collection_id,
            "amount_kg": waste_collection.amount_kg,
            "staff_name": waste_collection.staff_name,
            "collection_time": waste_collection.collection_time.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error recording collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routes/{route_id}/summary")
def get_route_summary(route_id: int, db: Session = Depends(get_db)):
    """Get summary of a specific route."""
    try:
        route = db.query(Route).filter(Route.route_id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        stops_with_times = []
        total_time = None
        
        if route.start_time and route.end_time:
            total_time = (route.end_time - route.start_time).total_seconds() / 60  # minutes
        
        for stop in sorted(route.route_stops, key=lambda x: x.stop_sequence):
            stop_time = None
            if stop.arrival_time and stop.departure_time:
                stop_time = (stop.departure_time - stop.arrival_time).total_seconds() / 60  # minutes
            
            stops_with_times.append({
                "stop_id": stop.stop_id,
                "hospital_id": stop.hospital_id,
                "hospital_name": stop.hospital.name if stop.hospital else None,
                "sequence": stop.stop_sequence,
                "arrival_time": stop.arrival_time.isoformat() if stop.arrival_time else None,
                "departure_time": stop.departure_time.isoformat() if stop.departure_time else None,
                "duration_minutes": stop_time,
                "waste_collected_kg": stop.waste_collected_kg,
                "vehicle_load_at_stop_kg": stop.vehicle_load_at_stop_kg,
                "collections": len(stop.waste_collections)
            })
        
        logger.info(f"Retrieved route summary for route {route_id}")
        
        return {
            "route_id": route.route_id,
            "vehicle_id": route.vehicle_id,
            "driver_id": route.driver_id,
            "status": route.route_status,
            "start_time": route.start_time.isoformat() if route.start_time else None,
            "end_time": route.end_time.isoformat() if route.end_time else None,
            "total_duration_minutes": total_time,
            "total_distance_m": route.total_distance_m,
            "total_waste_collected_kg": route.total_waste_collected_kg,
            "disposal_trips": route.num_disposal_trips,
            "stops": stops_with_times,
            "total_stops": len(stops_with_times)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting route summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
