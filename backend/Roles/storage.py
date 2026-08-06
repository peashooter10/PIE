from fastapi import APIRouter, HTTPException, Depends
from database import SessionLocal
from models import User, Role
from Users.auth import get_current_user
import os
import shutil
from pydantic import BaseModel

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

@router.get("/roles/all_storage", tags=["storage"])
def show_all_storage_units(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_name") != "storage":
        raise HTTPException(status_code=403, detail="Access denied. Storage only.")
    
    db = SessionLocal()
    try:
        directory_name="My_cloud" + current_user.get("username")
        try:
            os.mkdir(directory_name)
            print(f"Directory '{directory_name}' created successfully.")
        except FileExistsError:
            print(f"Directory '{directory_name}' already exists.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{directory_name}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

    finally:
        db.close()

'''
@router.post("/roles/create", tags=["admin"])
def create_user(payload: CreateUserRequest, current_user: dict = Depends(get_current_user)):
    if current_user.get("role_name") != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == payload.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        role = db.query(Role).filter(Role.role_name == payload.role_name).first()
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role")

        new_user = User(
            username=payload.username,
            password=hash_password(payload.password),
            ip_address=payload.ip_address,
            id_role=role.id_role,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created successfully",
            "username": new_user.username,
            "id_role": new_user.id_role,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/roles/delete", tags=["admin"])
def delete_user(payload: DeleteUserRequest, current_user: dict = Depends(get_current_user)):
    if current_user.get("role_name") != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == payload.username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(user)
        db.commit()
        return {"message": f"User {payload.username} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

'''