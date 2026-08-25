# auth.py creates/validates jwts and provides a dependency

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from database import SessionLocal
import models

# Replace with a secure env var in production
SECRET_KEY = "123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class TokenData(BaseModel):
    username: Optional[str] = None
    role_name: Optional[str] = None

# i create a token
def create_access_token(data: Dict[str, str], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# i decode a token
def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise JWTError()
        return TokenData(username=username, role_name=role)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data = decode_token(token)
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == token_data.username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        role = db.query(models.Role).filter(models.Role.id_role == user.id_role).first()
        role_name = role.role_name if role else token_data.role_name
        return {"username": user.username, "role_name": role_name}
    finally:
        db.close()