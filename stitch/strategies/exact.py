import re
from typing import List, Set, Tuple, Optional
from itertools import combinations
from stitch.models import Message
from stitch.strategies.base import Stitcher

def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return f"1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return digits
    if len(digits) >= 7:
        return digits
    return None

def normalize_email(email: Optional[str]) -> Optional[str]:
    if not email:
        return None
    clean = email.strip().lower()
    if "@" not in clean:
        return None
    return clean

def extract_emails_from_text(text: str) -> Set[str]:
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    matches = re.findall(pattern, text)
    result = set()
    for m in matches:
        norm = normalize_email(m)
        if norm:
            result.add(norm)
    return result

def extract_phones_from_text(text: str) -> Set[str]:
    pattern = r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
    matches = re.findall(pattern, text)
    result = set()
    for m in matches:
        norm = normalize_phone(m)
        if norm:
            result.add(norm)
    return result

def get_message_emails(m: Message) -> Set[str]:
    emails = extract_emails_from_text(m.text)
    norm = normalize_email(m.sender_email)
    if norm:
        emails.add(norm)
    return emails

def get_message_phones(m: Message) -> Set[str]:
    phones = extract_phones_from_text(m.text)
    norm = normalize_phone(m.sender_phone)
    if norm:
        phones.add(norm)
    return phones

class ExactMatchStitcher(Stitcher):
    def partition(self, messages: List[Message]) -> List[Set[str]]:
        message_ids = [m.message_id for m in messages]
        matching_pairs: List[Tuple[str, str]] = []

        msg_emails = {m.message_id: get_message_emails(m) for m in messages}
        msg_phones = {m.message_id: get_message_phones(m) for m in messages}

        for m1, m2 in combinations(messages, 2):
            id1 = m1.message_id
            id2 = m2.message_id

            if msg_emails[id1] & msg_emails[id2]:
                matching_pairs.append((id1, id2))
                continue

            if msg_phones[id1] & msg_phones[id2]:
                matching_pairs.append((id1, id2))
                continue

        return self.build_clusters_from_pairs(message_ids, matching_pairs)
