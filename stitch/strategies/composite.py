from typing import List, Set, Tuple, Optional, Dict
from itertools import combinations
from stitch.models import Message, ContactMemory
from stitch.strategies.base import Stitcher
from stitch.strategies.exact import (
    ExactMatchStitcher,
    normalize_email,
    normalize_phone,
    get_message_emails,
    get_message_phones
)
from stitch.strategies.permission import PermissionAwareStitcher, get_policy_list
from stitch.strategies.a2a import A2AStitcher
from stitch.strategies.contact import ContactResolutionStitcher
from stitch.strategies.memory import MemoryStitcher

class CompositeStitcher(Stitcher):
    def __init__(
        self,
        fallback_stitcher: Optional[Stitcher] = None,
        enable_permission: bool = True,
        enable_contact: bool = True,
        enable_a2a: bool = True,
        enable_memory: bool = False,
        memories: Optional[List[ContactMemory]] = None
    ):
        self.fallback_stitcher = fallback_stitcher or ExactMatchStitcher()
        self.enable_permission = enable_permission
        self.enable_contact = enable_contact
        self.enable_a2a = enable_a2a
        self.enable_memory = enable_memory
        self.memories = memories or []

    def get_unresolvable_message_ids(self, messages: List[Message]) -> Set[str]:
        if self.enable_permission:
            pre_filter = PermissionAwareStitcher(self.fallback_stitcher)
            return pre_filter.get_unresolvable_message_ids(messages)
        return set()

    def _get_whitelist_pairs(self, messages: List[Message]) -> List[Tuple[str, str]]:
        if not self.enable_permission:
            return []

        pre_filter = PermissionAwareStitcher(self.fallback_stitcher)
        pairs: List[Tuple[str, str]] = []
        for m1, m2 in combinations(messages, 2):
            if pre_filter.is_message_whitelisted(m1) and pre_filter.is_message_whitelisted(m2):
                p1 = m1.permission_policy
                p2 = m2.permission_policy
                if p1 == p2:
                    pairs.append((m1.message_id, m2.message_id))
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
                        pairs.append((m1.message_id, m2.message_id))
        return pairs

    def _post_process_contacts(self, initial_clusters: List[Set[str]], resolvable: List[Message]) -> List[Set[str]]:
        msg_by_id: Dict[str, Message] = {m.message_id: m for m in resolvable}

        split_clusters: List[Set[str]] = []
        for cluster in initial_clusters:
            contacts_in_cluster = {
                msg_by_id[m_id].contact_id
                for m_id in cluster
                if msg_by_id[m_id].contact_id is not None
            }

            if len(contacts_in_cluster) <= 1:
                split_clusters.append(set(cluster))
            else:
                contact_sub_clusters: Dict[str, Set[str]] = {
                    c_id: set() for c_id in contacts_in_cluster
                }
                unassigned: Set[str] = set()

                for m_id in cluster:
                    c_id = msg_by_id[m_id].contact_id
                    if c_id is not None:
                        contact_sub_clusters[c_id].add(m_id)
                    else:
                        unassigned.add(m_id)

                for u_id in unassigned:
                    u_msg = msg_by_id[u_id]
                    u_emails = get_message_emails(u_msg)
                    u_phones = get_message_phones(u_msg)
                    matched_c_id = None

                    for c_id, c_set in contact_sub_clusters.items():
                        c_emails = set()
                        c_phones = set()
                        for cm_id in c_set:
                            c_emails |= get_message_emails(msg_by_id[cm_id])
                            c_phones |= get_message_phones(msg_by_id[cm_id])

                        if (u_emails & c_emails) or (u_phones & c_phones):
                            if matched_c_id is None:
                                matched_c_id = c_id
                            else:
                                matched_c_id = None
                                break

                    if matched_c_id is not None:
                        contact_sub_clusters[matched_c_id].add(u_id)
                    else:
                        split_clusters.append({u_id})

                for c_set in contact_sub_clusters.values():
                    if c_set:
                        split_clusters.append(c_set)

        contact_clusters: List[Set[str]] = []
        non_contact_clusters: List[Set[str]] = []

        for cluster in split_clusters:
            has_contact = any(msg_by_id[m_id].contact_id is not None for m_id in cluster)
            if has_contact:
                contact_clusters.append(set(cluster))
            else:
                non_contact_clusters.append(set(cluster))

        remaining_non_contact: List[Set[str]] = []
        for nc_cluster in non_contact_clusters:
            merged = False
            for m_id in list(nc_cluster):
                m = msg_by_id[m_id]
                m_emails = get_message_emails(m)
                m_phones = get_message_phones(m)

                for c_cluster in contact_clusters:
                    c_emails = set()
                    c_phones = set()
                    for cm_id in c_cluster:
                        c_emails |= get_message_emails(msg_by_id[cm_id])
                        c_phones |= get_message_phones(msg_by_id[cm_id])

                    if (m_emails & c_emails) or (m_phones & c_phones):
                        c_cluster.add(m_id)
                        merged = True
                        break
            if not merged:
                remaining_non_contact.append(nc_cluster)

        return contact_clusters + remaining_non_contact

    def partition(self, messages: List[Message]) -> List[Set[str]]:
        if not messages:
            return []

        unresolvable_ids = self.get_unresolvable_message_ids(messages)
        resolvable = [m for m in messages if m.message_id not in unresolvable_ids]

        if not resolvable:
            return [{m.message_id} for m in messages]

        res_ids = [m.message_id for m in resolvable]
        all_pairs: List[Tuple[str, str]] = []

        whitelist_pairs = self._get_whitelist_pairs(resolvable)
        all_pairs.extend(whitelist_pairs)

        if self.enable_contact:
            for m1, m2 in combinations(resolvable, 2):
                if m1.contact_id is not None and m2.contact_id is not None:
                    if m1.contact_id == m2.contact_id:
                        all_pairs.append((m1.message_id, m2.message_id))

        if self.enable_a2a:
            a2a_stitcher = A2AStitcher()
            all_pairs.extend(a2a_stitcher.get_a2a_pairs(resolvable))

        if self.enable_memory and self.memories:
            mem_stitcher = MemoryStitcher(memories=self.memories, enabled=True)
            all_pairs.extend(mem_stitcher.get_memory_pairs(resolvable))

        fallback_clusters = self.fallback_stitcher.partition(resolvable)
        for cluster in fallback_clusters:
            c_list = list(cluster)
            for i in range(len(c_list)):
                for j in range(i + 1, len(c_list)):
                    all_pairs.append((c_list[i], c_list[j]))

        initial_clusters = self.build_clusters_from_pairs(res_ids, all_pairs)

        if self.enable_contact:
            processed_clusters = self._post_process_contacts(initial_clusters, resolvable)
        else:
            processed_clusters = initial_clusters

        for u_id in unresolvable_ids:
            processed_clusters.append({u_id})

        return processed_clusters
