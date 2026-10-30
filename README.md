# GenAI Ops training - my assignments

My work for the GenAI Ops course, one folder per day. Each day folder is a copy of the course repo for that day
with my changes added, so you can run the tests from inside it with `python -m unittest discover -s tests`.

```
week1/
  day1/  automation-to-agentic spectrum
  day2/  model tiers, embeddings, verification
  day3/  vector maths and cosine similarity
```

Each day has a `README_DAYn.md` (what I changed and what's left) and a write-up in `docs/`.

What I picked:
- Day 1: IT access requests for Part A, a 14-day damage-report window for Part B, and two new injection tickets
  (a fake tool result and a hidden Portuguese instruction) for Part C. My fix was a check on replies.
- Day 2: a term-deposit closure question for Part B, a new `facilities` topic for Part C, and a late-interest
  item plus a "right clause" check for Part D.
- Day 3: Scenario 5 (legacy modernization) for Task C.

Where things stand:
- Day 1: 69 tests pass. Levels 2-5 still need to be run with the API key.
- Day 2: 66 pass, 1 skipped. The tier runs need the API key, and the consumer app comparison has to be done by hand.
- Day 3: done apart from the photo of my handwritten working. One course test fails on purpose (see the write-up).

All the data here is made up. There's no `.env` file or API key in the repo.
