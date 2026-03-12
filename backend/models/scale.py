from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from . import Base


class ScaleMapping(Base):
    __tablename__ = "scale_mappings"

    mapping_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    scale_factor = Column(Float, nullable=False, default=100.0)  # 1 unit = 100 meters by default
    unit_label = Column(String(50), default="meters")
    pixel_to_meter_ratio = Column(Float, nullable=False, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ScaleMapping(mapping_id={self.mapping_id}, session_id={self.session_id}, factor={self.scale_factor})>"
