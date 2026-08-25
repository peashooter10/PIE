from fastapi import APIRouter, HTTPException, Depends
from database import SessionLocal
from models import User, Role
from Users.auth import get_current_user
import os
import shutil
from pathlib import Path
from pydantic import BaseModel

router = APIRouter()

class StorageOption(BaseModel):
     option:str

@router.get("/roles/show_all_storage", tags=["user"])
def show_all_storage_units(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_name") != "user":
        raise HTTPException(status_code=403, detail="Access denied. Users only.")

    db = SessionLocal()
    try:
        storage_users=db.query(User).filter(User.id_role==2).all()
        return storage_users
    finally:
        db.close()

@router.post("/roles/select_storage",tags=["user"])
def select_storage(payload:StorageOption,current_user:dict = Depends(get_current_user)):
    if current_user.get("role_name") != "user":
            raise HTTPException(status_code=403, detail="Access denied. Users only.")

    db = SessionLocal()
    try:
        option = db.query(User).filter(User.username == payload.option, User.id_role == 2).first()
        if not option:
            raise HTTPException(status_code=404, detail="Storage not found")
        return {"username": option.username, "id_role": option.id_role}
    finally:
        db.close()

