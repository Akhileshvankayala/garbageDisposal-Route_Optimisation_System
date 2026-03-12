from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NodeCreate(BaseModel):
    name: str
    location_x: float
    location_y: float
    current_waste_kg: Optional[float] = 0.0
    max_bin_capacity: Optional[float] = 500.0
    contact_number: Optional[str] = None
    contact_email: Optional[str] = None


class NodeUpdate(BaseModel):
    name: Optional[str] = None
    current_waste_kg: Optional[float] = None
    max_bin_capacity: Optional[float] = None
    contact_number: Optional[str] = None
    contact_email: Optional[str] = None


class NodeResponse(BaseModel):
    hospital_id: int
    name: str
    location_x: float
    location_y: float
    current_waste_kg: float
    max_bin_capacity: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WasteBinResponse(BaseModel):
    bin_id: int
    hospital_id: int
    bin_type: str
    capacity_kg: float
    current_fill_kg: float
    last_emptied: datetime

    class Config:
        from_attributes = True
