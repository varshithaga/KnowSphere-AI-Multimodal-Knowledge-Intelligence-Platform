from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import verify_password

from  app.models import User

router = APIRouter(prefix="/", tags=["Users"])

@router.post("/login")
def login_user(db: Session , username : str, password : str):
    user =db.query(User).filter(User.username==username).first()

    if not user :
        raise HTTPException(
            status_code =status.HTTP_401_UNAUTHORIZED,
            detail ="Invalid username "
        )

    if not verify_password(password,user.password_hash):
        raise HTTPException(
            status_code =status.HTTP_401_UNAUTHORIZED,
            detail ="Invalid password "
        )

    return {"message": "Login successful", "user": user}