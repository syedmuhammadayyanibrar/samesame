import re
from difflib import SequenceMatcher
from typing import List, Set, Tuple, Optional
from itertools import combinations
from stitch.models import Message
from stitch.strategies.base import Stitcher
from stitch.strategies.exact import normalize_email, normalize_phone

def extract_domain(email: Optional[str]) -> Optional[str]:
    norm = normalize_email(email)
    if not norm or "@" not in norm:
        return None
    return norm.split("@", 1)[1]

def extract_area_code(phone: Optional[str]) -> Optional[str]:
    digits = normalize_phone(phone)
    if not digits:
        return None
    if len(digits) == 10:
        return digits[:3]
    if len(digits) == 11 and digits.startswith("1"):
        return digits[1:4]
    if len(digits) >= 10:
        return digits[:3]
    return None

def normalize_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    clean = re.sub(r"[^a-zA-Z\s]", "", name).strip().lower()
    return clean if clean else None

def names_partially_match(name1: Optional[str], name2: Optional[str]) -> bool:
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    if not n1 or not n2:
        return False
    if n1 == n2:
        return True
    tokens1 = set(n1.split())
    tokens2 = set(n2.split())
    if tokens1 and tokens2 and (tokens1.issubset(tokens2) or tokens2.issubset(tokens1)):
        return True
    ratio = SequenceMatcher(None, n1, n2).ratio()
    return ratio >= 0.75

def extract_self_identified_name(text: str) -> Optional[str]:
    patterns = [
        r"(?:this is|it's|its|i'm|im|name is)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        r"(?:thanks|cheers|regards|sincerely),?\s*\n*\s*([A-Za-z]+(?:\s+[A-Za-z]+)?)"
    ]
    stopwords = {"speaking", "calling", "from", "here", "again", "with", "at", "regarding", "about", "for", "and", "just", "checking"}
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1).strip()
            words = [w for w in raw.split() if w.lower() not in stopwords]
            if words:
                return " ".join(words)
    return None

class FuzzyMatchStitcher(Stitcher):
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

            d1 = extract_domain(m1.sender_email)
            d2 = extract_domain(m2.sender_email)
            if d1 and d2 and d1 == d2:
                matching_pairs.append((m1.message_id, m2.message_id))
                continue

            ac1 = extract_area_code(m1.sender_phone)
            ac2 = extract_area_code(m2.sender_phone)
            if ac1 and ac2 and ac1 == ac2:
                matching_pairs.append((m1.message_id, m2.message_id))
                continue

            name1 = m1.display_name or extract_self_identified_name(m1.text)
            name2 = m2.display_name or extract_self_identified_name(m2.text)
            if names_partially_match(name1, name2):
                matching_pairs.append((m1.message_id, m2.message_id))
                continue

        return self.build_clusters_from_pairs(message_ids, matching_pairs)
