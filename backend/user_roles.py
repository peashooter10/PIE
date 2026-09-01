from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from database import Base, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal
from models import Role
from pydantic import BaseModel

# class for creating a user as an admin
class CreateUserRequest(BaseModel):
    username: str
    password: str
    ip_address: str = ""
    role_name: str
    diskSpace: int = 0

class DeleteUserRequest(BaseModel):
    username: str
    password: str

def seed_roles():
    db = SessionLocal()
    try:
        for role_name in ["admin", "storage", "user"]:
            if not db.query(Role).filter(Role.role_name == role_name).first():
                db.add(Role(role_name=role_name))
        db.commit()
    finally:
        db.close()

seed_roles()