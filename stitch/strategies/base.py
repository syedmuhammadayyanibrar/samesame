from abc import ABC, abstractmethod
from typing import List, Set, Tuple, Dict
from stitch.models import Message

class Stitcher(ABC):
    @abstractmethod
    def partition(self, messages: List[Message]) -> List[Set[str]]:
        pass

    def stitch(self, messages: List[Message]) -> List[Set[str]]:
        return self.partition(messages)

    @staticmethod
    def build_clusters_from_pairs(message_ids: List[str], pairs: List[Tuple[str, str]]) -> List[Set[str]]:
        parent = {m: m for m in message_ids}

        def find(item: str) -> str:
            path = []
            while parent[item] != item:
                path.append(item)
                item = parent[item]
            for node in path:
                parent[node] = item
            return item

        def union(item1: str, item2: str) -> None:
            root1 = find(item1)
            root2 = find(item2)
            if root1 != root2:
                parent[root2] = root1

        for m1, m2 in pairs:
            if m1 in parent and m2 in parent:
                union(m1, m2)

        clusters_dict: Dict[str, Set[str]] = {}
        for m in message_ids:
            root = find(m)
            if root not in clusters_dict:
                clusters_dict[root] = set()
            clusters_dict[root].add(m)

        return list(clusters_dict.values())

    @staticmethod
    def clusters_to_map(clusters: List[Set[str]]) -> Dict[str, str]:
        mapping = {}
        for idx, cluster in enumerate(clusters):
            cluster_id = f"c_{idx}"
            for m_id in cluster:
                mapping[m_id] = cluster_id
        return mapping
