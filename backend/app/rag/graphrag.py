from openai import AsyncOpenAI
import networkx as nx
from app.config import settings
import json

_client = AsyncOpenAI(api_key=settings.openai_api_key)

ENTITY_PROMPT = (
    "Extract all financial entities from the text. "
    "Return JSON: {\"entities\": [{\"name\": str, \"type\": str, \"value\": str}]}"
)

class GraphRAG:
    def __init__(self):
        self.graphs: dict[str, nx.DiGraph] = {}

    def _get_graph(self, org_id: str) -> nx.DiGraph:
        if org_id not in self.graphs:
            self.graphs[org_id] = nx.DiGraph()
        return self.graphs[org_id]

    async def extract_entities(self, text: str) -> list[dict]:
        resp = await _client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": ENTITY_PROMPT},
                {"role": "user", "content": text[:4000]},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        data = json.loads(resp.choices[0].message.content)
        return data.get("entities", [])

    async def add_document(self, org_id: str, doc_id: str, chunks: list[str]):
        g = self._get_graph(org_id)
        for chunk in chunks:
            entities = await self.extract_entities(chunk)
            for ent in entities:
                g.add_node(ent["name"], type=ent["type"], value=ent.get("value", ""))

graph_rag = GraphRAG()
