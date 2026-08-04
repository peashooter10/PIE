from fastapi import APIRouter, HTTPException, Request

from database import SessionLocal
from models import Role, User
from Users.utils import UserInfo, hash_password

router = APIRouter()


@router.post("/create_account", tags=["user account"])
def create_account(user: UserInfo, request: Request):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == user.username).first()
        forwarded = request.headers.get("x-forwarded-for")
        device_ip = (
            forwarded.split(",")[0].strip()
            if forwarded
            else (request.client.host if request.client else "unknown")
        )
        existing_device_user = db.query(User).filter(User.ip_address == device_ip).first()
        if existing_device_user:
            raise HTTPException(status_code=400, detail="This device is already linked to another account")

        role = db.query(Role).filter(Role.role_name == "user").first()
        if not role:
            raise HTTPException(status_code=500, detail="User role is not configured")

        new_user = User(
            username=user.username,
            password=hash_password(user.password),
            ip_address=device_ip,
            id_role=role.id_role,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User created successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()