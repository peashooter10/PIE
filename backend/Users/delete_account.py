from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import User
from Users.utils import UserInfo, verify_password

router = APIRouter()


@router.post("/delete_account",tags=["user account"])
def delete_account(user: UserInfo):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == user.username).first()
        if not existing_user:
            raise HTTPException(status_code=400, detail="The username does not exist")

        if not verify_password(user.password, existing_user.password):
            raise HTTPException(status_code=400, detail="The password isn't correct")

        db.delete(existing_user)
        db.commit()

        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()