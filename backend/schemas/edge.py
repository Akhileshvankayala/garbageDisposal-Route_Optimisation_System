from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EdgeCreate(BaseModel):
    from_hospital_id: int
    to_hospital_id: int
    distance_m: float = Field(gt=0, description="Distance must be positive")
    is_bidirectional: Optional[bool] = True


class EdgeUpdate(BaseModel):
    distance_m: Optional[float] = Field(None, gt=0)
    is_bidirectional: Optional[bool] = None


class EdgeResponse(BaseModel):
    edge_id: int
    from_hospital_id: int
    to_hospital_id: int
    distance_m: float
    is_bidirectional: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GraphResponse(BaseModel):
    nodes: list[dict]
    edges: list[EdgeResponse]

    class Config:
        from_attributes = True
