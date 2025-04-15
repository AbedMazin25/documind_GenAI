from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()

class QueryRequest(BaseModel):
    question: str
    document_ids: Optional[list[str]] = None
    mode: str = "agent"

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    reasoning_steps: Optional[list[str]] = None

@router.post("/", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    result = await agent_service.run(
        question=req.question,
        org_id=str(current_user.org_id),
        document_ids=req.document_ids,
    )
    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        reasoning_steps=result.get("steps"),
    )
