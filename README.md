# Hybrid GraphRAG

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.18-008CC1.svg?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC382D.svg?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![LangChain](https://img.shields.io/badge/LangChain-Enabled-1C3C3C.svg)](https://langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade **Hybrid Graph-Augmented Retrieval (GraphRAG)** system combining the multi-hop reasoning capabilities of **Knowledge Graphs (Neo4j)** with semantic similarity search from **Dense Vector Databases (Qdrant)**. Features asynchronous entity-relationship extraction, Louvain community clustering, hierarchical summaries, automated Cypher generation with self-healing reflection loops, and Reciprocal Rank Fusion (RRF).

---

## Architecture Overview

```
                      +-----------------------------+
                      |       Raw Document Text     |
                      +--------------+--------------+
                                     |
                                     v
                 +---------------------------------------+
                 | Async Graph Extraction (OpenAI / Pydantic)
                 +-------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 | Entity Resolution & Canonicalization   |
                 +-------------------+-------------------+
                                     |
                                     v
                      +-----------------------------+
                      |  Neo4j Knowledge Graph      |
                      +--------------+--------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
        +-----------------------+         +-----------------------+
        |  Louvain Community    |         | Multi-hop APOC Graph  |
        |  Detection & Summaries|         | Traversals (Neo4j)    |
        +-----------+-----------+         +-----------+-----------+
                    |                                 |
                    +----------------+----------------+
                                     |
     User Query ---> [ Hybrid Retriever & Cypher Agent ] <--- Qdrant Vector Search
                                     |
                                     v
                     +-------------------------------+
                     | Reciprocal Rank Fusion (RRF)  |
                     +---------------+---------------+
                                     |
                                     v
                     +-------------------------------+
                     | Synthesized Answer Generation |
                     +-------------------------------+
```

---

## Key Highlights

- **Dual-Track Hybrid Retrieval**: Unifies dense semantic embeddings (Qdrant) and structural knowledge graph traversals (Neo4j APOC subgraphs) via Reciprocal Rank Fusion (RRF, $k=60$).
- **Structured Knowledge Extraction**: Utilizes LangChain structured outputs with OpenAI models to extract canonicalized entities and relational triples asynchronously with bounded concurrency.
- **Entity Resolution & Canonicalization**: Normalizes aliases and variants into unified nodes, merging multi-source attribute descriptions dynamically.
- **Hierarchical Community Clustering**: Partitions entity relationship graphs using the Louvain modularity algorithm (`python-louvain` / `NetworkX`) and generates structured cluster summaries for global reasoning questions.
- **Self-Healing Cypher Agent**: Converts natural language into Neo4j Cypher queries with dynamic schema introspection and an automatic query error-correction loop.
- **RAGAS Evaluation Pipeline**: Built-in benchmark harness assessing faithfulness, answer relevancy, and context recall.

---

## Project Structure

```
Hybrid-GraphRAG/
├── docker-compose.yml              # Multi-container orchestration (Neo4j + Qdrant)
├── requirements.txt                # Core dependencies
├── .env.example                    # Sample environment configurations
├── eval/
│   └── evaluate_ragas.py           # RAGAS metrics evaluation harness
└── src/
    ├── config.py                   # Centralized configuration & environment loader
    ├── schemas.py                  # Pydantic schemas (Entity, Triple, ClusterSummary)
    ├── pipeline.py                 # End-to-end indexing pipeline entrypoint
    ├── indexing/
    │   ├── extractor.py            # Async LLM-based entity/triple extraction
    │   ├── resolver.py             # Coreference resolution & canonicalization
    │   └── graph_builder.py        # Neo4j batch ingestion engine
    ├── clustering/
    │   ├── community_detector.py   # Louvain algorithm community detector
    │   └── summarizer.py           # Hierarchical community summarizer
    └── retrieval/
        ├── cypher_agent.py         # Text-to-Cypher agent with error self-correction
        └── hybrid_retriever.py     # Dense + Graph RRF hybrid retriever
```

---

## Tech Stack

- **Graph Database**: Neo4j 5.18 (APOC plugin enabled)
- **Vector Database**: Qdrant v1.8.0
- **Frameworks & Orchestration**: LangChain, Pydantic v2, NetworkX, python-louvain
- **LLM & Embeddings**: OpenAI GPT-4 Turbo / text-embedding-3-small
- **Evaluation**: RAGAS, HuggingFace Datasets
- **Containerization**: Docker Compose

---

## Getting Started

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.10+

### 2. Environment Setup
Clone the repository and install dependencies:
```bash
git clone https://github.com/Ugine27/Hybrid-GraphRAG.git
cd Hybrid-GraphRAG

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create your `.env` file based on `.env.example`:
```bash
cp .env.example .env
```
Update `.env` with your OpenAI API key and service credentials.

### 3. Spin up Infrastructure
Start Neo4j and Qdrant in detached mode:
```bash
docker compose up -d
```
- Neo4j Browser: `http://localhost:7474` (Credentials: `neo4j` / `password`)
- Qdrant UI: `http://localhost:6333/dashboard`

### 4. Run the Indexing Pipeline
Index sample source text, resolve entities, construct graph relationships, and build community clusters:
```bash
python -m src.pipeline
```

### 5. Evaluate Retrieval Performance
Run the RAGAS evaluation suite to benchmark the system:
```bash
python -m eval.evaluate_ragas
```

---

## License
MIT License. Built for modularity, scalability, and production RAG applications.
