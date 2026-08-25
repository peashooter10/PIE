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

@router.post("/files/upload", tags=["files"])
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    username = current_user.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid user")

    target_dir = user_dir(username)
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise HTTPException(status_code=500, detail="Storage root not writable")

    # sanitize filename and avoid overwriting by appending timestamp if exists
    basename = Path(file.filename).name
    dest = target_dir / basename
    if dest.exists():
        ts = time.strftime("%Y%m%d-%H%M%S")
        dest = target_dir / f"{Path(basename).stem}_{ts}{Path(basename).suffix}"

    contents = await file.read()
    try:
        with open(dest, "wb") as f:
            f.write(contents)
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"filename": dest.name, "path": str(dest)}


