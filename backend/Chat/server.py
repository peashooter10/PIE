from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from jose import JWTError

from database import SessionLocal
from models import User, Role
from Users.auth import decode_token

router = APIRouter()
connections: dict[WebSocket, str] = {}


@router.websocket("/ws/chat")
async def chat(websocket: WebSocket, token: str):
    try:
        token_data = decode_token(token)

        db = SessionLocal()
        try:
            user = db.query(User).filter(
                User.username == token_data.username
            ).first()

            if not user:
                raise HTTPException(status_code=401, detail="User not found")

            role = db.query(Role).filter(
                Role.id_role == user.id_role
            ).first()

            if not role or role.role_name != "user":
                raise HTTPException(status_code=403, detail="Users only")

            username = user.username
        finally:
            db.close()

    except (JWTError, HTTPException):
        await websocket.close(code=1008, reason="Invalid authentication")
        return

    await websocket.accept()
    connections[websocket] = username

    try:
        await broadcast({
            "type": "system",
            "message": f"{username} joined the chat"
        })

        while True:
            message = await websocket.receive_text()

            await broadcast({
                "type": "message",
                "username": username,
                "message": message
            })

    except WebSocketDisconnect:
        connections.pop(websocket, None)
        await broadcast({
            "type": "system",
            "message": f"{username} left the chat"
        })


async def broadcast(message: dict[str, str]):
    disconnected = []

    for websocket in connections:
        try:
            await websocket.send_json(message)
        except Exception:
            disconnected.append(websocket)

    for websocket in disconnected:
        connections.pop(websocket, None)