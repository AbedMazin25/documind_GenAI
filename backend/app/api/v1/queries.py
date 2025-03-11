from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.rag.chains import rag_chain

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    document_ids: Optional[list[str]] = None
    k: int = 6

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

@router.post("/", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    result = await rag_chain.run(
        question=req.question,
        org_id=str(current_user.org_id),
        document_ids=req.document_ids,
        k=req.k,
    )
    return QueryResponse(answer=result["answer"], sources=result["sources"])
