from fastapi import APIRouter, HTTPException, Request

from database import SessionLocal
from models import User
from Users.utils import LoginRequest, verify_password

router = APIRouter()


@router.post("/login", tags=["user account"])
def login(payload: LoginRequest, request: Request):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == payload.username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(payload.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        forwarded = request.headers.get("x-forwarded-for")
        device_ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
        existing_device_user = db.query(User).filter(User.ip_address == device_ip).first()

        if existing_device_user and existing_device_user.id_user != user.id_user:
            raise HTTPException(
                status_code=401,
                detail="This device is already logged in to another account. Please log out first.",
            )

        user.ip_address = device_ip
        db.commit()
        db.refresh(user)

        return {"message": "Login successful", "user_id": user.id_user, "user_ip": user.ip_address}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()