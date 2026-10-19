from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.security import hash_password

router = APIRouter(prefix="/", tags=["Users"])

    
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if username or email already exists
    existing_user = (
        db.query(User)
        .filter((User.username == user_in.username) | (User.email == user_in.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # 2. Create the user with a hashed password
    new_user = User(
        name=user_in.name,
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )

    # 3. Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. Return the user (UserResponse removes the password automatically)
    return new_user