from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from . import Base


class RouteStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Route(Base):
    __tablename__ = "routes"

    route_id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id", ondelete="CASCADE"), nullable=False, index=True)
    start_location_x = Column(Float, nullable=False)
    start_location_y = Column(Float, nullable=False)
    end_location_x = Column(Float)
    end_location_y = Column(Float)
    total_distance_m = Column(Float, default=0.0)
    total_waste_collected_kg = Column(Float, default=0.0)
    num_disposal_trips = Column(Integer, default=0)
    route_status = Column(Enum(RouteStatus), default=RouteStatus.PLANNED, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="routes")
    driver = relationship("Driver", back_populates="routes")
    route_stops = relationship("RouteStop", back_populates="route", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Route(route_id={self.route_id}, status={self.route_status}, distance={self.total_distance_m}m)>"


class RouteStop(Base):
    __tablename__ = "route_stops"

    stop_id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.route_id", ondelete="CASCADE"), nullable=False, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id", ondelete="CASCADE"), nullable=False, index=True)
    stop_sequence = Column(Integer, nullable=False)
    arrival_time = Column(DateTime)
    departure_time = Column(DateTime)
    waste_collected_kg = Column(Float, default=0.0)
    vehicle_load_at_stop_kg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    route = relationship("Route", back_populates="route_stops")
    hospital = relationship("Hospital", back_populates="route_stops")
    waste_collections = relationship("WasteCollection", back_populates="route_stop", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RouteStop(stop_id={self.stop_id}, hospital_id={self.hospital_id}, sequence={self.stop_sequence})>"


class WasteCollection(Base):
    __tablename__ = "waste_collections"

    collection_id = Column(Integer, primary_key=True, index=True)
    stop_id = Column(Integer, ForeignKey("route_stops.stop_id", ondelete="CASCADE"), nullable=False, index=True)
    bin_id = Column(Integer, ForeignKey("waste_bins.bin_id", ondelete="CASCADE"), nullable=False, index=True)
    amount_kg = Column(Float, nullable=False)
    collection_time = Column(DateTime, default=datetime.utcnow)
    staff_name = Column(String(255))
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    route_stop = relationship("RouteStop", back_populates="waste_collections")
    bin = relationship("WasteBin", back_populates="waste_collections")

    def __repr__(self):
        return f"<WasteCollection(collection_id={self.collection_id}, amount_kg={self.amount_kg})>"


class PickupRecord(Base):
    __tablename__ = "pickup_records"

    pickup_id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id", ondelete="CASCADE"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False, index=True)
    amount_kg = Column(Float, nullable=False)
    pickup_time = Column(DateTime, default=datetime.utcnow)
    driver_name = Column(String(255))
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hospital = relationship("Hospital", back_populates="pickup_records")
    vehicle = relationship("Vehicle", back_populates="pickup_records")

    def __repr__(self):
        return f"<PickupRecord(pickup_id={self.pickup_id}, amount_kg={self.amount_kg})>"
