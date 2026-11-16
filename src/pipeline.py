import asyncio
from src.indexing.extractor import GraphExtractor
from src.indexing.resolver import EntityResolver
from src.indexing.graph_builder import GraphBuilder
from src.clustering.community_detector import CommunityDetector
from src.clustering.summarizer import HierarchicalSummarizer

async def index_document(text: str):
    print("1. Extracting entities and triples...")
    extractor = GraphExtractor()
    entities, triples = await extractor.extract(text)
    
    print(f"Extracted {len(entities)} raw entities and {len(triples)} raw triples.")
    
    print("2. Resolving and canonicalizing...")
    resolver = EntityResolver()
    res_entities, res_triples = resolver.resolve(entities, triples)
    
    print(f"Resolved down to {len(res_entities)} unique entities and {len(res_triples)} unique triples.")
    
    print("3. Building Graph in Neo4j...")
    builder = GraphBuilder()
    builder.build_graph(res_entities, res_triples)
    builder.close()
    
    print("4. Detecting Communities...")
    detector = CommunityDetector()
    communities = detector.detect_communities()
    detector.close()
    
    print(f"Detected {len(communities)} communities.")
    
    print("5. Generating Cluster Summaries...")
    summarizer = HierarchicalSummarizer()
    await summarizer.summarize_communities(communities)
    summarizer.close()
    
    print("Indexing Complete!")

if __name__ == "__main__":
    sample_text = """
    Microsoft Corp acquired LinkedIn in 2016. Satya Nadella is the CEO of Microsoft.
    LinkedIn was founded by Reid Hoffman. OpenAI received significant investment from Microsoft.
    Sam Altman is the CEO of OpenAI. Apple competes with Microsoft in the personal computing space.
    Tim Cook, also known as Timothy D. Cook, leads Apple as its CEO.
    """
    asyncio.run(index_document(sample_text))
