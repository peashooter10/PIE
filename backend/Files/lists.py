from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from database import SessionLocal
from models import User
from Users.auth import get_current_user
from pathlib import Path
import os
import time

router = APIRouter()

STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", Path.home() / "pie_storage"))

def safe_username(username: str) -> str:
    return "".join(c for c in username if c.isalnum() or c in ("-", "_")).strip()

def user_dir(username: str) -> Path:
    return STORAGE_ROOT / f"My_cloud_{safe_username(username)}"

@router.get("/files/list", tags=["files"])
def list_files(current_user: dict = Depends(get_current_user)):
    username = current_user.get("username")
    target_dir = user_dir(username)
    if not target_dir.exists():
        return {"files": []}
    files = [p.name for p in target_dir.iterdir() if p.is_file()]
    return {"files": files}