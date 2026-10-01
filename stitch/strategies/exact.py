import re
from typing import List, Set, Tuple, Optional
from itertools import combinations
from stitch.models import Message
from stitch.strategies.base import Stitcher

def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        return None
    return digits

def normalize_email(email: Optional[str]) -> Optional[str]:
    if not email:
        return None
    clean = email.strip().lower()
    if "@" not in clean:
        return None
    return clean

class ExactMatchStitcher(Stitcher):
    def partition(self, messages: List[Message]) -> List[Set[str]]:
        message_ids = [m.message_id for m in messages]
        matching_pairs: List[Tuple[str, str]] = []

        for m1, m2 in combinations(messages, 2):
            e1 = normalize_email(m1.sender_email)
            e2 = normalize_email(m2.sender_email)
            if e1 and e2 and e1 == e2:
                matching_pairs.append((m1.message_id, m2.message_id))
                continue

            p1 = normalize_phone(m1.sender_phone)
            p2 = normalize_phone(m2.sender_phone)
            if p1 and p2 and p1 == p2:
                matching_pairs.append((m1.message_id, m2.message_id))
                continue

        return self.build_clusters_from_pairs(message_ids, matching_pairs)
