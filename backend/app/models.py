from sqlalchemy import Column, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    password = Column(String)
    role = Column(String)
    tenant = Column(String)