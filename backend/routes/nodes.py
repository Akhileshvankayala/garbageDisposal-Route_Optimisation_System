from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Hospital
from schemas.node import NodeCreate, NodeUpdate, NodeResponse, WasteBinResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    """Create a new hospital node."""
    try:
        # Check if hospital with same name already exists
        existing = db.query(Hospital).filter(Hospital.name == node.name).first()
        if existing:
            logger.warning(f"Hospital creation failed: {node.name} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hospital with name '{node.name}' already exists",
            )

        db_hospital = Hospital(
            name=node.name,
            location_x=node.location_x,
            location_y=node.location_y,
            current_waste_kg=node.current_waste_kg or 0.0,
            max_bin_capacity=node.max_bin_capacity or 500.0,
            contact_number=node.contact_number,
            contact_email=node.contact_email,
        )

        db.add(db_hospital)
        db.commit()
        db.refresh(db_hospital)

        logger.info(f"Hospital created: {db_hospital.hospital_id} - {node.name}")
        return db_hospital

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating hospital: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating hospital",
        )


@router.get("", response_model=List[NodeResponse])
def get_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all active hospital nodes."""
    try:
        hospitals = (
            db.query(Hospital)
            .filter(Hospital.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.info(f"Retrieved {len(hospitals)} active hospitals")
        return hospitals
    except Exception as e:
        logger.error(f"Error retrieving hospitals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving hospitals",
        )


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(node_id: int, db: Session = Depends(get_db)):
    """Get a specific hospital node by ID."""
    try:
        hospital = db.query(Hospital).filter(Hospital.hospital_id == node_id).first()
        if not hospital:
            logger.warning(f"Hospital not found: {node_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hospital {node_id} not found",
            )
        return hospital
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving hospital {node_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving hospital",
        )


@router.put("/{node_id}", response_model=NodeResponse)
def update_node(node_id: int, node: NodeUpdate, db: Session = Depends(get_db)):
    """Update a hospital node."""
    try:
        db_hospital = db.query(Hospital).filter(Hospital.hospital_id == node_id).first()
        if not db_hospital:
            logger.warning(f"Hospital not found for update: {node_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hospital {node_id} not found",
            )

        # Update fields
        if node.name is not None:
            db_hospital.name = node.name
        if node.current_waste_kg is not None:
            db_hospital.current_waste_kg = node.current_waste_kg
        if node.max_bin_capacity is not None:
            db_hospital.max_bin_capacity = node.max_bin_capacity
        if node.contact_number is not None:
            db_hospital.contact_number = node.contact_number
        if node.contact_email is not None:
            db_hospital.contact_email = node.contact_email

        db.commit()
        db.refresh(db_hospital)

        logger.info(f"Hospital updated: {node_id}")
        return db_hospital

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating hospital {node_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating hospital",
        )


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    """Delete a hospital node (soft delete via is_active flag)."""
    try:
        db_hospital = db.query(Hospital).filter(Hospital.hospital_id == node_id).first()
        if not db_hospital:
            logger.warning(f"Hospital not found for deletion: {node_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hospital {node_id} not found",
            )

        db_hospital.is_active = False
        db.commit()

        logger.info(f"Hospital deleted (soft): {node_id}")
        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting hospital {node_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting hospital",
        )
