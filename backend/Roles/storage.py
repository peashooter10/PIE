from fastapi import APIRouter, HTTPException, Depends
from database import SessionLocal
from models import User, Role
from Users.auth import get_current_user
import os
import shutil
from pathlib import Path


BASE_DIR="C://"

router = APIRouter()

@router.get("/roles/all_storage", tags=["storage"])
def show_all_storage_units(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_name") != "storage":
        raise HTTPException(status_code=403, detail="Access denied. Storage only.")

    db = SessionLocal()
    try:
        storage_users=db.query(User).filter(User.id_role==2).all()
        return storage_users
    finally:
        db.close()

@router.get("/roles/create_upload_folder", tags=["storage"])
def create_upload_folder(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_name") != "storage":
        raise HTTPException(status_code=403, detail="Access denied. Storage only.")
    
    db = SessionLocal()
    try:

        directoryName=BASE_DIR+"My_cloud" + "_" +current_user.get("username")
        try:
            os.mkdir(directoryName)
            return(f"Directory '{directoryName}' created successfully.")
        except FileExistsError:
            return(f"Directory '{directoryName}' already exists.")
        except PermissionError:
            return(f"Permission denied: Unable to create '{directoryName}'.")
        except Exception as e:
            return(f"An error occurred: {e}")

    finally:
        db.close()

@router.post("/roles/free_storage", tags=["storage"])
def storage_info(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_name") != "storage":
        raise HTTPException(status_code=403, detail="Access denied. Storage only.")

    db = SessionLocal()
    try:
        directoryName = BASE_DIR + "My_cloud_" + current_user.get("username")
        if not os.path.exists(directoryName):
            raise HTTPException(status_code=404, detail="User storage directory not found")

        total, used, free = shutil.disk_usage(directoryName)
        user = db.query(User).filter(User.username == current_user.get("username")).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.diskSpace = free
        db.commit()
        return {
            "username": user.username, 
            "total_bytes":total,
            "used_bytes":used,
            "free_bytes": free
                }
    finally:
        db.close()
   