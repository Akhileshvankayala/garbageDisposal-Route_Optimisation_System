from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class RouteEvent(BaseModel):
    event_type: str  # "move", "pickup", "disposal", "return"
    node_id: int
    amount_kg: Optional[float] = None
    truck_load_after_kg: Optional[float] = None
    timestamp: Optional[datetime] = None


class ComputeRouteRequest(BaseModel):
    truck_id: int
    targets: List[int]
    disposal_threshold: Optional[float] = 0.8
    truck_capacity: Optional[float] = 1000.0
    efficiency_ratio: Optional[float] = 0.5  # Distance-to-waste ratio threshold


class ComputeRouteResponse(BaseModel):
    path: List[int]
    edges: List[Dict]
    total_distance_m: float
    total_waste_collected_kg: float
    disposal_trips: int
    events: List[RouteEvent]
    unreachable_hospitals: List[int]
    skipped_inefficient: Optional[List[int]] = []

    class Config:
        from_attributes = True


# ============================================================================
# ROUTE SCHEMAS
# ============================================================================

class RouteCreate(BaseModel):
    vehicle_id: int
    driver_id: int
    start_location_x: float
    start_location_y: float
    end_location_x: Optional[float] = None
    end_location_y: Optional[float] = None
    route_status: Optional[str] = "planned"


class RouteUpdate(BaseModel):
    route_status: Optional[str] = None
    end_location_x: Optional[float] = None
    end_location_y: Optional[float] = None
    total_distance_m: Optional[float] = None
    total_waste_collected_kg: Optional[float] = None
    num_disposal_trips: Optional[int] = None
    end_time: Optional[datetime] = None


class RouteResponse(BaseModel):
    route_id: int
    vehicle_id: int
    driver_id: int
    start_location_x: float
    start_location_y: float
    end_location_x: Optional[float] = None
    end_location_y: Optional[float] = None
    total_distance_m: float
    total_waste_collected_kg: float
    num_disposal_trips: int
    route_status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ROUTE STOP SCHEMAS
# ============================================================================

class RouteStopCreate(BaseModel):
    hospital_id: int
    stop_sequence: int
    waste_collected_kg: Optional[float] = 0.0
    vehicle_load_at_stop_kg: Optional[float] = 0.0


class RouteStopUpdate(BaseModel):
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    waste_collected_kg: Optional[float] = None
    vehicle_load_at_stop_kg: Optional[float] = None


class RouteStopResponse(BaseModel):
    stop_id: int
    route_id: int
    hospital_id: int
    stop_sequence: int
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    waste_collected_kg: float
    vehicle_load_at_stop_kg: float
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# WASTE COLLECTION SCHEMAS
# ============================================================================

class WasteCollectionCreate(BaseModel):
    bin_id: int
    amount_kg: float
    staff_name: Optional[str] = None
    notes: Optional[str] = None


class WasteCollectionResponse(BaseModel):
    collection_id: int
    stop_id: int
    bin_id: int
    amount_kg: float
    collection_time: datetime
    staff_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
