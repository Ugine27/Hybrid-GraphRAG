from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from src.config import config
import re

class CypherAgent:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        self.llm = ChatOpenAI(
            model=config.LLM_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0
        )
        self.schema_info = self._get_schema()
        
        self.gen_prompt = PromptTemplate.from_template(
            "You are a Neo4j Cypher expert. Generate a Cypher query to answer the following question.\n"
            "Schema Info: {schema}\n"
            "Question: {question}\n"
            "Cypher Query:"
        )
        
        self.fix_prompt = PromptTemplate.from_template(
            "The following Cypher query resulted in an error.\n"
            "Schema: {schema}\n"
            "Query: {query}\n"
            "Error: {error}\n"
            "Please provide a corrected Cypher query. Output ONLY the query."
        )

    def close(self):
        self.driver.close()

    def _get_schema(self) -> str:
        return "Node labels: Entity, Community. Rel types: ACQUIRED_BY, FOUNDED_BY, BELONGS_TO."

    def _extract_query(self, text: str) -> str:
        match = re.search(r'```cypher\n(.*?)\n```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    async def execute_query(self, question: str, max_retries: int = 3) -> list:
        response = await self.llm.ainvoke(self.gen_prompt.format(
            schema=self.schema_info,
            question=question
        ))
        
        query = self._extract_query(response.content)
        
        for attempt in range(max_retries):
            try:
                with self.driver.session() as session:
                    result = session.run(query)
                    return [r.data() for r in result]
            except Exception as e:
                print(f"Cypher Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    print("Max retries reached. Falling back to vector retrieval.")
                    return []
                    
                fix_response = await self.llm.ainvoke(self.fix_prompt.format(
                    schema=self.schema_info,
                    query=query,
                    error=str(e)
                ))
                query = self._extract_query(fix_response.content)
                
        return []
