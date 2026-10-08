from typing import List, Set, Tuple, Optional, Any
from itertools import combinations
from stitch.models import Message
from stitch.strategies.base import Stitcher

def get_a2a_field(ctx: Any, field_name: str) -> Optional[str]:
    if ctx is None:
        return None
    if isinstance(ctx, dict):
        val = ctx.get(field_name)
    else:
        val = getattr(ctx, field_name, None)
    if val and str(val).strip():
        return str(val).strip()
    return None

class A2AStitcher(Stitcher):
    def __init__(self, fallback_stitcher: Optional[Stitcher] = None):
        self.fallback_stitcher = fallback_stitcher

    def get_a2a_pairs(self, messages: List[Message]) -> List[Tuple[str, str]]:
        pairs: List[Tuple[str, str]] = []
        for m1, m2 in combinations(messages, 2):
            if not m1.a2a_context or not m2.a2a_context:
                continue

            t1 = get_a2a_field(m1.a2a_context, "task_id")
            t2 = get_a2a_field(m2.a2a_context, "task_id")
            if t1 and t2 and t1 == t2:
                pairs.append((m1.message_id, m2.message_id))
                continue

            a1 = get_a2a_field(m1.a2a_context, "agent_handle")
            tgt1 = get_a2a_field(m1.a2a_context, "target_handle")
            a2 = get_a2a_field(m2.a2a_context, "agent_handle")
            tgt2 = get_a2a_field(m2.a2a_context, "target_handle")
            if a1 and tgt1 and a2 and tgt2:
                pair1 = frozenset([a1.lower(), tgt1.lower()])
                pair2 = frozenset([a2.lower(), tgt2.lower()])
                if pair1 == pair2:
                    pairs.append((m1.message_id, m2.message_id))
                    continue
        return pairs

    def partition(self, messages: List[Message]) -> List[Set[str]]:
        message_ids = [m.message_id for m in messages]
        a2a_pairs = self.get_a2a_pairs(messages)

        if self.fallback_stitcher:
            fallback_clusters = self.fallback_stitcher.partition(messages)
            fallback_pairs: List[Tuple[str, str]] = []
            for cluster in fallback_clusters:
                c_list = list(cluster)
                for i in range(len(c_list)):
                    for j in range(i + 1, len(c_list)):
                        fallback_pairs.append((c_list[i], c_list[j]))
            combined_pairs = fallback_pairs + a2a_pairs
            return self.build_clusters_from_pairs(message_ids, combined_pairs)

        return self.build_clusters_from_pairs(message_ids, a2a_pairs)
