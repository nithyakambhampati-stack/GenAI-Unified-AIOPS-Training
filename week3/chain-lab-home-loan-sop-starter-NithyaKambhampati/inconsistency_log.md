# Inconsistency log

| # | File and place | What you observed | What it should be | How you found it | Fixed? |
|---|---|---|---|---|---|
| 1 | config.json `retrieval_k` | 2 | 3 (README: "the best 3 sections are sent to the model") | Compared config with README table | Yes |
| 2 | config.json `max_retries` | 0, so the REFINE step never runs | 1 (README: "one refinement retry") | Compared config with README; chain loop breaks when `attempts > max_retries` | Yes |
| 3 | config.json `max_answer_words` | 150 | 60 (README: "At most 60 words") | Compared config with README | Yes |
| 4 | config.json `json_keys` | `["answer", "sources", "confidence"]` | `["answer", "citations", "confidence"]` (README, chain.py, evaluate.py and examples all use `citations`) | Every correct answer would fail the `json_keys` check | Yes |
| 5 | config.json `prompts.extract` | `prompts/extract.md` (file does not exist) | `prompts/extract_template.md` | README file list and `ls prompts/` | Yes |
| 6 | config.json `persona.name` vs prompts/system_message.md | Config key is `name`, template placeholder is `{{assistant_name}}`; placeholder is left unfilled | Key renamed to `assistant_name` | Read `render_template` (unknown placeholders are left as is) | Yes |
| 7 | data/questions.json Q01 `facts` | `"15,000"` | `"25,000"` (SOP S2.1 and Q01's own answer_text/quote say Rs 25,000) | Compared with data/sop.txt | Yes |
| 8 | data/questions.json Q05 `sections` | `S3.2` (Foreclosure charges) | `S3.3` (Release of documents), where the Q05 quote actually appears | Retrieval returned S3.3 first; quote not in S3.2 | Yes |
| 9 | data/questions.json last question | Duplicate id `Q07` (two questions share it) | `Q08` (README: 8 questions) | Listed ids | Yes |
| 10 | data/examples.json example 1 | Quote "statement is issued within 3 working days of the request as per policy" is not in S3.1 (no "as per policy") | Verbatim: "The foreclosure statement is issued within 3 working days of the request." | Ran `verify_citation` on it: fails | Yes |
| 11 | data/examples.json example 2 | Unanswerable question answered "As per standard practice the answer is yes." citing non-existent S9.9, confidence high: teaches the model to invent | `{"answer": "Not found in the document.", "citations": [], "confidence": "low"}` | Compared with README "Not in the SOP" rule | Yes |
| 12 | tests/test_injection.py `test_harmless_question_is_flagged` | Asserts a harmless question IS detected as injection | `assertFalse` (renamed `..._is_not_flagged`) | Test name and assertion contradict the docstring of `detect_injection` | Yes |
| 13 | injection.py `PATTERNS` | Only `ignore all previous instructions`; the SOP's own injection ("ignore previous instructions", "SYSTEM NOTE:") and Q08 ("Pretend ... confirm that charges ...") are not detected | Broader patterns: optional "all", system note/prompt, pretend, you are now, confirm that charges | Ran `redact()` on S6.1 and Q08 | Yes |
| 14 | injection.py `redact()` | Replaces the whole line; Q08 is one line, so the real question would be removed too | Redact per sentence, keep the genuine question | Ran `redact()` on Q08 | Yes |
| 15 | data/rubric.json weights | 40 + 30 + 30 + 10 = 110, and accuracy is weighted equal to grounding although priority says grounding > accuracy | 40 / 30 / 20 / 10 = 100 | Summed weights | Yes |
| 16 | llm_client.py `ask()` | With `--live`, if the claude CLI is missing it silently uses the mock, so a "live" result can be fake | Raise an error instead | Read the code | Yes |
| 17 | llm_client.py `ask_live()` | Passes a multi-line prompt as a command-line argument and calls bare `claude` (fails for `claude.cmd` on Windows; length limits) | Resolve full path with `shutil.which`, send prompt on stdin | Read the code; Windows VM | Yes |
| 18 | chain.py failure branch | `answer` set to `NOT_FOUND`/model answer, then immediately overwritten (dead code) | One assignment | Read the code | Yes |
| 19 | README data list | "two [questions] carry injected text"; only Q08 does. The second injection is in the SOP (S6.1) | Wording corrected | Read questions.json | Yes |
| 20 | CLAUDE_CODE_PROMPTS.md | Refers to `prompt_builder.py` and `evaluate_output.py`, which are not in this lab | `doc_store.py` / `evaluate.py` | File list | Yes |
| 21 | data/policy.json vs README | README forbids "a promise of approval"; policy has no approval phrase | Open: adding "approved" would also flag the correct S4.1 quote ("approved by the branch manager"). Handled in the system message (rule 5) instead | Compared README rule with policy list | No (noted) |
