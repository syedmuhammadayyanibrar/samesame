from typing import List, Set, Tuple, Optional, Dict
from itertools import combinations
from stitch.models import Message
from stitch.strategies.base import Stitcher
from stitch.strategies.exact import (
    ExactMatchStitcher,
    get_message_emails,
    get_message_phones
)

class ContactResolutionStitcher(Stitcher):
    def __init__(self, fallback_stitcher: Optional[Stitcher] = None):
        self.fallback_stitcher = fallback_stitcher or ExactMatchStitcher()

    def partition(self, messages: List[Message]) -> List[Set[str]]:
        if not messages:
            return []

        message_ids = [m.message_id for m in messages]
        msg_by_id: Dict[str, Message] = {m.message_id: m for m in messages}

        contact_pairs: List[Tuple[str, str]] = []
        for m1, m2 in combinations(messages, 2):
            if m1.contact_id is not None and m2.contact_id is not None:
                if m1.contact_id == m2.contact_id:
                    contact_pairs.append((m1.message_id, m2.message_id))

        fallback_clusters = self.fallback_stitcher.partition(messages)
        fallback_pairs: List[Tuple[str, str]] = []
        for cluster in fallback_clusters:
            c_list = list(cluster)
            for i in range(len(c_list)):
                for j in range(i + 1, len(c_list)):
                    fallback_pairs.append((c_list[i], c_list[j]))

        all_pairs = fallback_pairs + contact_pairs
        initial_clusters = self.build_clusters_from_pairs(message_ids, all_pairs)

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

        final_clusters: List[Set[str]] = []
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
