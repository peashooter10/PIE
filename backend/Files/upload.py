from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File as FastAPIFile
from database import SessionLocal
from models import User, File as DbFile, Type, User_Files
from Users.auth import get_current_user
from pathlib import Path
import os

router = APIRouter()

STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", str(Path.home() / "pie_storage")))

def safe_username(username: str) -> str:
    return "".join(c for c in username if c.isalnum() or c in ("-", "_")).strip()

def user_dir(username: str) -> Path:
    return STORAGE_ROOT / f"My_cloud_{safe_username(username)}"

@router.post("/files/upload", tags=["files"])
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: dict = Depends(get_current_user),
):
    username = current_user.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid user")

    target_dir = user_dir(username)
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise HTTPException(status_code=500, detail="Storage root not writable")

    basename = Path(file.filename).name
    dest = target_dir / basename
    if dest.exists():
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        dest = target_dir / f"{Path(basename).stem}_{ts}{Path(basename).suffix}"

    contents = await file.read()
    try:
        with open(dest, "wb") as f:
            f.write(contents)
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        ext = dest.suffix.lower().lstrip(".") or "unknown"

        file_type = db.query(Type).filter(Type.type_name == ext).first()
        if not file_type:
            file_type = Type(type_name=ext)
            db.add(file_type)
            db.flush()

        new_file = DbFile(
            file_name=dest.name,
            id_type=file_type.id_type,
            file_path=str(dest),
            file_size=dest.stat().st_size,
            upload_time=datetime.utcnow(),
        )
        db.add(new_file)
        db.flush()

        user_file_link = User_Files(
            id_user=user.id_user,
            id_file=new_file.id_file,
            inSync=False,
        )
        db.add(user_file_link)

        user.id_files = new_file.id_file
        db.commit()
        db.refresh(new_file)
        db.refresh(user_file_link)

        return {
            "message": "File uploaded successfully",
            "file": {
                "id_file": new_file.id_file,
                "file_name": new_file.file_name,
                "file_path": new_file.file_path,
                "file_size": new_file.file_size,
                "id_type": new_file.id_type,
                "type_name": file_type.type_name,
                "upload_time": new_file.upload_time.isoformat() if new_file.upload_time else None,
            },
            "user_file_link": {
                "id_user_files": user_file_link.id_user_files,
                "id_user": user_file_link.id_user,
                "inSync": user_file_link.inSync,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Upload DB error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()