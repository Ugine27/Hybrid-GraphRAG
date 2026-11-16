from neo4j import GraphDatabase
from typing import List
from src.schemas import Entity, Triple
from src.config import config

class GraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI, 
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def build_graph(self, entities: List[Entity], triples: List[Triple]):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE")
            session.execute_write(self._batch_write_entities, entities)
            session.execute_write(self._batch_write_triples, triples)
            
    @staticmethod
    def _batch_write_entities(tx, entities: List[Entity]):
        query = """
        UNWIND $entities AS e
        MERGE (n:Entity {id: e.id})
        SET n.name = e.name, n.label = e.label, n.description = e.description
        """
        tx.run(query, entities=[e.model_dump() for e in entities])

    @staticmethod
    def _batch_write_triples(tx, triples: List[Triple]):
        query = """
        UNWIND $triples AS t
        MATCH (source:Entity {id: t.source})
        MATCH (target:Entity {id: t.target})
        CALL apoc.create.relationship(source, t.predicate, {context: t.context}, target) YIELD rel
        RETURN count(rel)
        """
        tx.run(query, triples=[t.model_dump() for t in triples])
