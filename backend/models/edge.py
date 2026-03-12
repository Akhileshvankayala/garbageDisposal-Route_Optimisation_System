from sqlalchemy import Column, Integer, Float, DateTime, Boolean, UniqueConstraint, ForeignKey
from datetime import datetime
from . import Base


class Edge(Base):
    __tablename__ = "edges"

    edge_id = Column(Integer, primary_key=True, index=True)
    from_hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id", ondelete="CASCADE"), nullable=False, index=True)
    to_hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id", ondelete="CASCADE"), nullable=False, index=True)
    distance_m = Column(Float, nullable=False)
    is_bidirectional = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('from_hospital_id', 'to_hospital_id', name='unique_edge'),
    )

    def __repr__(self):
        return f"<Edge(edge_id={self.edge_id}, from={self.from_hospital_id}, to={self.to_hospital_id}, distance={self.distance_m}m)>"
