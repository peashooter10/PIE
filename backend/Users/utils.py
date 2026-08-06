import hashlib
from pydantic import BaseModel


class UserInfo(BaseModel):
    username: str
    password: str
    ip_address: str


class LoginRequest(BaseModel):
    username: str
    password: str
    ip_address: str


class LogoutRequest(BaseModel):
    username: str
    password: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password


def get_device_ip(ip_address: str | None) -> str:
    return ip_address or ""

def get_my_name(payload: UserInfo) -> str:
    return payload.username

def get_my_role(payload: UserInfo) -> str:
    return UserInfo.username