from typing import List, Tuple, Dict
from src.schemas import Entity, Triple

class EntityResolver:
    """
    Handles coreference resolution and entity canonicalization.
    In a production environment, this would use cross-encoders or graph algorithms.
    Here we implement a robust ID-based merging system with alias tracking.
    """
    
    def __init__(self):
        self.entity_map: Dict[str, Entity] = {}
        
    def resolve(self, entities: List[Entity], triples: List[Triple]) -> Tuple[List[Entity], List[Triple]]:
        # 1. Merge Entities
        for entity in entities:
            canonical_id = entity.id.lower().strip()
            
            if canonical_id in self.entity_map:
                existing = self.entity_map[canonical_id]
                if entity.description and existing.description and entity.description not in existing.description:
                    existing.description += f" | {entity.description}"
                elif entity.description and not existing.description:
                    existing.description = entity.description
            else:
                entity.id = canonical_id
                self.entity_map[canonical_id] = entity
                
        resolved_entities = list(self.entity_map.values())
        
        # 2. Resolve Triples (deduplicate and link to canonical IDs)
        unique_triples = {}
        for t in triples:
            s_id = t.source.lower().strip()
            t_id = t.target.lower().strip()
            p = t.predicate.upper().strip()
            
            if s_id not in self.entity_map or t_id not in self.entity_map:
                continue
                
            triple_key = f"{s_id}-{p}-{t_id}"
            
            if triple_key in unique_triples:
                existing_t = unique_triples[triple_key]
                if t.context and existing_t.context and t.context not in existing_t.context:
                    existing_t.context += f" | {t.context}"
                elif t.context and not existing_t.context:
                    existing_t.context = t.context
            else:
                t.source = s_id
                t.target = t_id
                t.predicate = p
                unique_triples[triple_key] = t
                
        resolved_triples = list(unique_triples.values())
        
        return resolved_entities, resolved_triples
