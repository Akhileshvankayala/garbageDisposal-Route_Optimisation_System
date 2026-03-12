from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from schemas.auth import UserLogin, UserRegister, TokenResponse
from services.auth import authenticate_user, create_user, create_access_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """User login endpoint. Returns JWT token."""
    try:
        user = authenticate_user(db, credentials.username, credentials.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.user_id, "role": user.role.value}
        )

        logger.info(f"User logged in: {user.username} ({user.role.value})")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login error",
        )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """User registration endpoint."""
    try:
        # Validate role
        valid_roles = ["admin", "staff", "driver"]
        if user_data.role not in valid_roles:
            logger.warning(f"Invalid role in registration: {user_data.role}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
            )

        # Create user
        new_user = create_user(
            db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
        )

        if not new_user:
            logger.warning(f"User creation failed: username={user_data.username}, email={user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": new_user.username, "user_id": new_user.user_id, "role": new_user.role.value}
        )

        logger.info(f"New user registered: {new_user.username} ({new_user.role.value})")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": new_user.user_id,
            "username": new_user.username,
            "role": new_user.role.value,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration error",
        )
