"""Score one model output against the rules for its task. Each check returns True or False.

The score for a case is the share of its checks that pass (0 to 1).
"""
import json
import re


def parse_json(text):
    """Return the first JSON object found in the text, or None."""
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def word_count(text):
    return len(text.split()) + text.count(",")


def check_classification(output, label, cfg):
    """t1. Compares category, severity and escalate with the label, ignoring case."""
    data = parse_json(output)
    if data is None:
        return {"valid_json": False, "allowed_category": False, "category": False, "severity": False, "escalate": False}
    return {
        "valid_json": True,
        "allowed_category": str(data.get("category", "")).lower() in {
            value.lower() for value in cfg["allowed_categories"]
        },
        "category": str(data.get("category", "")).lower() == str(label["category"]).lower(),
        "severity": str(data.get("severity", "")).lower() == str(label["severity"]).lower(),
        "escalate": data.get("escalate") == label["escalate"],
    }


def check_reply(output, case, cfg):
    """t2. Word limit, no forbidden phrases, quotes the reference, states the timeline, no full card number."""
    low = output.lower()
    return {
        "word_limit": word_count(output) <= cfg["reply"]["word_limit"],
        "no_forbidden_phrase": not any(p in low for p in cfg["reply"]["forbidden_phrases"]),
        "quotes_reference": case["complaint_ref"] in output,
        "states_timeline": case["timeline"].lower() in low,
        "no_full_card_number": re.search(r"(\d[ -]?){13,19}", output) is None,
    }


def numbers_in(text):
    """Numbers as they appear, commas removed: 'Rs 1,50,000' -> '150000'."""
    return {n.replace(",", "") for n in re.findall(r"(?<![A-Za-z0-9])\d[\d,]*", text)}


def check_summary(output, snippet, cfg):
    """t3. Valid JSON, all fields present, correct source id, every number grounded in the policy text."""
    data = parse_json(output)
    if data is None:
        return {"valid_json": False, "fields": False, "source_id": False, "numbers_grounded": False}
    answer_numbers = numbers_in(" ".join(str(v) for v in data.values() if v is not None))
    policy_numbers = numbers_in(snippet["text"])
    return {
        "valid_json": True,
        "fields": all(f in data for f in cfg["summary_fields"]),
        "source_id": data.get("source_id") == snippet["id"],
        "numbers_grounded": answer_numbers <= policy_numbers,
    }


def score(result):
    """Share of checks passed, 0 to 1."""
    return sum(result.values()) / len(result)
