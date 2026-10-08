from typing import List, Set, Tuple, Optional, Dict
from itertools import combinations
import numpy as np
from stitch.models import Message, ContactMemory
from stitch.strategies.base import Stitcher
from stitch.strategies.exact import (
    ExactMatchStitcher,
    get_message_emails,
    get_message_phones
)

class MemoryStitcher(Stitcher):
    def __init__(
        self,
        memories: Optional[List[ContactMemory]] = None,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.60,
        fallback_stitcher: Optional[Stitcher] = None,
        enabled: bool = False
    ):
        self.memories = memories or []
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.fallback_stitcher = fallback_stitcher or ExactMatchStitcher()
        self.enabled = enabled
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def get_memory_pairs(self, messages: List[Message]) -> List[Tuple[str, str]]:
        if not self.enabled or not self.memories or not messages:
            return []

        model = self._get_model()
        mem_texts = [mem.text for mem in self.memories]
        msg_texts = [m.text for m in messages]

        mem_embeddings = model.encode(mem_texts, normalize_embeddings=True)
        msg_embeddings = model.encode(msg_texts, normalize_embeddings=True)

        sim_matrix = np.dot(msg_embeddings, mem_embeddings.T)

        memory_matched_messages: Dict[str, Set[str]] = {
            mem.memory_id: set() for mem in self.memories
        }

        for i, msg in enumerate(messages):
            msg_emails = get_message_emails(msg)
            msg_phones = get_message_phones(msg)
            msg_tokens = set(msg.text.lower().split())

            for j, mem in enumerate(self.memories):
                sim = float(sim_matrix[i, j])
                if sim < self.similarity_threshold:
                    continue

                citation_match = False
                for cit in mem.citations:
                    c_clean = cit.strip().lower()
                    if c_clean in msg_emails or c_clean in msg_phones:
                        citation_match = True
                        break
                    if msg.contact_id and c_clean == msg.contact_id.lower():
                        citation_match = True
                        break
                    if c_clean in msg_tokens or c_clean in msg.text.lower():
                        citation_match = True
                        break

                if citation_match:
                    memory_matched_messages[mem.memory_id].add(msg.message_id)

        pairs: List[Tuple[str, str]] = []
        for mem_id, msg_set in memory_matched_messages.items():
            if len(msg_set) >= 2:
                for m1, m2 in combinations(list(msg_set), 2):
                    pairs.append((m1, m2))

        return pairs

    def partition(self, messages: List[Message]) -> List[Set[str]]:
        message_ids = [m.message_id for m in messages]
        fallback_clusters = self.fallback_stitcher.partition(messages)

        if not self.enabled or not self.memories:
            return fallback_clusters

        mem_pairs = self.get_memory_pairs(messages)
        if not mem_pairs:
            return fallback_clusters

        fallback_pairs: List[Tuple[str, str]] = []
        for cluster in fallback_clusters:
            c_list = list(cluster)
            for i in range(len(c_list)):
                for j in range(i + 1, len(c_list)):
                    fallback_pairs.append((c_list[i], c_list[j]))

        all_pairs = fallback_pairs + mem_pairs
        return self.build_clusters_from_pairs(message_ids, all_pairs)
