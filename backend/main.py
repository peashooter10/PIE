from fastapi import FastAPI, UploadFile
from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import time, os
import json
import yaml
timestr=time.strftime("%Y%m%d-%H%M%S")

# import routerele
from Files.upload import router as upload_and_download

app=FastAPI()

# middleware

app.add_middleware(SessionMiddleware, secret_key="!secret")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://192.168.0.189:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# includ routere
app.include_router(upload_and_download)

@app.get("/", tags=["root"])
async def root():
    return {"serverul merge :)"}

