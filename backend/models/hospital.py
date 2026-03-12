from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from . import Base


class BinType(str, enum.Enum):
    SHARPS = "sharps"
    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    MIXED = "mixed"


class Hospital(Base):
    __tablename__ = "hospitals"

    hospital_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    location_x = Column(Float, nullable=False)
    location_y = Column(Float, nullable=False)
    current_waste_kg = Column(Float, default=0.0)
    max_bin_capacity = Column(Float, default=500.0)
    contact_number = Column(String(20))
    contact_email = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    waste_bins = relationship("WasteBin", back_populates="hospital", cascade="all, delete-orphan")
    route_stops = relationship("RouteStop", back_populates="hospital")
    pickup_records = relationship("PickupRecord", back_populates="hospital")

    def __repr__(self):
        return f"<Hospital(hospital_id={self.hospital_id}, name={self.name}, waste_kg={self.current_waste_kg})>"


class WasteBin(Base):
    __tablename__ = "waste_bins"

    bin_id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id", ondelete="CASCADE"), nullable=False, index=True)
    bin_type = Column(Enum(BinType), nullable=False)
    capacity_kg = Column(Float, default=100.0)
    current_fill_kg = Column(Float, default=0.0)
    last_emptied = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hospital = relationship("Hospital", back_populates="waste_bins")
    waste_collections = relationship("WasteCollection", back_populates="bin")

    def __repr__(self):
        return f"<WasteBin(bin_id={self.bin_id}, bin_type={self.bin_type}, current_fill_kg={self.current_fill_kg})>"
