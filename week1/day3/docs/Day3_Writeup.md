# Day 3 - Vector Mathematics: unguided session write-up

## Checklist

| Item | Done | Where |
|---|---|---|
| Guided steps 1-4 run | Yes | `outputs/step1_by_hand_check.txt` (12/12), `outputs/step3_check_my_code.txt`, `outputs/step4_why_cosine.txt` |
| Task A - three pairs by hand, prediction first | Yes | Section A below. **Photo of handwritten working: to be added** (`docs/TaskA_working_photo.jpg`) |
| Task B - `nearest()`, tests, prompt log, 4/4 PASS | Yes | `my_vector_math.py`, `test_mine.py` (14 OK), `docs/TaskB_prompt_log.md` |
| Task C - own scenario (Scenario 5, Legacy modernization copilot) | Yes | `data/my_scenario.json`, `outputs/taskC_scenario_matrix.txt`, section C |
| Task D - decision table | Yes | Section D |
| Task E - misleading score + own explanation | Yes | Section E, `day3_extras.py`, `outputs/taskE_and_stretch.txt` |
| Stretch tasks (all three) | Yes | Section F |
| All data synthetic, no keys, nothing sensitive | Yes | No `.env`, no real names, accounts or jobs |

---

## A. Calculate by hand again

**Prediction, written before calculating:** overdraft/chargeback most similar (both are about money going in and out
of an account, and both end up with the service team), KYC/AML second, complaint/fraud least similar.

| Pair | Dot product | Cosine similarity | Euclidean distance | My prediction | Actual rank |
|---|---|---|---|---|---|
| overdraft and chargeback | 22 | 0.773 | 3.606 | 1 | 2 |
| KYC and AML | 24 | 0.802 | 3.464 | 2 | 1 |
| complaint and fraud | 10 | 0.358 | 6.000 | 3 | 3 |

Working (vectors are lending, fraud_risk, kyc_compliance, customer_service):

* overdraft [4,2,1,3], chargeback [1,4,1,3]: dot 4+8+1+9 = 22; lengths √30 = 5.477 and √27 = 5.196;
  cosine 22 / 28.46 = 0.773; distance √(9+4+0+0) = √13 = 3.606.
* KYC [1,1,5,1], AML [0,4,4,0]: dot 0+4+20+0 = 24; lengths √28 = 5.292 and √32 = 5.657;
  cosine 24 / 29.93 = 0.802; distance √(1+9+1+1) = √12 = 3.464.
* complaint [0,1,0,5], fraud [0,5,2,1]: dot 0+5+0+5 = 10; lengths √26 = 5.099 and √30 = 5.477;
  cosine 10 / 27.93 = 0.358; distance √(0+16+4+16) = √36 = 6.000.

All nine numbers match `python vector_math.py <word1> <word2>` (`outputs/taskA_check.txt`).

My prediction swapped the top two. I was thinking about the products, but the vectors only know the four themes:
KYC and AML share two strong themes (compliance and fraud risk), while overdraft is mainly lending and chargeback is
mainly fraud risk, so they point in more different directions than the everyday wording suggests.

## B. Extend with Claude Code

`nearest(query, candidates, metric)` is in `my_vector_math.py`. Details of every prompt and fix are in
`docs/TaskB_prompt_log.md`. Short version of what I challenged and fixed:

1. **Ties depended on dict order** - fixed with a name tie-break; tested in both orders.
2. **A zero-vector candidate crashed the ranking without naming it** - the error now names the candidate.
3. **A test that could not fail** - the first `nearest` test used data where both metrics agree; replaced with data
   where cosine and distance must give opposite orders.

Checker after the change: 4/4 PASS. Own tests: 14 OK.

Note on the course test suite: `python -m unittest discover -s tests` gives 15/16. The one failure,
`test_stub_reports_todo`, checks that `my_vector_math.py` still contains the original stubs; it can only pass before
the functions are written, so I left the trainer's test unchanged.

## C. My scenario: Legacy modernization copilot (Scenario 5)

A modernization team must decide which legacy jobs to migrate together. Each item is a synthetic job description;
the four dimensions say where the job's work lies: `batch_scheduling`, `data_transformation`, `file_transfer_io`,
`error_handling`.

| Item | batch | transform | file I/O | errors |
|---|---|---|---|---|
| COBOL batch posting job | 5 | 3 | 2 | 2 |
| Informatica mapping | 1 | 5 | 2 | 1 |
| Nightly reconciliation | 5 | 3 | 1 | 3 |
| Monthly report extract | 2 | 3 | 4 | 1 |
| SFTP file transfer | 2 | 0 | 5 | 2 |
| Abend error handler | 1 | 0 | 1 | 5 |

**Prediction before running:** most similar = COBOL batch posting / Nightly reconciliation; least similar =
Informatica mapping / Abend error handler; surprise = Monthly report extract would sit close to *several* items,
because it does a bit of everything.

**Result** (`outputs/taskC_scenario_matrix.txt`): most similar COBOL batch posting / Nightly reconciliation (cosine
0.98, distance 1.41); least similar Informatica mapping / Abend error handler (0.28). Both as predicted. The surprise
held: Monthly report extract scores 0.82-0.85 with three different items (COBOL posting, Informatica, SFTP). An
"all-rounder" vector is close to everything and therefore a poor signal on its own. I kept my numbers.

What it means for the bank team: the posting job and the reconciliation are candidates to migrate in the same wave
and onto the same target scheduler, because they do the same kind of work. A human still has to check the things my
four numbers cannot see: whether reconciliation reads the posting job's output (a hard dependency and cut-over
order), the business calendar (month-end, year-end), and who owns each job. Similar is not the same as safe to
move together.

## D. Decision cases

| Case | Metric and why | How I would choose the threshold | Who reviews / what is automated |
|---|---|---|---|
| 1. Knowledge-search assistant answers a policy question or says "I don't know" | **Cosine.** Policy snippets and questions differ a lot in length; cosine compares topic, not size (Step 4, experiment 1). Chunk the policies to similar sizes so very long documents do not win by covering everything. | Take about 100 real agent questions labelled with the right snippet (or "no answer exists"). Plot the top score for correct and wrong answers and set the cut-off where wrong answers become rare, re-checked every time the policy library changes. | Above the threshold: answer with the snippet quoted and linked. Below it: "I don't know", routed to the policy team. Grey band: show the top 2-3 snippets to the agent and let them choose. Nothing customer-facing is sent without the agent. |
| 2. KYC tool compares an extracted address with the address on file | **Both, but neither decides alone.** Cosine on embeddings catches format differences ("Flat 4, 12 High St" vs "12 High Street, Apt 4"); a character or field-level comparison (house number, postcode) catches a single changed digit, which embeddings miss because the meaning barely changes. | From past remediation cases labelled match / mismatch, choose a high cosine bar for "same" and require the house number and postcode to match exactly. | Exact field match + high score: auto-confirm. Anything else: flag to a KYC analyst. Never auto-reject or auto-update an address: identity and money are at stake. |
| 3. Data pipeline suggests two customer records that may be duplicates | **Distance on normalised fields** for the structured parts (date of birth, ID numbers, postcode) plus **cosine** on free-text name/address. | Sample pairs scored at different levels and have data stewards label them; pick the threshold that keeps false merges near zero, accepting that some duplicates are missed. | The pipeline only *suggests*. A data steward approves every merge, and merges must be reversible and logged. A wrong merge mixes two customers' money and data, so the cost of a false positive is far higher than a missed duplicate. |

## E. Where it breaks, and my own explanation

**Misleading pair** (from my scenario, `day3_extras.py`):

* "Retire the COBOL batch posting job after cut-over" → [5, 3, 2, 2]
* "Keep the COBOL batch posting job running; month-end close still depends on it" → [5, 3, 2, 3]
* cosine **0.990**, distance 1.0

The two change requests describe the same job, with the same scheduling, data and file work, so every dimension
lines up, but one says switch it off and the other says keep it. My four dimensions have nowhere to store the
decision itself. Real embeddings fail in a similar way: most of the words, entities and topic are shared, and a small
word like "retire", "keep" or "not" moves the vector only a little, so opposite instructions can still score above
0.9. In a bank, acting on the wrong one could stop a job that month-end close depends on. **Safeguard:** treat
similarity as "find candidates", never "decide". Before any action, a rule-based check extracts the action verb
(retire / keep / pause) and the job id from both texts and requires them to match, and any change to a production
job needs a named approver.

**Why closer vectors mean similar meaning, in my own words:** each number in a vector answers "how much is this item
about theme X?". If two items have their numbers in the same proportions, they are about the same mix of themes, so
their arrows point the same way, and cosine measures exactly that angle. In my work on legacy jobs, the COBOL
posting job and the nightly reconciliation are both mostly scheduled batch work with some data transformation;
their arrows almost overlap, and in practice they are the jobs a team would look at together. The closeness is only
as good as the themes the numbers capture: anything the dimensions leave out (like "retire" versus "keep") is
invisible to it.

## F. Stretch tasks (`outputs/taskE_and_stretch.txt`)

1. **Unit-vector identity:** COBOL batch posting vs Monthly report extract: cosine 0.816982; distance² of the unit
   vectors 0.366035; 2 - 2 × cosine 0.366035. Same number, so on unit-length vectors ranking by cosine and by
   distance give the same order.
2. **Centroids:** wave 1 (posting + reconciliation) centre [5.0, 3.0, 1.5, 2.5]; wave 2 (Informatica, report
   extract, SFTP) centre [1.67, 2.67, 3.67, 1.33]; cosine between centres 0.770. The unassigned Abend error handler
   is closer to wave 1 (0.561 vs 0.461), so it would go with the batch wave. Tracking how a group's centre moves
   over time is the idea behind a drift check.
3. **Sensitivity:** raising COBOL posting's `file_transfer_io` by 2 moves its cosine with the report extract by
   +0.102, more than any other dimension; raising `batch_scheduling` (already 5, and where they disagree in the other
   direction) lowers it by 0.075. A change matters most in a dimension where the two items differ, so no dimension
   has a fixed weight.
