from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Any
from src.config import config

class HybridRetriever:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        self.qdrant = QdrantClient(url=config.QDRANT_URL)
        self.embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY
        )
        
    def close(self):
        self.driver.close()

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # 1. Track A: Dense Vector Retrieval
        dense_results = self._dense_search(query, top_k)
        
        # 2. Track B: Graph Traversal via apoc.path.subgraphAll
        seed_entities = [res['entity_id'] for res in dense_results]
        graph_results = self._graph_search(seed_entities, top_k)
        
        # 3. Merge with Reciprocal Rank Fusion
        merged_results = self._rrf(dense_results, graph_results, k=60)
        
        return merged_results[:top_k]

    def _dense_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        query_vector = self.embeddings.embed_query(query)
        try:
            hits = self.qdrant.search(
                collection_name="entities",
                query_vector=query_vector,
                limit=top_k
            )
            return [{"entity_id": hit.payload.get("id"), "score": hit.score, "type": "dense"} for hit in hits]
        except Exception:
            return []

    def _graph_search(self, seed_entities: List[str], top_k: int) -> List[Dict[str, Any]]:
        if not seed_entities:
            return []
            
        query = """
        MATCH (e:Entity) WHERE e.id IN $seeds
        CALL apoc.path.subgraphAll(e, {maxLevel: 2}) YIELD nodes, relationships
        RETURN [n in nodes | n.id] AS node_ids, length(relationships) as rel_count
        ORDER BY rel_count DESC
        LIMIT $limit
        """
        results = []
        with self.driver.session() as session:
            records = session.run(query, seeds=seed_entities, limit=top_k)
            for i, record in enumerate(records):
                results.append({"node_ids": record["node_ids"], "score": 1.0 / (i + 1), "type": "graph"})
        return results

    def _rrf(self, list1: List[Dict[str, Any]], list2: List[Dict[str, Any]], k: int = 60) -> List[Dict[str, Any]]:
        scores = {}
        
        for rank, item in enumerate(list1):
            key = item.get("entity_id", str(item))
            if key not in scores:
                scores[key] = {"item": item, "score": 0.0}
            scores[key]["score"] += 1.0 / (k + rank + 1)
            
        for rank, item in enumerate(list2):
            key = str(item.get("node_ids", item))
            if key not in scores:
                scores[key] = {"item": item, "score": 0.0}
            scores[key]["score"] += 1.0 / (k + rank + 1)
            
        sorted_results = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return [res["item"] for res in sorted_results]
