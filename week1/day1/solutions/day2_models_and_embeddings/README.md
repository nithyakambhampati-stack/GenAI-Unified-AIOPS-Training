# Day 2 - Model tiers, embeddings and verification

Three ideas: (1) models differ in quality, speed and cost, so **choose a tier on evidence**; (2) text can be turned into
numbers that capture **meaning**; (3) a fluent answer is not a verified answer.

## Files

| File | Role |
|---|---|
| `compare_tiers_cli.py` | **In-lab.** Same query to Opus / Sonnet / Haiku via Claude Code CLI; table + markdown report |
| `verify_outputs.py` | Propose -> verify -> tier -> human decides -> log. `--offline-demo` needs no key |
| `embeddings_map.py` | Embeddings, cosine similarity, semantic search, 2-D map. Real model (fastembed) or offline toy embedder |
| `redact_pii.py` | Pattern-based PII redaction and its limits |
| `homework_pack.py` | **Homework.** Prints the identical prompt and creates a comparison sheet for ChatGPT, Claude.ai, Gemini |
| `data/vendor_clause.txt` | Fictional contract extract |
| `data/queries.json` | The standard query (Q1) with reference answers, plus two extras |
| `data/sentences.json` | 16 sentences on 4 topics for the embeddings demo |
| `data/approved_tools.json` | EXAMPLE approved-tools table (replace with your organisation's policy) |

## In-lab: compare tiers through Claude Code CLI

```bash
python solutions/day2_models_and_embeddings/compare_tiers_cli.py --dry-run     # see the exact commands first
python solutions/day2_models_and_embeddings/compare_tiers_cli.py               # Q1 on opus, sonnet, haiku
python solutions/day2_models_and_embeddings/compare_tiers_cli.py --query Q3    # a judgement question
python solutions/day2_models_and_embeddings/compare_tiers_cli.py --prompt "your own question"
```

Each tier is called as `claude -p --model <tier> --output-format json --max-turns 1 --tools ""` so it is a clean
"model only" test. Output: seconds, cost, tokens, the model that actually answered, and an automatic check for the key numbers
(620 and 24,800 for Q1). The report `outputs/tier_comparison_Q1.md` has a scoring table for you to fill in.

Reference answers for Q1: credit **620.00** (0.9 points below target = 1 full 0.5-point step = 5% of 12,400); termination
charge **24,800.00**; **No** - clause 11.4 requires prior written consent outside the EEA.

Questions to answer: Did every tier get all three parts right? Did they respect the 150-word limit? What did the cheapest
correct answer cost versus the most expensive? For which tasks would you choose each tier?

## Embeddings and semantic search

```bash
python solutions/day2_models_and_embeddings/embeddings_map.py --toy     # offline, 6-number vectors you can read
pip install -r requirements-embeddings.txt                              # once, for the real model
python solutions/day2_models_and_embeddings/embeddings_map.py           # real 384-number vectors
```
Open `outputs/embedding_map.png`. Queries find the right topic even with almost no shared words
(for example "Reimburse me for the defective goods" finds the refund sentences).

## Verification

```bash
python solutions/day2_models_and_embeddings/verify_outputs.py --offline-demo   # two deliberate errors -> HIGH risk
python solutions/day2_models_and_embeddings/verify_outputs.py                  # live: the model extracts, code verifies
```
Each run appends a line to `outputs/verification_audit.jsonl`.

## Homework (no API key, no code)

```bash
python solutions/day2_models_and_embeddings/homework_pack.py
```
Paste the printed prompt into **ChatGPT, Claude.ai and Gemini** (new chat each, identical text, synthetic data only),
then fill in `outputs/homework_comparison.md`. Also find, in each app, the setting that controls whether your chats
are used to improve the model, and note whether your account is personal or enterprise.

## Take-home

See `docs/assignments/Day2_Take_Home_Assignment.docx`.
