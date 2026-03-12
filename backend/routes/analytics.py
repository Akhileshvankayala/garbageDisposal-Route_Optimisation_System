from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Hospital, Route, Vehicle, RouteStatus, VehicleStatus, RouteStop, WasteCollection, Edge
from schemas.analytics import WasteReport, SummaryReport
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["analytics"])


@router.get("/waste")
def get_waste_report(db: Session = Depends(get_db)):
    """Get waste collection summary for all hospitals including disposal center."""
    try:
        # Get all hospitals (including disposal center)
        hospitals = db.query(Hospital).all()

        waste_reports = []
        for hospital in hospitals:
            fill_percentage = 0.0
            if hospital.max_bin_capacity > 0:
                fill_percentage = (hospital.current_waste_kg / hospital.max_bin_capacity) * 100

            waste_reports.append(
                {
                    "hospital_id": hospital.hospital_id,
                    "hospital_name": hospital.name,
                    "current_waste_kg": round(hospital.current_waste_kg, 2),
                    "max_capacity": hospital.max_bin_capacity,
                    "fill_percentage": round(fill_percentage, 2),
                    "last_updated": hospital.updated_at.isoformat(),
                }
            )

        logger.info(f"Generated waste report for {len(waste_reports)} hospitals")
        total_waste = sum(h["current_waste_kg"] for h in waste_reports)
        
        return {
            "report_type": "waste_collection",
            "generated_at": datetime.utcnow().isoformat(),
            "hospitals": waste_reports,
            "total_waste_kg": round(total_waste, 2),
            "average_fill_percentage": (
                sum(h["fill_percentage"] for h in waste_reports) / len(waste_reports)
                if waste_reports
                else 0
            ),
        }

    except Exception as e:
        logger.error(f"Error generating waste report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating waste report",
        )


@router.get("/routes")
def get_routes_report(days: int = 1, db: Session = Depends(get_db)):
    """Get route summary for past N days."""
    try:
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        routes = db.query(Route).filter(Route.start_time >= cutoff_time).all()

        route_details = []
        for route in routes:
            route_details.append(
                {
                    "route_id": route.route_id,
                    "vehicle_id": route.vehicle_id,
                    "driver_id": route.driver_id,
                    "start_time": route.start_time.isoformat(),
                    "end_time": route.end_time.isoformat() if route.end_time else None,
                    "total_distance_m": route.total_distance_m,
                    "total_waste_collected_kg": route.total_waste_collected_kg,
                    "disposal_trips": route.num_disposal_trips,
                    "hospitals_visited": len(route.route_stops),
                    "route_status": route.route_status.value,
                }
            )

        logger.info(f"Generated routes report: {len(routes)} routes in past {days} days")

        return {
            "report_type": "routes_summary",
            "generated_at": datetime.utcnow().isoformat(),
            "period_days": days,
            "routes": route_details,
            "total_routes": len(routes),
            "completed_routes": len([r for r in routes if r.route_status == RouteStatus.COMPLETED]),
            "total_distance_m": sum(r.total_distance_m for r in routes),
            "total_waste_collected_kg": sum(r.total_waste_collected_kg for r in routes),
            "average_waste_per_route_kg": (
                sum(r.total_waste_collected_kg for r in routes) / len(routes)
                if routes
                else 0
            ),
        }

    except Exception as e:
        logger.error(f"Error generating routes report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating routes report",
        )


@router.get("/summary")
def get_summary_report(db: Session = Depends(get_db)):
    """Get comprehensive system summary."""
    try:
        # Hospitals - count ALL hospitals including disposal center
        total_hospitals = db.query(Hospital).count()
        active_hospitals = db.query(Hospital).filter(Hospital.is_active == True).count()
        # Sum ALL waste including disposal center
        total_waste = db.query(func.sum(Hospital.current_waste_kg)).scalar() or 0.0

        # Vehicles
        total_vehicles = db.query(Vehicle).count()
        on_route_vehicles = (
            db.query(Vehicle).filter(Vehicle.status == VehicleStatus.ON_ROUTE).count()
        )
        idle_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.IDLE).count()

        # Routes (today)
        today = datetime.utcnow().date()
        completed_routes = (
            db.query(Route)
            .filter(
                (Route.start_time >= today)
                & (Route.route_status == RouteStatus.COMPLETED)
            )
            .count()
        )
        pending_routes = (
            db.query(Route)
            .filter(
                (Route.start_time >= today)
                & (Route.route_status.in_([RouteStatus.PLANNED, RouteStatus.IN_PROGRESS]))
            )
            .count()
        )
        total_distance_today = (
            db.query(func.sum(Route.total_distance_m))
            .filter(Route.start_time >= today)
            .scalar()
            or 0.0
        )

        # Average fill percentage - calculate for ALL hospitals
        all_hospitals = db.query(Hospital).all()
        fill_percentages = [
            (h.current_waste_kg / h.max_bin_capacity * 100) if h.max_bin_capacity > 0 else 0
            for h in all_hospitals
        ]
        avg_fill = sum(fill_percentages) / len(fill_percentages) if fill_percentages else 0

        logger.info("Generated system summary report")

        return {
            "report_type": "system_summary",
            "generated_at": datetime.utcnow().isoformat(),
            "hospitals": {
                "total": total_hospitals,
                "active": active_hospitals,
                "total_waste_kg": round(total_waste, 2),
                "average_fill_percentage": round(avg_fill, 2),
            },
            "vehicles": {
                "total": total_vehicles,
                "on_route": on_route_vehicles,
                "idle": idle_vehicles,
            },
            "routes_today": {
                "completed": completed_routes,
                "pending": pending_routes,
                "total_distance_m": round(total_distance_today, 2),
            },
        }

    except Exception as e:
        logger.error(f"Error generating summary report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating summary report",
        )

@router.post("/reset")
def reset_all_data(db: Session = Depends(get_db)):
    """
    DANGER: Reset/clear all data from the database.
    This removes all hospitals, edges, routes, vehicles, drivers, users, etc.
    Use only for testing and development!
    """
    try:
        logger.warning("RESETTING DATABASE - DELETING ALL DATA")
        
        # Import required models
        from models import Edge, User, Driver, WasteCollection, RouteStop, Route
        
        # Delete all data in correct dependency order (children before parents)
        logger.info("Deleting WasteCollection...")
        db.query(WasteCollection).delete()
        
        logger.info("Deleting RouteStop...")
        db.query(RouteStop).delete()
        
        logger.info("Deleting Route...")
        db.query(Route).delete()
        
        logger.info("Deleting Edge...")
        db.query(Edge).delete()
        
        logger.info("Deleting Driver...")
        db.query(Driver).delete()
        
        logger.info("Deleting User...")
        db.query(User).delete()
        
        logger.info("Deleting Vehicle...")
        db.query(Vehicle).delete()
        
        logger.info("Deleting Hospital...")
        db.query(Hospital).delete()
        
        db.commit()
        
        logger.warning("DATABASE RESET COMPLETE - All data cleared")
        
        # Recreate default vehicles and drivers
        logger.info("Recreating default vehicles and drivers...")
        import hashlib
        
        # Create default hospital as disposal center (ID=1)
        disposal_center = Hospital(
            hospital_id=1,
            name="Disposal Center",
            location_x=0.0,
            location_y=0.0,
            current_waste_kg=0.0,
            max_bin_capacity=10000.0,
            is_active=True
        )
        db.add(disposal_center)
        logger.info("Created disposal center")
        
        # Create default vehicle
        default_vehicle = Vehicle(
            vehicle_id=1,
            vehicle_name="Waste Collection Truck 01",
            registration_number="MED-001",
            capacity_kg=1000.0,
            status="idle",
            current_location_x=0.0,
            current_location_y=0.0
        )
        db.add(default_vehicle)
        logger.info("Created default vehicle (ID: 1, Capacity: 1000kg)")
        
        # Create default driver user
        driver_user = User(
            user_id=3,
            username="driver_default",
            email="driver@meditrack.local",
            hashed_password=hashlib.sha256(b"default").hexdigest(),
            role="driver",
            is_active=True
        )
        db.add(driver_user)
        db.flush()  # Get user_id
        
        # Create default driver
        driver = Driver(
            driver_id=3,
            user_id=3,
            license_number="DL-001",
            is_active=True
        )
        db.add(driver)
        logger.info("Created default driver (ID: 3)")
        
        db.commit()
        
        logger.info("Database reset complete and reinitialized")
        
        return {
            "status": "success",
            "message": "Database completely reset! All data cleared. Default vehicles, drivers, and disposal center recreated.",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting database: {str(e)}",
        )