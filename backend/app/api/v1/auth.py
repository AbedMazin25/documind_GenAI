from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db.session import get_db
from app.models.user import User
from app.models.org import Org
from app.core.security import hash_password, verify_password, create_access_token
import uuid

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    org_name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    org = Org(name=data.org_name, slug=data.org_name.lower().replace(" ", "-"))
    db.add(org)
    db.flush()
    user = User(
        org_id=org.id,
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "org": str(user.org_id)})
    return TokenResponse(access_token=token)
