from fastapi import APIRouter, HTTPException, Depends
from database import SessionLocal
from models import User, Role
from Users.utils import hash_password
from user_roles import DeleteUserRequest, CreateUserRequest
from Users.auth import get_current_user

router = APIRouter()

@router.get("/roles/all_users", tags=["admin"])
def show_all_users(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_name") != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()

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