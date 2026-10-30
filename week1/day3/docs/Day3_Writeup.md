# Day 3 - Vector maths (unguided session)

## Checklist

- [x] Guided steps 1-4 (outputs in `outputs/`, step 1 was 12/12)
- [x] Task A - three pairs by hand. Still need to add the photo of my paper working (`docs/TaskA_working_photo.jpg`)
- [x] Task B - `nearest()`, tests, prompt log, checker 4/4
- [x] Task C - Scenario 5, legacy modernization copilot
- [x] Task D - decision table
- [x] Task E - a misleading score, and my own explanation
- [x] All three stretch tasks
- [x] Only made-up data, no keys

---

## A. Calculate by hand again

What I predicted before working anything out: overdraft/chargeback would be the closest, since both are about money
going in and out of an account and both end up with customer service. Then KYC/AML, with complaint/fraud the least
similar.

| Pair | Dot | Cosine | Distance | My guess | Actual |
|---|---|---|---|---|---|
| overdraft / chargeback | 22 | 0.773 | 3.606 | 1st | 2nd |
| KYC / AML | 24 | 0.802 | 3.464 | 2nd | 1st |
| complaint / fraud | 10 | 0.358 | 6.000 | 3rd | 3rd |

Working (the order is lending, fraud_risk, kyc_compliance, customer_service):

- overdraft [4,2,1,3] and chargeback [1,4,1,3]: dot = 4+8+1+9 = 22. Lengths √30 = 5.477 and √27 = 5.196.
  Cosine = 22 / 28.46 = 0.773. Distance = √(9+4+0+0) = √13 = 3.606.
- KYC [1,1,5,1] and AML [0,4,4,0]: dot = 0+4+20+0 = 24. Lengths √28 = 5.292 and √32 = 5.657.
  Cosine = 24 / 29.93 = 0.802. Distance = √(1+9+1+1) = √12 = 3.464.
- complaint [0,1,0,5] and fraud [0,5,2,1]: dot = 0+5+0+5 = 10. Lengths √26 = 5.099 and √30 = 5.477.
  Cosine = 10 / 27.93 = 0.358. Distance = √(0+16+4+16) = √36 = 6.000.

I checked all of them with `python vector_math.py <word1> <word2>` and they match (`outputs/taskA_check.txt`).

I got the top two the wrong way round. I was thinking about what the products actually are, but the vectors only
know about the four themes. KYC and AML are both strong on compliance and fraud risk. Overdraft is mostly lending
and chargeback is mostly fraud risk, so they point in more different directions than you'd expect from the names.

## B. Extending it with Claude Code

`nearest(query, candidates, metric)` is in `my_vector_math.py`, and every prompt is in `docs/TaskB_prompt_log.md`.
The main things I found and fixed:

1. When two candidates tied, the result depended on the order of the dict. I added a tie-break on the name and
   tested it with both orders.
2. If one candidate was a zero vector, the whole thing crashed without saying which one. Now the error names it.
3. My first test for `nearest` couldn't actually fail. Both metrics gave the same order on the data I'd used, so I
   replaced it with data where cosine and distance give opposite orders.

After that, the checker still gives 4/4 and my own tests are 14 OK.

The course test suite gives 15/16. The one failure is `test_stub_reports_todo`, which checks that
`my_vector_math.py` still has the original empty stubs. That can only pass before you write the functions, so I've
left the trainer's test as it is.

## C. My scenario: legacy modernization copilot (Scenario 5)

The idea: a team moving old jobs off a legacy system needs to decide which ones to migrate together. Each item is a
made-up job, and the four numbers say how much of its work is batch scheduling, data transformation, file
transfer/IO, and error handling.

| Item | batch | transform | file I/O | errors |
|---|---|---|---|---|
| COBOL batch posting job | 5 | 3 | 2 | 2 |
| Informatica mapping | 1 | 5 | 2 | 1 |
| Nightly reconciliation | 5 | 3 | 1 | 3 |
| Monthly report extract | 2 | 3 | 4 | 1 |
| SFTP file transfer | 2 | 0 | 5 | 2 |
| Abend error handler | 1 | 0 | 1 | 5 |

My guess before running it: COBOL posting and nightly reconciliation would be the most similar, and Informatica and
the abend handler the least. I also thought the monthly report extract would be close to several items, because it
does a bit of everything.

Result (`outputs/taskC_scenario_matrix.txt`): COBOL posting and reconciliation were the most similar (cosine 0.98,
distance 1.41), and Informatica and the abend handler the least (0.28), so both guesses were right. The report
extract did score 0.82-0.85 against three different jobs (COBOL posting, Informatica and SFTP). A vector that's a bit
of everything ends up close to everything, so it doesn't tell you much on its own. I didn't change any numbers after
seeing the results.

What it would mean for the team: the posting job and the reconciliation do the same kind of work, so they're good
candidates for the same migration wave and the same scheduler. But there's a lot my four numbers can't see: whether
reconciliation reads the posting job's output (which would fix the order they have to move in), month-end and
year-end timing, and who owns each job. Being similar doesn't mean they're safe to move together.

## D. Decision cases

| Case | Metric | Threshold | Who checks |
|---|---|---|---|
| 1. Policy search assistant answers or says "I don't know" | Cosine, because questions and policy text are very different lengths, and cosine compares topic rather than size (step 4). I'd also split policies into similar-sized chunks so long documents don't win just by covering everything. | Take about 100 real questions where we know the right snippet (or know there isn't one), plot the top score for right and wrong answers, and set the cut-off where wrong answers mostly stop. Redo it whenever the policies change. | Above the line: answer and link the snippet. Below: "I don't know" and pass to the policy team. In between: show the agent the top 2-3 snippets and let them pick. Nothing goes to a customer without the agent. |
| 2. KYC tool compares an extracted address to the one on file | Both, but neither decides on its own. Cosine on embeddings handles different formats ("Flat 4, 12 High St" vs "12 High Street, Apt 4"). An exact check on house number and postcode catches one changed digit, which embeddings barely notice. | Use past cases marked match/mismatch to set a high cosine bar, and also require the house number and postcode to match exactly. | Exact match plus a high score: confirm automatically. Anything else goes to a KYC analyst. Never reject or change an address automatically. |
| 3. Pipeline suggests two customer records might be duplicates | Distance on the normalised structured fields (date of birth, ID numbers, postcode), plus cosine on the name and address text | Have data stewards label pairs at different scores, and pick a threshold that keeps wrong merges close to zero, even if we miss some duplicates. | It only suggests. A data steward approves every merge, and merges are logged and can be undone. Merging two different customers mixes up their money and data, which is much worse than missing a duplicate. |

## E. Where it breaks

Misleading pair, from my scenario (`day3_extras.py`):

- "Retire the COBOL batch posting job after cut-over" -> [5, 3, 2, 2]
- "Keep the COBOL batch posting job running; month-end close still depends on it" -> [5, 3, 2, 3]
- cosine 0.990, distance 1.0

Both requests are about the same job with the same kind of work, so all four numbers line up, but one says turn it
off and the other says keep it. My dimensions have nowhere to put the actual decision. Real embeddings have the same
problem: most of the words and the topic are shared, and a small word like "retire", "keep" or "not" only shifts the
vector a little, so opposite instructions can still score over 0.9. In a bank, acting on the wrong one could switch
off a job that month-end close needs.

What I'd do about it: use similarity to find candidates, never to make the decision. Before anything happens, a
simple rule-based check pulls out the action (retire, keep, pause) and the job ID from both texts and makes sure
they match. And any change to a production job needs a named person to approve it.

Why closer vectors mean similar meaning, in my own words: each number answers "how much is this about theme X?" If
two items have their numbers in the same proportions, they're about the same mix of things, so their arrows point
the same way, and cosine is measuring that angle. With my legacy jobs, the COBOL posting job and the nightly
reconciliation are both mostly batch work with some transformation, so their arrows almost sit on top of each
other. And in real life those are the jobs a team would look at together. But it's only as good as the themes you
chose. Anything the dimensions leave out, like retire versus keep, it just can't see.

## F. Stretch tasks (`outputs/day3_extras_output.txt`)

1. Unit vectors: for COBOL posting vs the report extract, cosine is 0.816982. After making both unit length, the
   squared distance is 0.366035, and 2 - 2 × 0.816982 is also 0.366035. So for unit vectors, ranking by cosine and by
   distance gives the same order.
2. Centroids: wave 1 (posting + reconciliation) has centre [5.0, 3.0, 1.5, 2.5], and wave 2 (Informatica, report
   extract, SFTP) has [1.67, 2.67, 3.67, 1.33]. The cosine between the two centres is 0.770. The abend handler isn't
   in either wave, but it's closer to wave 1 (0.561 vs 0.461), so it would go with the batch jobs. Watching how a
   group's centre moves over time is basically how a drift check works.
3. Sensitivity: adding 2 to COBOL posting's file_transfer_io raises its cosine with the report extract by 0.102, more
   than any other dimension. Adding 2 to batch_scheduling (already 5, and the direction where they disagree) lowers
   it by 0.075. So a change matters most in a dimension where the two items differ. No dimension has a fixed weight.
