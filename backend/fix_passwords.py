from database import SessionLocal
from models import User
import hashlib

db = SessionLocal()

# Update all test user passwords
users_to_update = [
    ('admin', 'Admin@123'),
    ('staff', 'Staff@123'),
    ('driver1', 'Driver@123'),
    ('driver2', 'Driver@123'),
]

for username, password in users_to_update:
    user = db.query(User).filter(User.username == username).first()
    if user:
        # Use the same salt as in auth service
        salt = "meditrack_salt_2024"
        user.hashed_password = hashlib.sha256(f'{password}{salt}'.encode()).hexdigest()
        db.commit()
        print(f"✓ Updated {username} password hash: {user.hashed_password[:20]}...")
    else:
        print(f"✗ User {username} not found")

db.close()
print("\nAll passwords updated successfully!")
