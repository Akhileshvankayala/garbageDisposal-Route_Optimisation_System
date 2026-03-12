from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Edge, Hospital
from schemas.edge import EdgeCreate, EdgeUpdate, EdgeResponse, GraphResponse
from services.routing import GraphBuilder
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/edges", tags=["edges"])


@router.post("", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
def create_edge(edge: EdgeCreate, db: Session = Depends(get_db)):
    """Create a new edge between two hospitals."""
    try:
        # Validate hospitals exist
        from_hospital = db.query(Hospital).filter(Hospital.hospital_id == edge.from_hospital_id).first()
        to_hospital = db.query(Hospital).filter(Hospital.hospital_id == edge.to_hospital_id).first()

        if not from_hospital:
            logger.warning(f"Source hospital not found: {edge.from_hospital_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source hospital {edge.from_hospital_id} not found",
            )

        if not to_hospital:
            logger.warning(f"Target hospital not found: {edge.to_hospital_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target hospital {edge.to_hospital_id} not found",
            )

        # Check if edge already exists
        existing = (
            db.query(Edge)
            .filter(
                (Edge.from_hospital_id == edge.from_hospital_id)
                & (Edge.to_hospital_id == edge.to_hospital_id)
            )
            .first()
        )
        if existing:
            logger.warning(
                f"Edge already exists: {edge.from_hospital_id} -> {edge.to_hospital_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Edge between these hospitals already exists",
            )

        db_edge = Edge(
            from_hospital_id=edge.from_hospital_id,
            to_hospital_id=edge.to_hospital_id,
            distance_m=edge.distance_m,
            is_bidirectional=edge.is_bidirectional,
        )

        db.add(db_edge)
        db.commit()
        db.refresh(db_edge)

        logger.info(
            f"Edge created: {edge.from_hospital_id} -> {edge.to_hospital_id}, distance={edge.distance_m}m"
        )
        return db_edge

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating edge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating edge",
        )


@router.get("", response_model=List[EdgeResponse])
def get_edges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all edges."""
    try:
        edges = db.query(Edge).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(edges)} edges")
        return edges
    except Exception as e:
        logger.error(f"Error retrieving edges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving edges",
        )


@router.get("/graph", response_model=GraphResponse)
def get_graph(db: Session = Depends(get_db)):
    """Get complete graph with all nodes and edges for visualization."""
    try:
        # Get all active hospitals
        hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
        nodes = [
            {
                "hospital_id": h.hospital_id,
                "name": h.name,
                "x": h.location_x,
                "y": h.location_y,
                "waste": h.current_waste_kg,
            }
            for h in hospitals
        ]

        # Get all edges
        edges = db.query(Edge).all()

        logger.info(f"Retrieved graph: {len(nodes)} nodes, {len(edges)} edges")
        return {"nodes": nodes, "edges": edges}

    except Exception as e:
        logger.error(f"Error retrieving graph: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving graph",
        )


@router.get("/{edge_id}", response_model=EdgeResponse)
def get_edge(edge_id: int, db: Session = Depends(get_db)):
    """Get a specific edge by ID."""
    try:
        edge = db.query(Edge).filter(Edge.edge_id == edge_id).first()
        if not edge:
            logger.warning(f"Edge not found: {edge_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edge {edge_id} not found",
            )
        return edge
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving edge {edge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving edge",
        )


@router.put("/{edge_id}", response_model=EdgeResponse)
def update_edge(edge_id: int, edge: EdgeUpdate, db: Session = Depends(get_db)):
    """Update an edge."""
    try:
        db_edge = db.query(Edge).filter(Edge.edge_id == edge_id).first()
        if not db_edge:
            logger.warning(f"Edge not found for update: {edge_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edge {edge_id} not found",
            )

        if edge.distance_m is not None:
            db_edge.distance_m = edge.distance_m
        if edge.is_bidirectional is not None:
            db_edge.is_bidirectional = edge.is_bidirectional

        db.commit()
        db.refresh(db_edge)

        logger.info(f"Edge updated: {edge_id}")
        return db_edge

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating edge {edge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating edge",
        )


@router.delete("/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_edge(edge_id: int, db: Session = Depends(get_db)):
    """Delete an edge."""
    try:
        db_edge = db.query(Edge).filter(Edge.edge_id == edge_id).first()
        if not db_edge:
            logger.warning(f"Edge not found for deletion: {edge_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edge {edge_id} not found",
            )

        db.delete(db_edge)
        db.commit()

        logger.info(f"Edge deleted: {edge_id}")
        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting edge {edge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting edge",
        )
