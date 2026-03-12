from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class WasteReport(BaseModel):
    hospital_id: int
    hospital_name: str
    current_waste_kg: float
    max_capacity: float
    fill_percentage: float
    last_updated: datetime


class RouteReportDetail(BaseModel):
    route_id: int
    vehicle_id: int
    driver_id: int
    start_time: datetime
    end_time: Optional[datetime]
    total_distance_m: float
    total_waste_collected_kg: float
    disposal_trips: int
    hospitals_visited: int
    route_status: str


class SummaryReport(BaseModel):
    total_hospitals: int
    active_hospitals: int
    total_waste_kg: float
    average_fill_percentage: float
    vehicles_on_route: int
    idle_vehicles: int
    completed_routes_today: int
    pending_routes: int
    total_distance_today_m: float


class AnalyticsResponse(BaseModel):
    report_type: str
    generated_at: datetime
    data: dict

    class Config:
        from_attributes = True
