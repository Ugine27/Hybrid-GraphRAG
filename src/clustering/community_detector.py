import networkx as nx
from community import community_louvain
from neo4j import GraphDatabase
from src.config import config
from typing import Dict, List

class CommunityDetector:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def _fetch_graph(self) -> nx.Graph:
        query = """
        MATCH (s:Entity)-[r]->(t:Entity)
        RETURN s.id AS source, t.id AS target
        """
        with self.driver.session() as session:
            records = session.run(query)
            
            G = nx.Graph()
            for record in records:
                G.add_edge(record["source"], record["target"])
                
        return G

    def detect_communities(self) -> Dict[int, List[str]]:
        G = self._fetch_graph()
        if G.number_of_nodes() == 0:
            return {}
            
        partition = community_louvain.best_partition(G)
        
        communities = {}
        for node, comm_id in partition.items():
            communities.setdefault(comm_id, []).append(node)
            
        self._write_communities_to_db(communities)
        return communities

    def _write_communities_to_db(self, communities: Dict[int, List[str]]):
        query = """
        UNWIND $data AS row
        MATCH (e:Entity {id: row.node})
        SET e.community_id = row.comm_id
        """
        data = [{"node": n, "comm_id": c} for c, nodes in communities.items() for n in nodes]
        with self.driver.session() as session:
            session.run(query, data=data)
