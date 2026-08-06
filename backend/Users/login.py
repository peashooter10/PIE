from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from database import SessionLocal
from models import User,Role
from Users.utils import LoginRequest, verify_password, UserInfo
from Users.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter()

'''
@router.get("/login", tags=["user account"])
def say_hello(payload:UserInfo):
    db=SessionLocal()
    try:
        name=UserInfo.username
        user=db.query(Role).filter(Role.id_role==UserInfo.id_role).first()
        return {"message": f"Hello {name}",
                "your role": f"{user.role_name}"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
'''


@router.post("/login", tags=["user account"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    db = SessionLocal()
    try:
        # form_data.username and form_data.password automatically handle the Swagger UI form popup
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        forwarded = request.headers.get("x-forwarded-for") if request else None
        device_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request and request.client else "unknown")
        
        existing_device_user = db.query(User).filter(User.ip_address == device_ip).first()

        if existing_device_user and existing_device_user.id_user != user.id_user:
            raise HTTPException(
                status_code=401,
                detail="This device is already logged in to another account. Please log out first.",
            )

        user.ip_address = device_ip
        db.commit()
        db.refresh(user)

        role = db.query(Role).filter(Role.id_role == user.id_role).first()
        role_name = role.role_name if role else "user"
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token({"sub": user.username, "role": role_name}, expires_delta=access_token_expires)
        
        return {"success": "let's go", "access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()