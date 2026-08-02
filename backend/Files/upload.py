from fastapi import FastAPI, UploadFile
from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import time, os
import json
import yaml
timestr=time.strftime("%Y%m%d-%H%M%S")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

@router.post("/updown",tags=["updown"])
def upload_and_download(file: UploadFile):
    if file.content_type != "application/json":
        return {"error": "Invalid file type. Only JSON files are allowed."}
    else:
        json_data=json.loads(file.file.read())
        new_filename = "{}_{}.yaml".format(os.path.splitext(file.filename)[0],timestr)
        # scriu datele intr-un fisier
        # salvez fisierul
        SAVE_FILE_PATH = os.path.join(UPLOAD_DIR, new_filename)
        with open(SAVE_FILE_PATH, "w") as f:
            yaml.dump(json_data, f)

        return FileResponse(path=SAVE_FILE_PATH, media_type="application/octet-stream", filename=new_filename)
