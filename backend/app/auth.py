from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session
from app.authModels import User
from passlib.context import CryptContext
import os

SECRET = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt_sha256"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def authenticate(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not pwd_context.verify(password, user.password):
        return None

    return user

def create_token(data: dict):
    return jwt.encode(data, SECRET, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")