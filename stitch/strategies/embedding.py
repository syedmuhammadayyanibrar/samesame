from typing import List, Set, Tuple, Optional
from itertools import combinations
import numpy as np
from stitch.models import Message
from stitch.strategies.base import Stitcher
from stitch.strategies.exact import (
    get_message_emails,
    get_message_phones
)
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

    def _identifiers_partially_match(
        self,
        m1: Message,
        m2: Message,
        emails1: Set[str],
        emails2: Set[str],
        phones1: Set[str],
        phones2: Set[str]
    ) -> bool:
        if emails1 & emails2:
            return True

        if phones1 & phones2:
            return True

        domains1 = {extract_domain(e) for e in emails1 if extract_domain(e)}
        domains2 = {extract_domain(e) for e in emails2 if extract_domain(e)}
        if domains1 & domains2:
            return True

        ac1 = {extract_area_code(p) for p in phones1 if extract_area_code(p)}
        ac2 = {extract_area_code(p) for p in phones2 if extract_area_code(p)}
        if ac1 & ac2:
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

        msg_emails = {m.message_id: get_message_emails(m) for m in messages}
        msg_phones = {m.message_id: get_message_phones(m) for m in messages}

        matching_pairs: List[Tuple[str, str]] = []
        for i, j in combinations(range(len(messages)), 2):
            sim = float(similarity_matrix[i, j])
            m1 = messages[i]
            m2 = messages[j]
            id1 = m1.message_id
            id2 = m2.message_id

            if sim >= self.similarity_threshold and self._identifiers_partially_match(
                m1, m2, msg_emails[id1], msg_emails[id2], msg_phones[id1], msg_phones[id2]
            ):
                matching_pairs.append((id1, id2))

        return self.build_clusters_from_pairs(message_ids, matching_pairs)
