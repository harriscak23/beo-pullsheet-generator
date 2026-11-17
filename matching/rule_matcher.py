import json
from pathlib import Path

from rapidfuzz import fuzz, process

from extraction.beo_parser import normalize_name

RULES_PATH = Path(__file__).resolve().parent.parent / "rules" / "rules.json"

# Scores are 0-100. At or above this, a fuzzy result counts as a match.
# Below it, the best candidate is still reported so it can be reviewed.
MATCH_THRESHOLD = 75


def load_rules(path=RULES_PATH):
    """Load rules.json and return the list of menu item rules."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)["menu_items"]


def match_menu_item(normalized_name, rules):
    """
    Find the rules.json entry that best matches one normalized menu item name.

    Returns a dict:
        rule    - the matched rule dict (or None if the name is empty)
        score   - rapidfuzz similarity, 0-100
        status  - "exact", "fuzzy" (score >= MATCH_THRESHOLD) or "no match"
    """
    if not normalized_name or not rules:
        return {"rule": None, "score": 0.0, "status": "no match"}

    rule_names = [normalize_name(rule["name"]) for rule in rules]

    # Exact match on the normalized name wins outright.
    if normalized_name in rule_names:
        index = rule_names.index(normalized_name)
        return {"rule": rules[index], "score": 100.0, "status": "exact"}

    # token_sort_ratio ignores word order but, unlike partial/WRatio scorers,
    # does not let a short rule like "bar" score 100 inside a longer name.
    _, score, index = process.extractOne(
        normalized_name, rule_names, scorer=fuzz.token_sort_ratio
    )
    status = "fuzzy" if score >= MATCH_THRESHOLD else "no match"
    return {"rule": rules[index], "score": score, "status": status}


def match_menu_selections(menu_items, rules=None):
    """Attach a "match" result to each parsed menu item."""
    if rules is None:
        rules = load_rules()

    results = []
    for item in menu_items:
        name = item.get("normalized_name") or normalize_name(item.get("name"))
        results.append({**item, "match": match_menu_item(name, rules)})
    return results


def print_match_report(matched_items):
    """Print each menu item next to the rules.json entry it was compared to."""
    print("=== MENU ITEM MATCHES (rules.json) ===")
    print()

    if not matched_items:
        print("  (no menu items)")
        return

    for item in matched_items:
        match = item["match"]
        rule = match["rule"]
        rule_name = rule["name"] if rule else "(none)"

        print(f"- {item['name']}")
        print(f"  Normalized: {item.get('normalized_name')}")
        print(f"  Compared to: {rule_name}")
        print(f"  Score: {match['score']:.1f}  [{match['status'].upper()}]")
        print()

    counts = {"exact": 0, "fuzzy": 0, "no match": 0}
    for item in matched_items:
        counts[item["match"]["status"]] += 1
    print(
        f"Summary: {counts['exact']} exact, {counts['fuzzy']} fuzzy, "
        f"{counts['no match']} no match (threshold {MATCH_THRESHOLD})"
    )
