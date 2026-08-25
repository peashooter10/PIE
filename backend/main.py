from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from database import SessionLocal
import models


from Files.upload import router as upload_router
from Files.download import router as download_router
from Files.lists import router as lists_router

from Users.create_account import router as create_account_router
from Users.login import router as login_router
from Users.logout import router as logout_router
from Users.delete_account import router as delete_account_router

from Roles.admin import router as admin_router
from Roles.storage import router as storage_router
from Roles.user import router as user_router

app = FastAPI()



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

app.include_router(upload_router)
app.include_router(download_router)
app.include_router(lists_router)

app.include_router(create_account_router)
app.include_router(login_router)
app.include_router(logout_router)
app.include_router(delete_account_router)

app.include_router(admin_router)
app.include_router(storage_router)
app.include_router(user_router)

print("registred routes:")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"route found: {route.path}")
print("---")


@app.get("/", tags=["root"])
async def root():
    return {"the server works :)"}

@app.on_event("shutdown")
def logout_all_users_on_shutdown():
    db = SessionLocal()
    try:
        # clear the ip_address field for all users 
        db.query(models.User).update({models.User.ip_address: ""})
        db.commit()
        print("Logged out all users on shutdown.")
    except Exception as e:
        db.rollback()
        print("Failed to clear user logins on shutdown:", e)
    finally:
        db.close()

