from fastapi import FastAPI, Form, HTTPException
from app.auth import authenticate, create_token
from app.database import engine,SessionLocal,Base
from app.authModels import Base,User
from app.ingest import router as ingest_router
from pydantic import BaseModel
from passlib.context import CryptContext
from app.opensearch import client
import os

app = FastAPI()
app.include_router(ingest_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/os-health")
def os_health():
    return client.info()

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
def create_index():
    if not client.indices.exists(index="logs-*"):
        client.indices.create(
            index="logs-demo",
            body={
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "tenant": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "event_type": {"type": "keyword"},
                        "severity": {"type": "integer"},
                        "src_ip": {"type": "ip"},
                        "user": {"type": "keyword"},
                        "raw": {"type": "object"}
                    }
                }
            }
        )

pwd_context = CryptContext(schemes=["bcrypt_sha256"])

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str
    tenant: str

@app.post("/register")
def rregister(req: RegisterRequest):
    username = req.username
    password = req.password
    role = req.role
    tenant = req.tenant

    db = SessionLocal()
    print(password)
    user = User(
        username=username,
        password=pwd_context.hash(password),
        role=role,
        tenant=tenant
    )
    
    db.add(user)
    db.commit()
    db.close()

    return {"status": "created"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(req: LoginRequest):
    db = SessionLocal()

    user = db.query(User).filter(User.username == req.username).first()

    if not user:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(req.password, user.password):
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "sub": user.username,
        "role": user.role,
        "tenant": user.tenant
    })

    db.close()
    return {"access_token": token}