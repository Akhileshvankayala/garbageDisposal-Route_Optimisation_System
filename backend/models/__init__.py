from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .user import User, Admin, Driver, UserRole
from .hospital import Hospital, WasteBin, BinType
from .vehicle import Vehicle, VehicleStatus
from .route import Route, RouteStop, WasteCollection, PickupRecord, RouteStatus
from .edge import Edge
from .scale import ScaleMapping

__all__ = [
    "Base",
    "User",
    "Admin",
    "Driver",
    "UserRole",
    "Hospital",
    "WasteBin",
    "BinType",
    "Vehicle",
    "VehicleStatus",
    "Route",
    "RouteStop",
    "WasteCollection",
    "PickupRecord",
    "RouteStatus",
    "Edge",
    "ScaleMapping",
]
