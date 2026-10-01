from typing import List, Set, Tuple, Optional
from itertools import combinations
import numpy as np
from stitch.models import Message
from stitch.strategies.base import Stitcher
from stitch.strategies.exact import normalize_email, normalize_phone
from stitch.strategies.fuzzy import (
    extract_domain,
    extract_area_code,
    names_partially_match,
    extract_self_identified_name
)

class EmbeddingMatchStitcher(Stitcher):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", similarity_threshold: float = 0.60):
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _identifiers_partially_match(self, m1: Message, m2: Message) -> bool:
        e1 = normalize_email(m1.sender_email)
        e2 = normalize_email(m2.sender_email)
        if e1 and e2 and e1 == e2:
            return True

        p1 = normalize_phone(m1.sender_phone)
        p2 = normalize_phone(m2.sender_phone)
        if p1 and p2 and p1 == p2:
            return True

        d1 = extract_domain(m1.sender_email)
        d2 = extract_domain(m2.sender_email)
        if d1 and d2 and d1 == d2:
            return True

        ac1 = extract_area_code(m1.sender_phone)
        ac2 = extract_area_code(m2.sender_phone)
        if ac1 and ac2 and ac1 == ac2:
            return True

        name1 = m1.display_name or extract_self_identified_name(m1.text)
        name2 = m2.display_name or extract_self_identified_name(m2.text)
        if names_partially_match(name1, name2):
            return True

        return False

    def partition(self, messages: List[Message]) -> List[Set[str]]:
        message_ids = [m.message_id for m in messages]
        if len(messages) <= 1:
            return [{m} for m in message_ids]

        texts = [m.text for m in messages]
        model = self._get_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        similarity_matrix = np.dot(embeddings, embeddings.T)

        matching_pairs: List[Tuple[str, str]] = []
        for i, j in combinations(range(len(messages)), 2):
            sim = float(similarity_matrix[i, j])
            m1 = messages[i]
            m2 = messages[j]
            if sim >= self.similarity_threshold and self._identifiers_partially_match(m1, m2):
                matching_pairs.append((m1.message_id, m2.message_id))

        return self.build_clusters_from_pairs(message_ids, matching_pairs)
