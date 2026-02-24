from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

from app.database import SessionLocal
from app.models import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt_sha256"])

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str
    tenant: str


class LoginRequest(BaseModel):
    username: str
    password: str


def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=2)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(lambda: None)):
    from fastapi.security import HTTPBearer
    from fastapi import Security

    security = HTTPBearer()
    credentials = Security(security)

    payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


@router.post("/register")
def register(req: RegisterRequest):
    db: Session = SessionLocal()

    hashed = pwd_context.hash(req.password)

    user = User(
        username=req.username,
        password=hashed,
        role=req.role,
        tenant=req.tenant,
    )

    db.add(user)
    db.commit()
    db.close()

    return {"status": "created"}


@router.post("/login")
def login(req: LoginRequest):
    db: Session = SessionLocal()

    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "sub": user.username,
        "role": user.role,
        "tenant": user.tenant
    })

    db.close()
    return {"access_token": token}