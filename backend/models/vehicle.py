from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from . import Base


class VehicleStatus(str, enum.Enum):
    IDLE = "idle"
    ON_ROUTE = "on_route"
    AT_DISPOSAL = "at_disposal"
    MAINTENANCE = "maintenance"


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(Integer, primary_key=True, index=True)
    vehicle_name = Column(String(255), nullable=False, index=True)
    registration_number = Column(String(255), unique=True, nullable=False, index=True)
    capacity_kg = Column(Float, default=1000.0)
    current_load_kg = Column(Float, default=0.0)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.IDLE, index=True)
    current_location_x = Column(Float)
    current_location_y = Column(Float)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id", ondelete="SET NULL"), nullable=True, index=True)
    last_maintenance = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    driver = relationship("Driver", back_populates="vehicles")
    routes = relationship("Route", back_populates="vehicle")
    pickup_records = relationship("PickupRecord", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle(vehicle_id={self.vehicle_id}, vehicle_name={self.vehicle_name}, status={self.status})>"
