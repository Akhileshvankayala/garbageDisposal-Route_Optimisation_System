from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Vehicle, Route, RouteStop, WasteCollection, Hospital
from schemas.route import ComputeRouteRequest, ComputeRouteResponse
from services.routing import RoutingService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/route", tags=["routes"])


@router.post("/compute", response_model=ComputeRouteResponse)
def compute_route(request: ComputeRouteRequest, db: Session = Depends(get_db)):
    """
    Compute an optimized route using Dijkstra's capacity-aware algorithm.

    The algorithm:
    1. Greedily selects nearest unvisited hospital
    2. Routes to disposal if adding hospital waste exceeds capacity
    3. Routes to disposal when load >= disposal_threshold * capacity
    4. Returns to depot at end

    Required: truck_id, targets (list of hospital IDs to visit)
    Optional: disposal_threshold (0-1, default 0.8), truck_capacity (kg, default 1000)
    """
    try:
        # Validate truck exists
        truck = db.query(Vehicle).filter(Vehicle.vehicle_id == request.truck_id).first()
        if not truck:
            logger.warning(f"Truck not found: {request.truck_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Truck {request.truck_id} not found",
            )

        # Validate targets
        if not request.targets or len(request.targets) == 0:
            logger.warning("No target hospitals specified for route computation")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one target hospital must be specified",
            )

        # Get disposal threshold and truck capacity
        disposal_threshold = request.disposal_threshold or 0.8
        truck_capacity = request.truck_capacity or truck.capacity_kg or 1000.0
        efficiency_ratio = getattr(request, 'efficiency_ratio', 0.5)  # Default: 0.5

        # Validate disposal threshold
        if disposal_threshold <= 0 or disposal_threshold > 1:
            logger.warning(f"Invalid disposal threshold: {disposal_threshold}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Disposal threshold must be between 0 and 1",
            )

        logger.info(
            f"Computing route: truck={request.truck_id}, targets={request.targets}, "
            f"threshold={disposal_threshold}, capacity={truck_capacity}kg, efficiency_ratio={efficiency_ratio}"
        )

        # Compute route using Dijkstra's algorithm
        route_result = RoutingService.compute_route(
            db=db,
            start_node_id=1,  # Start from disposal center
            target_hospital_ids=request.targets,
            truck_capacity=truck_capacity,
            disposal_threshold=disposal_threshold,
            disposal_node_id=1,  # Disposal center node ID
            efficiency_ratio=efficiency_ratio,
        )

        logger.info(
            f"Route computed successfully: distance={route_result['total_distance_m']}m, "
            f"waste={route_result['total_waste_collected_kg']}kg, "
            f"disposals={route_result['disposal_trips']}"
        )

        return route_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error computing route: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error computing route: {str(e)}",
        )


@router.post("/save")
def save_route(route_data: dict, db: Session = Depends(get_db)):
    """
    Save a computed route to the database with all details.
    
    This is called after a route is visualized in the Playground.
    Records the complete route with all stops and waste collections.
    """
    try:
        vehicle_id = route_data.get("vehicle_id", 1)
        driver_id = route_data.get("driver_id", 3)
        path = route_data.get("path", [])
        total_distance_m = route_data.get("total_distance_m", 0.0)
        total_waste_collected_kg = route_data.get("total_waste_collected_kg", 0.0)
        disposal_trips = route_data.get("disposal_trips", 0)
        events = route_data.get("events", [])
        
        # Create route record
        db_route = Route(
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            start_location_x=0.0,
            start_location_y=0.0,
            end_location_x=0.0,
            end_location_y=0.0,
            total_distance_m=total_distance_m,
            total_waste_collected_kg=total_waste_collected_kg,
            num_disposal_trips=disposal_trips,
            route_status="completed",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
        )
        
        db.add(db_route)
        db.flush()  # Get the route_id
        
        # Create route stops from path
        stop_sequence = 1
        for i, node_id in enumerate(path):
            if node_id != 1:  # Skip disposal center
                hospital = db.query(Hospital).filter(Hospital.hospital_id == node_id).first()
                if hospital:
                    # Find waste collected at this hospital from events
                    waste_at_stop = 0.0
                    for event in events:
                        if event.get("event_type") == "pickup" and event.get("node_id") == node_id:
                            waste_at_stop = event.get("amount_kg", 0.0)
                            break
                    
                    db_stop = RouteStop(
                        route_id=db_route.route_id,
                        hospital_id=node_id,
                        stop_sequence=stop_sequence,
                        arrival_time=datetime.utcnow(),
                        departure_time=datetime.utcnow(),
                        waste_collected_kg=waste_at_stop,
                        vehicle_load_at_stop_kg=0.0,
                    )
                    db.add(db_stop)
                    db.flush()
                    
                    # Add waste collection record
                    if waste_at_stop > 0:
                        db_collection = WasteCollection(
                            stop_id=db_stop.stop_id,
                            bin_id=1,
                            amount_kg=waste_at_stop,
                            collection_time=datetime.utcnow(),
                            staff_name="Route Automation",
                            notes=f"Automatic collection via route {db_route.route_id}",
                        )
                        db.add(db_collection)
                    
                    stop_sequence += 1
        
        db.commit()
        db.refresh(db_route)
        
        logger.info(
            f"Route saved: route_id={db_route.route_id}, "
            f"waste={total_waste_collected_kg}kg, distance={total_distance_m}m"
        )
        
        return {
            "route_id": db_route.route_id,
            "vehicle_id": vehicle_id,
            "total_waste_collected_kg": total_waste_collected_kg,
            "total_distance_m": total_distance_m,
            "disposal_trips": disposal_trips,
            "stops_created": stop_sequence - 1,
            "message": "Route saved successfully",
        }
        
    except Exception as e:
        logger.error(f"Error saving route: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving route: {str(e)}",
        )


@router.post("/update-waste")
def update_waste(waste_data: dict, db: Session = Depends(get_db)):
    """
    Update hospital waste levels based on collections from a route.
    - Decreases waste for hospitals that were visited (collected_from)
    - Adds waste to disposal centers (identified by name starting with 'D' or 'Disposal')
    - If multiple disposal centers exist, distributes waste to the least full one
    """
    try:
        hospital_updates = waste_data.get("hospitals", {})
        total_waste_collected = 0.0
        hospitals_updated = []
        least_full_disposal = None
        
        # Update each hospital (decrease waste from collection)
        for hospital_id_str, waste_collected_kg in hospital_updates.items():
            hospital_id = int(hospital_id_str)
            hospital = db.query(Hospital).filter(Hospital.hospital_id == hospital_id).first()
            
            if hospital:
                # Decrease waste by amount collected (but don't go below 0)
                old_waste = hospital.current_waste_kg
                new_waste = max(0, hospital.current_waste_kg - waste_collected_kg)
                hospital.current_waste_kg = new_waste
                hospital.updated_at = datetime.utcnow()
                total_waste_collected += waste_collected_kg
                hospitals_updated.append(hospital_id)
                
                logger.info(
                    f"Hospital {hospital_id}: waste DECREASED from {old_waste}kg to {new_waste}kg "
                    f"(collected: {waste_collected_kg}kg)"
                )
        
        # Find disposal centers (hospitals with names starting with 'D' or containing 'Disposal')
        disposal_hospitals = db.query(Hospital).filter(
            (Hospital.name.like('D%')) | (Hospital.name.like('%Disposal%'))
        ).all()
        
        logger.info(f"Found {len(disposal_hospitals)} disposal centers: {[h.name for h in disposal_hospitals]}")
        
        # Add collected waste to the least full disposal center
        if total_waste_collected > 0 and disposal_hospitals:
            # Find the disposal center with lowest fill percentage
            least_full_disposal = min(
                disposal_hospitals,
                key=lambda h: (h.current_waste_kg / h.max_bin_capacity) if h.max_bin_capacity > 0 else 0
            )
            
            old_disposal_waste = least_full_disposal.current_waste_kg
            least_full_disposal.current_waste_kg += total_waste_collected
            least_full_disposal.updated_at = datetime.utcnow()
            
            logger.info(
                f"Disposal center '{least_full_disposal.name}' (ID: {least_full_disposal.hospital_id}): "
                f"waste INCREASED from {old_disposal_waste}kg to {least_full_disposal.current_waste_kg}kg "
                f"(received: {total_waste_collected}kg)"
            )
        elif total_waste_collected > 0 and not disposal_hospitals:
            logger.warning(f"No disposal centers found! Collected {total_waste_collected}kg cannot be deposited.")
        
        db.commit()
        
        return {
            "message": "Waste levels updated successfully",
            "hospitals_updated": len(hospitals_updated),
            "hospital_ids": hospitals_updated,
            "total_waste_collected_kg": round(total_waste_collected, 2),
            "disposal_center_updated": total_waste_collected > 0 and len(disposal_hospitals) > 0,
            "disposal_center_name": least_full_disposal.name if least_full_disposal else None,
        }
        
    except Exception as e:
        logger.error(f"Error updating waste: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating waste: {str(e)}",
        )

