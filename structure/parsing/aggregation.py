
import json
from collections import Counter, defaultdict
from typing import Dict, List, Set

def parse(parsed_results):
    # Group the JSONs by their key sets
    grouped_by_keys = group_by_key_sets(parsed_results)

    # Merge JSONs with the same keys based on the most common values
    merged_results = {}
    for key_set, results in grouped_by_keys.items():
        merged_results[frozenset(key_set)] = merge_jsons(results)

    # Return the merged results as a JSON object
    return json.dumps(merged_results)

def group_by_key_sets(parsed_results):
    grouped_by_keys = defaultdict(list)
    for result in parsed_results:
        key_set = frozenset(result["results"].keys())
        grouped_by_keys[key_set].append(result)
    return grouped_by_keys

def merge_jsons(parsed_results):
    # Count the occurrences of each value for each key
    counters = {}
    for result in parsed_results:
        for key, value in result["results"].items():
            if key not in counters:
                counters[key] = Counter()
            counters[key][value] += 1

    # Merge the JSONs based on the most common values
    merged_results = {}
    for key, counter in counters.items():
        most_common_value, _ = counter.most_common(1)[0]
        merged_results[key] = most_common_value

    return merged_results
