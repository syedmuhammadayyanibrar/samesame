from typing import List, Set, Tuple, Optional, Any, Union
from itertools import combinations
from stitch.models import Message, PermissionPolicy
from stitch.strategies.base import Stitcher
from stitch.strategies.exact import (
    normalize_email,
    normalize_phone,
    get_message_emails,
    get_message_phones
)

def get_policy_list(policy: Any, attr_name: str) -> List[str]:
    if policy is None:
        return []
    if isinstance(policy, dict):
        return policy.get(attr_name, [])
    return getattr(policy, attr_name, [])

class PermissionAwareStitcher(Stitcher):
    def __init__(self, wrapped_stitcher: Stitcher):
        self.wrapped_stitcher = wrapped_stitcher

    def is_message_blacklisted(self, message: Message) -> bool:
        policy = message.permission_policy
        if not policy:
            return False

        b_emails = {normalize_email(e) for e in get_policy_list(policy, "blacklist_emails") if normalize_email(e)}
        b_phones = {normalize_phone(p) for p in get_policy_list(policy, "blacklist_phones") if normalize_phone(p)}

        emails = get_message_emails(message)
        phones = get_message_phones(message)

        if emails & b_emails:
            return True
        if phones & b_phones:
            return True
        return False

    def is_message_whitelisted(self, message: Message) -> bool:
        policy = message.permission_policy
        if not policy:
            return False

        w_emails = {normalize_email(e) for e in get_policy_list(policy, "whitelist_emails") if normalize_email(e)}
        w_phones = {normalize_phone(p) for p in get_policy_list(policy, "whitelist_phones") if normalize_phone(p)}

        emails = get_message_emails(message)
        phones = get_message_phones(message)

        if emails & w_emails:
            return True
        if phones & w_phones:
            return True
        return False

    def get_unresolvable_message_ids(self, messages: List[Message]) -> Set[str]:
        return {m.message_id for m in messages if self.is_message_blacklisted(m)}

    def partition(self, messages: List[Message]) -> List[Set[str]]:
        unresolvable_ids = self.get_unresolvable_message_ids(messages)
        resolvable = [m for m in messages if m.message_id not in unresolvable_ids]

        if not resolvable:
            return [{m.message_id} for m in messages]

        base_clusters = self.wrapped_stitcher.partition(resolvable)

        whitelist_pairs: List[Tuple[str, str]] = []
        for m1, m2 in combinations(resolvable, 2):
            if self.is_message_whitelisted(m1) and self.is_message_whitelisted(m2):
                p1 = m1.permission_policy
                p2 = m2.permission_policy
                if p1 == p2:
                    whitelist_pairs.append((m1.message_id, m2.message_id))
                else:
                    e1 = get_message_emails(m1)
                    e2 = get_message_emails(m2)
                    ph1 = get_message_phones(m1)
                    ph2 = get_message_phones(m2)
                    w_emails1 = {normalize_email(e) for e in get_policy_list(p1, "whitelist_emails") if normalize_email(e)}
                    w_emails2 = {normalize_email(e) for e in get_policy_list(p2, "whitelist_emails") if normalize_email(e)}
                    w_phones1 = {normalize_phone(p) for p in get_policy_list(p1, "whitelist_phones") if normalize_phone(p)}
                    w_phones2 = {normalize_phone(p) for p in get_policy_list(p2, "whitelist_phones") if normalize_phone(p)}
                    if (e1 & e2 & (w_emails1 | w_emails2)) or (ph1 & ph2 & (w_phones1 | w_phones2)):
                        whitelist_pairs.append((m1.message_id, m2.message_id))

        if whitelist_pairs:
            existing_pairs: List[Tuple[str, str]] = []
            for cluster in base_clusters:
                c_list = list(cluster)
                for i in range(len(c_list)):
                    for j in range(i + 1, len(c_list)):
                        existing_pairs.append((c_list[i], c_list[j]))
            combined_pairs = existing_pairs + whitelist_pairs
            res_ids = [m.message_id for m in resolvable]
            merged_clusters = self.build_clusters_from_pairs(res_ids, combined_pairs)
        else:
            merged_clusters = base_clusters

        for u_id in unresolvable_ids:
            merged_clusters.append({u_id})

        return merged_clusters
