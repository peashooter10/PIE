from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from Files.upload import router as upload_and_download
from Users.create_account import router as create_account_router
from Users.login import router as login_router
from Users.logout import router as logout_router
from Users.delete_account import router as delete_account_router

app = FastAPI()

@app.get("/", tags=["root"])
async def root():
    return {"the server works :)"}

app.add_middleware(SessionMiddleware, secret_key="!secret")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.0.189:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_and_download)
app.include_router(create_account_router)
app.include_router(login_router)
app.include_router(logout_router)
app.include_router(delete_account_router)

print("registred routes:")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"route found: {route.path}")
print("---")
