from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from models import Base, Vehicle, Driver, User
import hashlib

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and create default vehicles/drivers."""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")
    
    # Create default vehicles and drivers for route computation
    db = SessionLocal()
    try:
        # Check if vehicles already exist
        existing_vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == 1).first()
        if not existing_vehicle:
            # Create default vehicle
            vehicle = Vehicle(
                vehicle_id=1,
                vehicle_name="Waste Collection Truck 01",
                registration_number="MED-001",
                capacity_kg=1000.0,
                status="idle"
            )
            db.add(vehicle)
            print("✓ Created default vehicle (ID: 1, Capacity: 1000kg)")
        
        # Check if driver exists  
        existing_driver = db.query(Driver).filter(Driver.driver_id == 3).first()
        if not existing_driver:
            # Create driver user first
            driver_user = User(
                user_id=3,
                username="driver_default",
                email="driver@meditrack.local",
                hashed_password=hashlib.sha256(b"default").hexdigest(),
                role="driver",
                is_active=True
            )
            db.add(driver_user)
            db.flush()  # Flush to get the user_id
            
            # Create driver linked to user
            driver = Driver(
                driver_id=3,
                user_id=3,
                license_number="DL-001",
                is_active=True
            )
            db.add(driver)
            print("✓ Created default driver (ID: 3)")
        
        db.commit()
        print("✓ Database initialized with default vehicles and drivers")
    except Exception as e:
        db.rollback()
        print(f"⚠ Warning initializing defaults: {str(e)}")
    finally:
        db.close()
