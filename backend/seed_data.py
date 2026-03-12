"""
Seed database with test data for MediTrack system.

Run with: python -m backend.seed_data
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal, init_db
from models import Hospital, Edge, Vehicle, User, Driver, VehicleStatus, UserRole, Route, RouteStop, WasteCollection, WasteBin
from services.auth import hash_password
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def seed_hospitals(db):
    """Create test hospitals."""
    hospitals = [
        {
            "name": "Disposal Center",
            "location_x": 0.0,
            "location_y": 0.0,
            "current_waste_kg": 0.0,
            "max_bin_capacity": 10000.0,
        },
        {
            "name": "City Hospital",
            "location_x": 10.0,
            "location_y": 15.0,
            "current_waste_kg": 250.0,
            "max_bin_capacity": 500.0,
        },
        {
            "name": "Central Clinic",
            "location_x": 20.0,
            "location_y": 10.0,
            "current_waste_kg": 180.0,
            "max_bin_capacity": 400.0,
        },
        {
            "name": "Emergency Care",
            "location_x": 15.0,
            "location_y": 25.0,
            "current_waste_kg": 320.0,
            "max_bin_capacity": 600.0,
        },
        {
            "name": "Research Institute",
            "location_x": 30.0,
            "location_y": 30.0,
            "current_waste_kg": 150.0,
            "max_bin_capacity": 350.0,
        },
        {
            "name": "Community Health Center",
            "location_x": 5.0,
            "location_y": 35.0,
            "current_waste_kg": 100.0,
            "max_bin_capacity": 300.0,
        },
    ]

    for data in hospitals:
        # Check if hospital already exists
        existing = db.query(Hospital).filter(Hospital.name == data["name"]).first()
        if existing:
            logger.info(f"Hospital already exists: {data['name']}")
            continue

        hospital = Hospital(**data)
        db.add(hospital)
        logger.info(f"Created hospital: {data['name']}")

    db.commit()


def seed_edges(db):
    """Create test edges between hospitals."""
    edges_data = [
        {"from_hospital_id": 1, "to_hospital_id": 2, "distance_m": 100.0},
        {"from_hospital_id": 1, "to_hospital_id": 3, "distance_m": 150.0},
        {"from_hospital_id": 1, "to_hospital_id": 4, "distance_m": 120.0},
        {"from_hospital_id": 2, "to_hospital_id": 3, "distance_m": 80.0},
        {"from_hospital_id": 2, "to_hospital_id": 4, "distance_m": 110.0},
        {"from_hospital_id": 3, "to_hospital_id": 4, "distance_m": 95.0},
        {"from_hospital_id": 3, "to_hospital_id": 5, "distance_m": 140.0},
        {"from_hospital_id": 4, "to_hospital_id": 5, "distance_m": 125.0},
        {"from_hospital_id": 4, "to_hospital_id": 6, "distance_m": 180.0},
        {"from_hospital_id": 5, "to_hospital_id": 6, "distance_m": 200.0},
        {"from_hospital_id": 1, "to_hospital_id": 5, "distance_m": 220.0},
        {"from_hospital_id": 1, "to_hospital_id": 6, "distance_m": 90.0},
    ]

    for data in edges_data:
        # Check if edge already exists
        existing = (
            db.query(Edge)
            .filter(
                (Edge.from_hospital_id == data["from_hospital_id"])
                & (Edge.to_hospital_id == data["to_hospital_id"])
            )
            .first()
        )
        if existing:
            continue

        edge = Edge(**data, is_bidirectional=True)
        db.add(edge)
        logger.info(
            f"Created edge: {data['from_hospital_id']} -> {data['to_hospital_id']}, "
            f"distance={data['distance_m']}m"
        )

    db.commit()


def seed_vehicles(db):
    """Create test vehicles."""
    vehicles_data = [
        {
            "vehicle_name": "Truck-01",
            "registration_number": "MED-001",
            "capacity_kg": 1000.0,
            "status": VehicleStatus.IDLE,
            "current_location_x": 0.0,
            "current_location_y": 0.0,
            "current_load_kg": 0.0,
            "last_maintenance": datetime.utcnow() - timedelta(days=30),
        },
        {
            "vehicle_name": "Truck-02",
            "registration_number": "MED-002",
            "capacity_kg": 1200.0,
            "status": VehicleStatus.IDLE,
            "current_location_x": 10.0,
            "current_location_y": 15.0,
            "current_load_kg": 0.0,
            "last_maintenance": datetime.utcnow() - timedelta(days=45),
        },
        {
            "vehicle_name": "Truck-03",
            "registration_number": "MED-003",
            "capacity_kg": 900.0,
            "status": VehicleStatus.IDLE,
            "current_location_x": 20.0,
            "current_location_y": 10.0,
            "current_load_kg": 0.0,
            "last_maintenance": datetime.utcnow() - timedelta(days=15),
        },
    ]

    for data in vehicles_data:
        # Check if vehicle already exists
        existing = db.query(Vehicle).filter(Vehicle.registration_number == data["registration_number"]).first()
        if existing:
            logger.info(f"Vehicle already exists: {data['vehicle_name']}")
            continue

        vehicle = Vehicle(**data)
        db.add(vehicle)
        logger.info(f"Created vehicle: {data['vehicle_name']} ({data['registration_number']})")

    db.commit()


def seed_users(db):
    """Create test users."""
    users_data = [
        {
            "username": "admin",
            "email": "admin@meditrack.com",
            "password": "Admin@123",
            "role": UserRole.ADMIN,
            "full_name": "Admin User",
        },
        {
            "username": "staff",
            "email": "staff@meditrack.com",
            "password": "Staff@123",
            "role": UserRole.STAFF,
            "full_name": "Staff Member",
        },
        {
            "username": "driver1",
            "email": "driver1@meditrack.com",
            "password": "Driver@123",
            "role": UserRole.DRIVER,
            "full_name": "Driver One",
        },
        {
            "username": "driver2",
            "email": "driver2@meditrack.com",
            "password": "Driver@123",
            "role": UserRole.DRIVER,
            "full_name": "Driver Two",
        },
    ]

    for data in users_data:
        # Check if user already exists
        existing = db.query(User).filter(User.username == data["username"]).first()
        if existing:
            logger.info(f"User already exists: {data['username']}")
            continue

        user = User(
            username=data["username"],
            email=data["email"],
            hashed_password=hash_password(data["password"]),
            role=data["role"],
        )
        db.add(user)

        # Create driver if role is driver
        if data["role"] == UserRole.DRIVER:
            db.flush()
            driver = Driver(
                user_id=user.user_id,
                license_number=f"DRV-{data['username'].upper()}-001",
            )
        db.commit()


def seed_routes_with_data(db):
    """Create test routes with realistic data, stops, and waste collections."""
    try:
        # Get first driver and vehicle
        driver = db.query(User).filter(User.role == UserRole.DRIVER).first()
        vehicle = db.query(Vehicle).first()
        
        if not driver or not vehicle:
            logger.info("Skipping route seeding - no driver or vehicle available")
            return
        
        # Create a sample completed route
        now = datetime.utcnow()
        route_start = now - timedelta(hours=2)
        
        route = Route(
            vehicle_id=vehicle.vehicle_id,
            driver_id=driver.user_id,
            start_location_x=0.0,
            start_location_y=0.0,
            end_location_x=0.0,
            end_location_y=0.0,
            total_distance_m=85.5,
            total_waste_collected_kg=650.0,
            num_disposal_trips=2,
            route_status="completed",
            start_time=route_start,
            end_time=now
        )
        db.add(route)
        db.flush()
        
        logger.info(f"Created sample route {route.route_id}")
        
        # Add stops to the route
        hospitals = db.query(Hospital).filter(Hospital.name != "Disposal Center").limit(3).all()
        
        for idx, hospital in enumerate(hospitals):
            stop_time_start = route_start + timedelta(minutes=(idx + 1) * 20)
            stop_time_end = stop_time_start + timedelta(minutes=15)
            
            route_stop = RouteStop(
                route_id=route.route_id,
                hospital_id=hospital.hospital_id,
                stop_sequence=idx + 1,
                arrival_time=stop_time_start,
                departure_time=stop_time_end,
                waste_collected_kg=150.0 + (idx * 50),
                vehicle_load_at_stop_kg=300.0 + (idx * 100)
            )
            db.add(route_stop)
            db.flush()
            
            # Add waste collections for this stop
            waste_bins = db.query(WasteBin).filter(WasteBin.hospital_id == hospital.hospital_id).limit(2).all()
            
            for bin_idx, waste_bin in enumerate(waste_bins):
                collection = WasteCollection(
                    stop_id=route_stop.stop_id,
                    bin_id=waste_bin.bin_id,
                    amount_kg=80.0 + (bin_idx * 20),
                    collection_time=stop_time_start + timedelta(minutes=5),
                    staff_name=f"Staff-{idx + 1}",
                    notes=f"Regular collection from {hospital.name}"
                )
                db.add(collection)
            
            logger.info(f"Created route stop {idx + 1} at {hospital.name}")
        
        db.commit()
        logger.info("Sample route with stops and collections created successfully")
        
    except Exception as e:
        logger.warning(f"Could not seed routes with data: {str(e)}")
        db.rollback()



    """Run all seed operations."""
    logger.info("=" * 80)
    logger.info("Seeding MediTrack database...")
    logger.info("=" * 80)

    # Initialize database tables
    init_db()

    # Create database session
    db = SessionLocal()

    try:
        logger.info("\n1. Seeding hospitals...")
        seed_hospitals(db)

        logger.info("\n2. Seeding edges...")
        seed_edges(db)

        logger.info("\n3. Seeding vehicles...")
        seed_vehicles(db)

        logger.info("\n4. Seeding users...")
        seed_users(db)
        
        logger.info("\n5. Seeding routes with sample data...")
        seed_routes_with_data(db)

        logger.info("\n" + "=" * 80)
        logger.info("✓ Database seeded successfully!")
        logger.info("=" * 80)
        logger.info("\nTest credentials:")
        logger.info("  Admin:  admin / Admin@123")
        logger.info("  Staff:  staff / Staff@123")
        logger.info("  Driver: driver1 / Driver@123")
        logger.info("=" * 80)

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {str(e)}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
