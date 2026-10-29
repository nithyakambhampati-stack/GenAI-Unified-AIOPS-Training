# Prompts for Claude Code (Step 2)

Open the VS Code terminal in this folder, start Claude Code (`claude`), and paste the prompts one at a time.
After EVERY answer: read the code, run it, and check it (Step 3). Claude Code can be confidently wrong.

## Prompt 1 - write the functions
```
Open my_vector_math.py. Implement the four functions dot, norm, cosine_similarity and euclidean_distance.
Rules: standard library only (the math module is allowed), no numpy. Add a short comment above each line of working.
cosine_similarity must raise ValueError for a zero vector. Every function must raise ValueError if the two vectors
have different lengths. Do not open or copy vector_math.py.
```

## Prompt 2 - check your own work (before you run the checker)
```
Without running anything, walk me through cosine_similarity([3, 4], [4, 3]) line by line and show the number at each step.
```
Compare Claude's numbers with your hand calculation from Step 1. They should match: dot 24, lengths 5 and 5, cosine 0.96.

## Prompt 3 - explain it back
```
Explain in plain words, for a banking operations manager, what cosine similarity measures and why two vectors with
cosine similarity close to 1 are treated as "similar in meaning". Use a bank example. Maximum 120 words.
```
Ask yourself: is every sentence true? Anything you cannot explain to your partner should be challenged.

## Prompt 4 - break it
```
Write five test cases for my four functions, including edge cases (zero vector, different lengths, negative numbers).
Put them in test_mine.py using unittest, then run them.
```

## Prompt 5 - extend (unguided session)
```
Add a function nearest(query, candidates, metric="cosine") to my_vector_math.py that returns the candidate names
sorted from most to least similar. For cosine, higher is better; for euclidean, lower is better.
```

## Good habits
* Ask Claude Code to show its working, then compare with yours.
* If the checker says FAIL, paste the failure line back and ask Claude Code to explain the bug before fixing it.
* Never accept code you cannot explain.
