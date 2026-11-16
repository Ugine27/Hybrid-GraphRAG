import asyncio
from typing import List, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from src.schemas import ExtractionResult, Entity, Triple
from src.config import config

class GraphExtractor:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.LLM_MODEL, 
            api_key=config.OPENAI_API_KEY, 
            temperature=0
        ).with_structured_output(ExtractionResult)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        
        self.prompt = PromptTemplate.from_template(
            "Extract entities and relationships from the following text to build a knowledge graph.\n"
            "Ensure entity IDs are canonicalized and normalized (e.g., 'Microsoft Corp', 'MSFT', 'Microsoft' all map to 'microsoft').\n"
            "Text:\n{text}\n"
        )
        self.chain = self.prompt | self.llm
        self.semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY)

    async def _extract_chunk(self, chunk: str) -> ExtractionResult:
        async with self.semaphore:
            try:
                result = await self.chain.ainvoke({"text": chunk})
                return result
            except Exception as e:
                print(f"Error during chunk extraction: {e}")
                return ExtractionResult(entities=[], triples=[])

    async def extract(self, text: str) -> Tuple[List[Entity], List[Triple]]:
        chunks = self.text_splitter.split_text(text)
        tasks = [self._extract_chunk(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        
        all_entities = []
        all_triples = []
        
        for res in results:
            if res:
                all_entities.extend(res.entities)
                all_triples.extend(res.triples)
                
        return all_entities, all_triples
