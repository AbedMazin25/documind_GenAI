from openai import AsyncOpenAI
import networkx as nx
from app.config import settings
from app.rag.retriever import retriever
import json

_client = AsyncOpenAI(api_key=settings.openai_api_key)

ENTITY_PROMPT = (
    "Extract all financial entities from the text. "
    "Return JSON: {\"entities\": [{\"name\": str, \"type\": str, \"value\": str}]}"
)
RELATION_PROMPT = (
    "Given these entities, extract relationships. "
    "Return JSON: {\"relations\": [{\"source\": str, \"target\": str, \"relation\": str}]}"
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
            messages=[{"role": "system", "content": ENTITY_PROMPT}, {"role": "user", "content": text[:4000]}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        try:
            return json.loads(resp.choices[0].message.content).get("entities", [])
        except (json.JSONDecodeError, KeyError):
            return []

    async def extract_relations(self, text: str, entities: list[dict]) -> list[dict]:
        resp = await _client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "system", "content": RELATION_PROMPT},
                      {"role": "user", "content": f"Entities: {[e['name'] for e in entities]}\nText: {text[:3000]}"}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        try:
            return json.loads(resp.choices[0].message.content).get("relations", [])
        except (json.JSONDecodeError, KeyError):
            return []

    async def add_document(self, org_id: str, doc_id: str, chunks: list[str]):
        g = self._get_graph(org_id)
        for chunk in chunks:
            entities = await self.extract_entities(chunk)
            relations = await self.extract_relations(chunk, entities)
            for ent in entities:
                g.add_node(ent["name"], type=ent["type"], value=ent.get("value", ""), doc_id=doc_id)
            for rel in relations:
                if rel["source"] in g and rel["target"] in g:
                    g.add_edge(rel["source"], rel["target"], relation=rel["relation"])

    def get_subgraph(self, org_id: str, entity: str, hops: int = 2) -> list[dict]:
        g = self._get_graph(org_id)
        if entity not in g:
            return []
        sub = nx.ego_graph(g, entity, radius=hops)
        return [{"node": n, **g.nodes[n]} for n in sub.nodes]

    async def augment_context(self, org_id: str, question: str, docs: list[dict]) -> list[dict]:
        entities = await self.extract_entities(question)
        extra = []
        for ent in entities[:3]:
            neighbors = self.get_subgraph(org_id, ent["name"], hops=2)
            for neighbor in neighbors[:4]:
                extra_docs = retriever.retrieve(neighbor["node"], org_id, k=2)
                extra.extend(extra_docs)
        return docs + extra

graph_rag = GraphRAG()
