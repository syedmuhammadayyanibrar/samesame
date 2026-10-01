from typing import List, Dict, Tuple, Any
from itertools import combinations
from sklearn.metrics import cohen_kappa_score
from stitch.models import Scenario

def extract_pairwise_links(message_ids: List[str], cluster_map: Dict[str, str]) -> List[int]:
    pairs = list(combinations(message_ids, 2))
    links = []
    for m1, m2 in pairs:
        c1 = cluster_map.get(m1)
        c2 = cluster_map.get(m2)
        if c1 is not None and c2 is not None and c1 == c2:
            links.append(1)
        else:
            links.append(0)
    return links

def compute_dataset_kappa(
    scenarios: List[Scenario],
    second_pass_data: Dict[str, Dict[str, str]]
) -> Tuple[float, Dict[str, float], List[str]]:
    all_annotator_1 = []
    all_annotator_2 = []
    per_scenario_kappa = {}
    flagged_scenarios = []

    for scenario in scenarios:
        s_id = scenario.scenario_id
        if s_id not in second_pass_data:
            continue
        
        message_ids = [m.message_id for m in scenario.messages]
        ann1_map = {m.message_id: m.true_identity_id for m in scenario.messages if m.true_identity_id is not None}
        ann2_map = second_pass_data[s_id]

        links1 = extract_pairwise_links(message_ids, ann1_map)
        links2 = extract_pairwise_links(message_ids, ann2_map)

        all_annotator_1.extend(links1)
        all_annotator_2.extend(links2)

        if len(set(links1)) <= 1 and len(set(links2)) <= 1:
            if links1 == links2:
                s_kappa = 1.0
            else:
                s_kappa = 0.0
        else:
            s_kappa = float(cohen_kappa_score(links1, links2))
        
        per_scenario_kappa[s_id] = s_kappa
        if s_kappa < 0.80:
            flagged_scenarios.append(s_id)

    overall_kappa = float(cohen_kappa_score(all_annotator_1, all_annotator_2))
    return overall_kappa, per_scenario_kappa, flagged_scenarios
