from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import Dict, List
from src.config import config
from src.schemas import ClusterSummary

class HierarchicalSummarizer:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        self.llm = ChatOpenAI(
            model=config.LLM_MODEL, 
            api_key=config.OPENAI_API_KEY, 
            temperature=0
        ).with_structured_output(ClusterSummary)
        
        self.prompt = PromptTemplate.from_template(
            "You are an expert graph summarizer. Based on the following entities and relationships belonging to a single community, "
            "generate a comprehensive summary.\n\n"
            "Community ID: {comm_id}\n"
            "Entities: {entities}\n"
            "Relationships: {relationships}\n"
        )
        
    def close(self):
        self.driver.close()

    async def summarize_communities(self, communities: Dict[int, List[str]]) -> List[ClusterSummary]:
        summaries = []
        for comm_id, nodes in communities.items():
            entities, relationships = self._fetch_subgraph_data(nodes)
            
            summary = await self.llm.ainvoke(self.prompt.format(
                comm_id=comm_id, 
                entities=entities, 
                relationships=relationships
            ))
            summary.cluster_id = comm_id
            summary.key_entities = nodes
            summaries.append(summary)
            
            self._write_summary_to_db(summary)
            
        return summaries

    def _fetch_subgraph_data(self, nodes: List[str]):
        with self.driver.session() as session:
            entity_query = "MATCH (e:Entity) WHERE e.id IN $nodes RETURN e.id AS id, e.name AS name, e.description AS description"
            rel_query = """
            MATCH (s:Entity)-[r]->(t:Entity) 
            WHERE s.id IN $nodes AND t.id IN $nodes 
            RETURN s.id AS source, type(r) AS type, t.id AS target, r.context AS context
            """
            
            e_records = session.run(entity_query, nodes=nodes)
            entities = [{"id": r["id"], "name": r["name"], "desc": r["description"]} for r in e_records]
            
            r_records = session.run(rel_query, nodes=nodes)
            relationships = [{"source": r["source"], "type": r["type"], "target": r["target"], "context": r["context"]} for r in r_records]
            
        return entities, relationships

    def _write_summary_to_db(self, summary: ClusterSummary):
        query = """
        MERGE (c:Community {id: $comm_id})
        SET c.title = $title, c.summary = $summary
        WITH c
        UNWIND $entities AS e_id
        MATCH (e:Entity {id: e_id})
        MERGE (e)-[:BELONGS_TO]->(c)
        """
        with self.driver.session() as session:
            session.run(query, 
                        comm_id=summary.cluster_id, 
                        title=summary.title, 
                        summary=summary.summary, 
                        entities=summary.key_entities)
