# Day 2 take-home - model tiers, embeddings and verification

All data is synthetic. No `.env` or API key is included. Evidence is in `outputs/` and `outputs/day2_runs/`.

> **Status:** Parts C, D and E are complete. **Part A** and the Claude-tier half of **Part B** need the programme API
> key (`compare_tiers_cli.py` calls Claude Code CLI); the consumer-app half of Part B (ChatGPT, Claude.ai, Gemini in a
> browser, plus their privacy settings) has to be done by hand. Those sections are marked **[PENDING]**.
> Commands: `README_DAY2.md`.

---

## Part A - Tier study [PENDING LIVE RUN]

Commands: `python solutions/day2_models_and_embeddings/compare_tiers_cli.py --query Q1` (then `Q2`, `Q3`). Reports go to
`outputs/tier_comparison_Q1.md`, `_Q2.md`, `_Q3.md`. Correctness is judged by me against the reference answers, not
only by the automatic number check.

Reference answers used for marking:
* **Q1** (vendor clause): credit for 98.6% availability = **620.00** (one full 0.5-point step x 5% x 12,400.00, under the
  20% cap); termination after 8 months = **24,800.00** (two months' fees, inside the first 12 months); 3 marks.
* **Q2** (2-sentence executive summary): must mention the 12,400.00 monthly fee, service credits capped at 20%, and the
  early-termination charge; no invented terms; 2 sentences.
* **Q3** (judgement, max 80 words): three real risks (personal data leaves our control / consumer terms and training
  use / breach of data-protection law or client contract) and one safer alternative (enterprise tool or redacted /
  synthetic data).

| Query | Tier | Correct? (0-3) | Seconds | Cost ($) | Followed length limit? | Notes |
|---|---|---|---|---|---|---|
| Q1 | opus | | | | | |
| Q1 | sonnet | | | | | |
| Q1 | haiku | | | | | |
| Q2 | opus | | | | | |
| Q2 | sonnet | | | | | |
| Q2 | haiku | | | | | |
| Q3 | opus | | | | | |
| Q3 | sonnet | | | | | |
| Q3 | haiku | | | | | |

**Recommendation per task type:** [PENDING - to be written from the table: tier for extraction with arithmetic,
for summarisation, for judgement, with the evidence.]

---

## Part B - My own query across six tools

**Query** (`solutions/day2_models_and_embeddings/data/own_query_term_deposit.txt`): about 150 words of synthetic
term-deposit premature-closure terms (clauses 3.1-3.5 and a rate card) and three questions with known answers,
written before running anything (`data/own_query_answers.md`):

1. 200,000.00 booked for 2 years, closed after 120 days → **4.50%** (5.25% card rate for 91-180 days minus 0.75).
   The trap: using the booked 2-year rate (6.75% → 6.00%), which clause 3.3 rules out.
2. Take 50,000.00 out of 300,000.00 → **No**, partial withdrawal is not allowed (3.5).
3. 600,000.00 closed on day 5 → **no interest** (3.2) and **branch manager** approval (3.4).

Redaction check: `redact_pii.py --file ...` found nothing (`outputs/day2_runs/partB_redaction_check.txt`). It only
recognises patterns such as emails, phone and card numbers, so I also read the text myself: no names or personal data.

**Claude tiers** [PENDING LIVE RUN]: `compare_tiers_cli.py --prompt "<contents of the file>"` →
`outputs/tier_comparison_custom.md`.

**Consumer apps** [PENDING - to do by hand]: the lab's Q1 prompt (printed by `homework_pack.py`, saved in
`outputs/day2_runs/partB_homework_pack.txt`) in ChatGPT, Claude.ai and Gemini, each in a **new chat** with identical
text. Fill in `outputs/homework_comparison.md`: model and plan shown, correctness, length limit, time, anything added
that is not in the source.

**Training-data settings** [PENDING - check in each account and record what you actually see]:

| Tool | Where to look | Default I found | Account type (personal / enterprise) |
|---|---|---|---|
| ChatGPT | Settings → Data controls → the "improve the model" toggle | | |
| Claude.ai | Settings → Privacy → the "help improve Claude" setting | | |
| Gemini | Gemini Apps Activity (activity / "keep activity") setting | | |

Menu names change often, so the "where to look" column is a starting point. Record the exact path and default you see.

**Trust analysis (8-12 sentences)** [PENDING - written after the runs].

---

## Part C - Embeddings experiment

**New topic: `facilities`** - 8 synthetic office-facilities requests (broken air conditioning, meeting-room
reservation, flickering light, faulty bike-gate lock, leaking water cooler, extra chairs, lift out of service, spare
desk key) added to `data/sentences.json`.

**Bug found and fixed first.** `plot_map()` paired topics with a 4-colour palette using `zip()`, which stops at the
shorter list, so **a fifth topic was silently left off the map**: the data was embedded but never drawn. The palette
now has 8 colours and the function raises an error instead of dropping topics if there are ever more.

**Toy vs real map.** Toy map: `outputs/embedding_map_toy.png` (log: `outputs/day2_runs/partC_toy.txt`). The real model
(fastembed bge-small) could not run on this machine: the package is installed but `onnxruntime` fails to load its DLL
(`DLL load failed while importing onnxruntime_pybind11_state`, the Microsoft Visual C++ runtime is missing), and the
script falls back to the toy embedder (`outputs/day2_runs/partC_real_attempt.txt`). **[PENDING: real map once the
runtime is installed, or on another machine.]** On the toy map the four original topics form tight groups, but
`facilities` is **scattered**: some points sit among `refunds`, two sit near `hr_leave`, the rest in between. That is
what the toy design predicts: none of its six word groups (money, delivery, damage, access, leave, security) is about
buildings, so a facilities sentence is placed by the few group words it happens to contain ("broken", "faulty" →
damage) plus small checksum "nudges" for every unknown word.

**Where the toy embedder fails** (`--query`, a new option I added so you can try your own queries):

| Query | Toy top match | Why, in terms of the six word groups |
|---|---|---|
| "Book a room for the team workshop" | `hr_leave` - "I need to **book** a holiday..." (0.99) | "book" is in the **leave** group, and nothing else in the query is in any group. The toy reads it as a leave request. A real model knows "book a room" is about space, not time off. |
| "Reimburse me for the defective goods" (built-in) | `facilities` - "...the **faulty** lock on the bike storage gate" (0.96), refunds 2nd (0.90) | "defective" and "faulty" are both in the **damage** group; the facilities sentence has almost nothing else, so it points almost purely at "damage", as does half the query. Adding my topic changed the answer to an existing query. |
| "The radiator by my seat is stone cold" | `facilities` - "We need six extra chairs..." (0.99) | Looks like a success, but it is luck: no word is in any group, so both vectors are made only of checksum nudges, and the "best match" is about chairs. |

**Test.** The course test that checked "Reimburse me for the defective goods" → refunds as the top hit now fails, for the
reason above. I changed it to require refunds in the **top two**, with a comment explaining why, rather than editing my
data to hide the effect. I added:
`test_facilities_topic_added`; `test_toy_embedder_sends_a_room_booking_to_leave` (pins the documented failure);
and `test_facilities_synonym_query_with_real_model`, the actual synonym check ("Book a room for the team workshop" →
facilities). **It is skipped when fastembed cannot load**, as here. Why I did not write a toy-embedder synonym test for
`facilities`: the toy has no facilities word group, so any toy "success" for a synonym query comes from checksum
nudges (see the radiator row), and the test would pass or fail by accident, not because of meaning.

**What distance on the map means, and why the axes have no meaning.** Each sentence is really a point in 6
dimensions (toy) or 384 (real model); the map squeezes them onto 2 axes with PCA, keeping the two directions in
which the points differ most. Two dots close together therefore have similar vectors, so the embedder considers
them similar in meaning, while dots far apart are less similar. But the squeeze loses information, so two points
that look close in 2-D can still be far apart in the full space, and only the original cosine scores should be
trusted. The axes are new directions that PCA calculates from *this* set of sentences: each is a weighted mix of all
the original dimensions, and the mix changes as soon as you add or remove sentences (adding `facilities` changed the
whole picture). So "axis 1" has no fixed meaning and no units; only the relative positions matter.

---

## Part D - Extending the verification pipeline

**New item:** `late_interest_pct_month` = **1.5** (clause 4.2), added to `EXTRACT_SYSTEM`, `ground_truth()`,
`NUMBER_IN_QUOTE` and the offline reply (with a correct quote, so the demo's deliberate errors are still the only
ones).

**Three weaknesses found while adding it** (demonstrated on the unchanged code in
`outputs/day2_runs/partD_weaknesses_before_fix.txt`):

1. **Rounding:** the number forms tried for 1.5 were `['1.5', '1.50', '2']`. The whole-number forms are now used only
   for whole numbers.
2. **Number inside another number:** "5" counted as found inside "interest at **1.5**% per month", so a quote from
   the late-payment clause passed as evidence for the 5% service-credit step. The check now requires the number to
   stand on its own (not preceded or followed by other digits).
3. **Unsupported numbers did not raise the risk:** a real quote that does not contain the number set
   `number_in_quote = False`, but `risk_tier()` ignored that field, so the run still came out **LOW**. It now gives
   **HIGH** ("a quote is real but does not support its number").

**My extra check - quote must come from the right clause.** `SOURCE_CLAUSE` maps each item to its clause (fee → 4.1,
interest → 4.2, credits → 7.1, termination → 9.2); `split_clauses()` cuts the contract at each clause number, and
`verify()` adds `right_clause`. A real sentence from the wrong clause is not evidence, so it gives **HIGH**. The
results table has a new "right clause" column.

**Tests** (`tests/test_day2.py`): new item correct → **LOW**; invented interest quote → **HIGH**; real quote but
wrong number → **HIGH**; 1.5 never tried as "2"; "5" not found inside "1.5%" and "20" not inside "12,400.00"; real
quote from the wrong clause → **HIGH**; unsupported number → **HIGH**; clauses split as 4.1/4.2/7.1/9.2/11.4.
Day 2 suite: **28 tests, OK, 1 skipped** (the real-model embedding test).

**Offline demo** (`outputs/day2_runs/partD_offline_demo.txt`):

```
item                           model  expected  quote exists  right clause  number in quote  value ok
monthly_fee                    12400     12400  yes          yes          yes              yes
late_interest_pct_month          1.5       1.5  yes          yes          yes              yes
credit_percent_per_step            5         5  yes          yes          yes              yes
credit_cap_percent                25        20  NO           NO           yes              NO
credit_for_98_6                 1240       620  yes          yes          n/a              NO
termination_charge_8m          24800     24800  yes          yes          n/a              yes
RISK TIER: HIGH
```
Audit line: `{"source": "offline-demo", "tier": "HIGH", "failed_items": ["credit_cap_percent", "credit_for_98_6"]}`

**Live mode** [PENDING LIVE RUN]: `python solutions/day2_models_and_embeddings/verify_outputs.py` → paste the table
and the new audit line here.

**If the model had silently left out clause 9.2, what would catch it?** For the items we *ask* for, the pipeline
already catches a missing item: `verify()` loops over the ground truth, so a missing `termination_charge_8m` fails
with no quote and gives HIGH. The real gap is everything we did **not** think to ask for: if the task were "list
every obligation" and the answer skipped 9.2, every check would pass, because the checks only look at what the model
returned. **Proposed check - clause coverage:** `split_clauses()` already lists the clauses in the source (4.1, 4.2,
7.1, 9.2, 11.4); require the model to cite a clause number for every statement, and flag any source clause that is
cited by nothing as `UNCOVERED` (at least MEDIUM, so a person reads that clause). A missing clause is invisible to
checks that only inspect the answer; it is only visible when you compare the answer against the full source.

---

## Part E - Approved-tools guideline

See `docs/Approved_Tools_Guideline_DRAFT.md` (one page, clearly marked as a draft for Security and Legal review).
