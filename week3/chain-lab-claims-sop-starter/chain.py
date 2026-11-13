"""
chain.py - the prompt chain. Each step does ONE job and hands a checked result to the next.

  1 GUARD     remove instruction-like lines from the question and from the sections we retrieved
  2 RETRIEVE  find the best sections in the SOP (doc_store.search)
  3 EXTRACT   one model call: system message + extract template -> JSON {answer, citations, confidence}
  4 VERIFY    check every citation: the section exists and the quote really appears in it
  5 REFINE    if verification fails, call the model again with the problem described (up to max_retries)
  6 RENDER    produce the final markdown answer with sources (or a clear 'needs review')
"""
import json
import re

from doc_store import search
from injection import redact, wrap_untrusted

NOT_FOUND = "Not found in the document."


def render_template(template, values):
    """Replace {{name}} placeholders. A placeholder with no value is left as it is, so mistakes are easy to see."""
    for key, val in values.items():
        template = template.replace("{{" + key + "}}", str(val))
    return template


def render_examples(examples):
    return "\n\n".join(f"Example {i}\nQuestion: {e['question']}\nAnswer JSON: {e['answer_json']}" for i, e in enumerate(examples, 1))


def parse_json(text):
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except ValueError:
        return None


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def verify_citation(citation, by_id):
    """Return (True, "") when the cited section exists and the quote appears in it; otherwise (False, reason). Ignore case and extra spaces."""
    if not isinstance(citation, dict):
        return False, "a citation is not an object with 'section' and 'quote'"
    sec, quote = str(citation.get("section", "")).strip(), str(citation.get("quote", ""))
    if sec not in by_id:
        return False, f"section {sec!r} does not exist in the SOP"
    if not norm(quote):
        return False, f"the quote for {sec} is empty"
    if norm(quote) not in norm(by_id[sec]["text"]):
        return False, f"the quote for {sec} is not word for word from that section"
    return True, ""


def render_markdown(result):
    """Final answer for a person: the answer, then the sources (section id and quote), then a note if it needs review."""
    lines = ["**Answer:** " + result.get("answer", NOT_FOUND), ""]
    cites = result.get("citations") or []
    if cites:
        lines.append("**Sources:**")
        lines += [f"- [{c.get('section')}] \"{c.get('quote')}\"" for c in cites]
    else:
        lines.append("**Sources:** none")
    lines.append("")
    lines.append(f"Confidence: {result.get('confidence', 'low')}")
    if result.get("status") != "ok":
        lines.append("")
        lines.append("> **Needs review:** this answer could not be verified against the SOP. A claims executive must check the SOP before replying.")
    return "\n".join(lines)


def check_reply(obj, by_id, cfg):
    """All the code checks on one model reply. Returns a list of problems (empty = the reply passes)."""
    if obj is None:
        return ["the reply was not valid JSON"]
    problems = [f"the key {k!r} is missing" for k in cfg["json_keys"] if k not in obj]
    cites = obj.get("citations", [])
    if not isinstance(cites, list):
        return problems + ["'citations' must be a list"]
    answer = str(obj.get("answer", ""))
    if len(answer.split()) > cfg["max_answer_words"]:
        problems.append(f"the answer has more than {cfg['max_answer_words']} words")
    if answer.strip() == NOT_FOUND and cites:
        problems.append("a 'Not found in the document.' answer must have an empty citations list")
    if answer.strip() != NOT_FOUND and not cites and "answer" in obj:
        problems.append("an answer must cite at least one section, or be exactly 'Not found in the document.'")
    for c in cites:
        ok, why = verify_citation(c, by_id)
        if not ok:
            problems.append(why)
    return problems


def build_prompt(system_message, template, question, sections, examples, persona):
    context = "\n\n".join(f"[{s['id']}] {s['title']}\n{s['text']}" for s in sections)
    body = render_template(template, {"context": wrap_untrusted(context, "document"), "question": wrap_untrusted(question, "question"),
                                       "examples": render_examples(examples)})
    return render_template(system_message, persona) + "\n\n" + body


def run_chain(question, all_sections, ask, system_message, template, examples, cfg, case=None):
    by_id = {s["id"]: s for s in all_sections}
    clean_q = redact(question)                                                    # 1 GUARD
    found = search(clean_q, all_sections, cfg["retrieval_k"])                    # 2 RETRIEVE
    ctx = [dict(s, text=redact(s["text"])) for s in found]
    prompt = build_prompt(system_message, template, clean_q, ctx, examples, cfg["persona"])
    attempts, raw, obj, problems = 0, "", None, []
    while True:
        raw = ask(prompt, case)                                                  # 3 EXTRACT
        attempts += 1
        obj = parse_json(raw)
        problems = check_reply(obj, by_id, cfg)                                  # 4 VERIFY
        if not problems or attempts > cfg["max_retries"]:
            break
        prompt = prompt + "\n\nFEEDBACK:your last reply had problems: " + "; ".join(problems) + ". Fix them and answer again with JSON only."   # 5 REFINE
    if problems:
        result = dict(answer="Not found: the answer could not be verified against the SOP.", citations=[], confidence="low", status="needs_review")
    else:
        result = dict(answer=obj["answer"], citations=obj["citations"], confidence=obj.get("confidence", "low"), status="ok")
    result["attempts"], result["raw"] = attempts, raw
    result["markdown"] = render_markdown(result)                                 # 6 RENDER
    return result
