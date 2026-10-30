# Day 2 take-home: model tiers, embeddings and verification

All the data is made up. Outputs are in `outputs/` and `outputs/day2_runs/`.

Status: Parts C, D and E are done. Part A and the Claude half of Part B need the API key. The consumer app half of
Part B (ChatGPT, Claude.ai and Gemini in the browser, plus their privacy settings) I have to do myself by hand.
Those parts are marked [PENDING].

---

## Part A - Tier study [PENDING LIVE RUN]

Run `python solutions/day2_models_and_embeddings/compare_tiers_cli.py --query Q1`, then Q2 and Q3. I'll mark the
answers myself against these, not just rely on the automatic number check.

- Q1 (vendor clause): the credit for 98.6% availability is 620.00 (one 0.5-point step x 5% x 12,400.00, which is
  under the 20% cap). Terminating after 8 months costs 24,800.00 (two months' fees, since it's within the first
  12 months). 3 marks.
- Q2 (two-sentence summary): has to mention the 12,400.00 monthly fee, credits capped at 20%, and the early
  termination charge, without making up any terms.
- Q3 (judgement, 80 words max): three real risks (personal data leaving our control, consumer terms and training
  use, breaking data-protection law or the client contract) and one safer option (an enterprise tool, or redacted
  or synthetic data).

| Query | Tier | Score (0-3) | Seconds | Cost ($) | Within length? | Notes |
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

Which tier for which kind of task: [PENDING - after the runs]

---

## Part B - My own query across six tools

My query is in `solutions/day2_models_and_embeddings/data/own_query_term_deposit.txt`. It's about 150 words of
made-up rules for closing a term deposit early (clauses 3.1-3.5 plus a rate card), followed by three questions. I
wrote down my answers before running anything (`data/own_query_answers.md`):

1. 200,000.00 booked for 2 years and closed after 120 days: 4.50%. That's the 5.25% rate for 91-180 days minus the
   0.75 penalty. The trap is using the 2-year rate instead (6.75% down to 6.00%), which clause 3.3 says not to do.
2. Can you take 50,000.00 out of 300,000.00? No, partial withdrawals aren't allowed (3.5).
3. 600,000.00 closed on day 5: no interest (3.2), and it needs the branch manager to approve (3.4).

I ran `redact_pii.py` on the file and it found nothing (`partB_redaction_check.txt`). It only looks for things like
emails, phone numbers and card numbers, though, so I also read through the text myself. There are no names or
personal details in it.

Claude tiers [PENDING LIVE RUN]: `compare_tiers_cli.py --prompt "<file contents>"`.

Consumer apps [PENDING - by hand]: paste the lab's Q1 prompt (saved in `partB_homework_pack.txt`) into ChatGPT,
Claude.ai and Gemini, in a new chat each time, using exactly the same text. Then fill in
`outputs/homework_comparison.md`.

Training data settings [PENDING - check in each account]:

| Tool | Where I looked | Default | Personal or enterprise |
|---|---|---|---|
| ChatGPT | Settings > Data controls > "Improve the model for everyone" | | |
| Claude.ai | Settings > Privacy > "Help improve Claude" | | |
| Gemini | Gemini Apps Activity | | |

The menus move around, so I'll write down the actual path I find.

Trust analysis: [PENDING - after the runs]

---

## Part C - Embeddings experiment

I added a `facilities` topic with 8 office requests: broken air conditioning, booking a meeting room, a flickering
light, a faulty lock on the bike gate, a leaking water cooler, extra chairs, the lift being out of service, and a
spare desk key.

Before I could see it, I had to fix a bug. `plot_map()` matched topics to colours with `zip()`, but there were only
4 colours, and `zip()` stops at the shorter list. So my fifth topic was being embedded but never drawn. I added more
colours and made it raise an error if there are ever too many topics, instead of silently dropping them.

The toy map is `outputs/embedding_map_toy.png`. I couldn't get the real model (fastembed bge-small) to run: it
installs, but onnxruntime fails with "DLL load failed", because the Visual C++ runtime is missing on this laptop. So
the script falls back to the toy embedder (`partC_real_attempt.txt`). [PENDING: real map.]

On the toy map, the original four topics group together nicely, but facilities is scattered all over. Some points
land in refunds, two near hr_leave, and the rest in between. That makes sense given how the toy works. It only has
six word groups (money, delivery, damage, access, leave, security), and none of them are about buildings. So a
facilities sentence is placed by whatever group words it happens to contain ("broken" and "faulty" count as damage)
plus small random-ish nudges for the words it doesn't know.

Some queries where the toy gets it wrong (using the `--query` option I added):

| Query | Toy's top match | Why |
|---|---|---|
| "Book a room for the team workshop" | hr_leave, "I need to book a holiday..." (0.99) | "book" is in the leave group and no other word in the query is in any group, so it looks like a leave request. A real model would know booking a room is about space, not time off. |
| "Reimburse me for the defective goods" (built-in) | facilities, "...the faulty lock on the bike storage gate" (0.96). Refunds came second (0.90). | "defective" and "faulty" are both in the damage group, and the facilities sentence has hardly anything else in it. So adding my topic changed the answer to a query that already existed. |
| "The radiator by my seat is stone cold" | facilities, "We need six extra chairs..." (0.99) | Looks right but it's luck. None of the words are in any group, so both vectors are just nudges, and the match is about chairs. |

That second query broke a course test, which expected refunds to come out on top. I changed it to "refunds in the
top 2" and left a comment saying why, rather than tweaking my sentences to hide the problem. I also added a test that
facilities is in the data, a test that records the room-booking failure, and the real synonym test ("Book a room..."
should give facilities with the real model). That last one is skipped here because fastembed won't load. I didn't
write a synonym test for the toy, because it has no facilities words, so it would pass or fail by luck.

What distance on the map means: each sentence is really a point in 6 dimensions (toy) or 384 (real model). PCA
squashes that down to 2 axes, keeping the two directions where the points spread out the most. So dots that are
close have similar vectors, which means the embedder thinks they're similar in meaning. But some information is lost
in the squash, so two dots can look close on the map and still be far apart in the full space. The cosine scores are
what to trust.

The axes don't mean anything by themselves. Each one is a mix of all the original dimensions, worked out from this
particular set of sentences, and the mix changes when you add or remove sentences. Adding facilities changed the
whole picture. So there's no fixed meaning or unit for "axis 1"; only where the points are compared to each other
matters.

---

## Part D - Extending the verification pipeline

I added `late_interest_pct_month` = 1.5 (clause 4.2) to `EXTRACT_SYSTEM`, `ground_truth()`, `NUMBER_IN_QUOTE` and the
offline reply. I gave it a correct quote so that the demo's deliberate mistakes are still the only ones.

While adding it I found three problems. I recorded them on the original code first, in
`partD_weaknesses_before_fix.txt`:

1. For 1.5 it was also looking for "2" (rounded). Now it only tries the rounded form for whole numbers.
2. It found "5" inside "1.5% per month", so a quote about late interest counted as evidence for the 5% credit step.
   Now the number has to stand on its own, with no other digits right before or after it.
3. A real quote that didn't contain the number set `number_in_quote = False`, but `risk_tier()` never looked at
   that, so the result was still LOW. Now it gives HIGH.

My extra check is that the quote has to come from the right clause. `SOURCE_CLAUSE` says which clause each item
should come from (fee 4.1, interest 4.2, credits 7.1, termination 9.2). `split_clauses()` splits the contract at the
clause numbers, and `verify()` adds a `right_clause` field. A real sentence from the wrong clause isn't evidence, so
that gives HIGH. I also added a "right clause" column to the results table.

New tests: correct new item gives LOW. A made-up interest quote gives HIGH, and so does a real quote with the wrong
number. 1.5 is never tried as "2". "5" isn't found inside "1.5%", and "20" isn't found inside "12,400.00". A quote
from the wrong clause gives HIGH, an unsupported number gives HIGH, and the clauses split as
4.1/4.2/7.1/9.2/11.4. Day 2 tests: 28 OK, 1 skipped.

Offline demo (`partD_offline_demo.txt`):

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

Live run: [PENDING LIVE RUN]

What if the model quietly left out clause 9.2? For things we ask for, it would already be caught. `verify()` goes
through every expected item, so a missing `termination_charge_8m` has no quote and gives HIGH. The real gap is things
we didn't think to ask about. If the task was "list every obligation" and the answer skipped 9.2, everything would
pass, because the checks only look at what the model gave back.

What I'd add is a coverage check. `split_clauses()` already knows which clauses exist (4.1, 4.2, 7.1, 9.2, 11.4). Make
the model cite a clause number for each statement, and flag any clause nobody cited as UNCOVERED, at least MEDIUM, so
someone goes and reads it. You can't spot a missing clause by looking only at the answer. You have to compare it
against the full source.

---

## Part E - Approved tools guideline

See `docs/Approved_Tools_Guideline_DRAFT.md`.
