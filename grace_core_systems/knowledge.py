from enum import Enum, auto
from pydantic import BaseModel, Field
from typing import Dict, List, Any
from datetime import datetime
import networkx as nx
import threading

class MemoryType(Enum):
    SEMANTIC = auto()
    EPISODIC = auto()
    PROCEDURAL = auto()
    CONTEXTUAL = auto()

class MemoryChunk(BaseModel):
    id: str = Field(..., min_length=3)
    content: Any
    type: MemoryType
    source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    relations: Dict[str, List[str]] = Field(default_factory=dict)

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, chunk: MemoryChunk):
        self.graph.add_node(chunk.id, **chunk.dict())

    def add_edge(self, source: str, target: str, relation: str):
        if self.graph.has_node(source) and self.graph.has_node(target):
            self.graph.add_edge(source, target, relation=relation)

    def query(self, pattern: Dict) -> List[MemoryChunk]:
        return [
            MemoryChunk(**self.graph.nodes[node])
            for node in self.graph.nodes
            if all(self.graph.nodes[node].get(k) == v for k, v in pattern.items())
        ]

class KnowledgeManager:
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.chunks: Dict[str, MemoryChunk] = {}
        self.lock = threading.RLock()

    def ingest(self, chunk: MemoryChunk):
        with self.lock:
            self.chunks[chunk.id] = chunk
            self.graph.add_node(chunk)

    def recall(self, pattern: Dict) -> List[MemoryChunk]:
        with self.lock:
            return self.graph.query(pattern)