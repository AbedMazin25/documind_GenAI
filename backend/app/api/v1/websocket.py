from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.services.agent_service import AgentService
import json

router = APIRouter()
agent_service = AgentService()

@router.websocket("/query")
async def ws_query(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            question = payload.get("question", "")
            org_id = payload.get("org_id", "")
            document_ids = payload.get("document_ids")

            async for chunk in agent_service.stream(
                question=question,
                org_id=org_id,
                document_ids=document_ids,
            ):
                await websocket.send_text(json.dumps({"chunk": chunk}))
            await websocket.send_text(json.dumps({"done": True}))
    except WebSocketDisconnect:
        pass
