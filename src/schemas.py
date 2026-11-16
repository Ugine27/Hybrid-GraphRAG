from pydantic import BaseModel, Field
from typing import List, Optional

class Entity(BaseModel):
    id: str = Field(description="Canonical ID of the entity (e.g., 'microsoft_corp').")
    label: str = Field(description="Entity type (e.g., 'COMPANY', 'PERSON', 'PRODUCT').")
    name: str = Field(description="Original surface form or display name of the entity.")
    description: Optional[str] = Field(default=None, description="Detailed description of the entity derived from text.")

class Triple(BaseModel):
    source: str = Field(description="Canonical ID of the source entity.")
    target: str = Field(description="Canonical ID of the target entity.")
    predicate: str = Field(description="Type of relationship in UPPER_SNAKE_CASE (e.g., 'ACQUIRED_BY').")
    context: Optional[str] = Field(default=None, description="Snippet or description explaining the relationship context.")

class ExtractionResult(BaseModel):
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities from the chunk.")
    triples: List[Triple] = Field(default_factory=list, description="Extracted relationship triples.")

class ClusterSummary(BaseModel):
    cluster_id: int = Field(description="ID of the cluster/community.")
    title: str = Field(description="Short thematic title of the cluster.")
    summary: str = Field(description="Comprehensive summary of entities and relationships within this cluster.")
    key_entities: List[str] = Field(default_factory=list, description="List of key entity IDs in this cluster.")
