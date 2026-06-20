from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.security import decode_token
from app.services.agent_service import AgentService
from jose import JWTError
import json

router = APIRouter()
agent_service = AgentService()


@router.websocket("/query")
async def ws_query(websocket: WebSocket):
    token = websocket.query_params.get("token")
    org_id = None
    if token:
        try:
            payload = decode_token(token)
            org_id = payload.get("org")
        except JWTError:
            org_id = None

    if not org_id:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            question = payload.get("query") or payload.get("question") or ""
            document_ids = payload.get("document_ids")
            if not question.strip():
                continue

            try:
                async for event in agent_service.stream_events(
                    question=question,
                    org_id=org_id,
                    document_ids=document_ids,
                ):
                    await websocket.send_text(json.dumps(event))
            except Exception as exc:  # noqa: BLE001
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "token",
                            "content": "Sorry, something went wrong generating a response.",
                        }
                    )
                )
            await websocket.send_text(json.dumps({"type": "done"}))
    except WebSocketDisconnect:
        pass
