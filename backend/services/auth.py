from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models import User, UserRole
import logging
import hashlib
import bcrypt

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=4)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return decoded data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user by username and password."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        logger.warning(f"Login failed: User {username} not found")
        return None

    if not verify_password(password, user.hashed_password):
        logger.warning(f"Login failed: Invalid password for user {username}")
        return None

    if not user.is_active:
        logger.warning(f"Login failed: User {username} is inactive")
        return None

    logger.info(f"User {username} authenticated successfully")
    return user


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: str,
    role: str,
) -> Optional[User]:
    """Create a new user in the database."""
    # Check if user already exists
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        logger.warning(f"User creation failed: User {username} or email {email} already exists")
        return None

    # Create new user
    hashed_password = hash_password(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=UserRole(role),
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User {username} created successfully with role {role}")
    return db_user
