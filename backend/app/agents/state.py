from typing import Optional, Annotated
from typing_extensions import TypedDict
import operator

class AgentState(TypedDict):
    question: str
    org_id: str
    document_ids: Optional[list[str]]
    route: Optional[str]
    retrieved_docs: Annotated[list[dict], operator.add]
    analysis: Optional[str]
    answer: Optional[str]
    steps: Annotated[list[str], operator.add]
