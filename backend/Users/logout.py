from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import User
from Users.utils import LogoutRequest, verify_password

router = APIRouter()


@router.post("/logout",tags=["user account"])
def logout(payload: LogoutRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == payload.username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(payload.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        user.ip_address = ""
        db.commit()

        return {"message": "Logout successful"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()