# Missing pieces

Write these with Claude Code. You must be able to explain every line, and every sentence of every prompt.

| Id | File | What | Done |
| --- | --- | --- | --- |
| M1 | prompts/improved/t1_classify.md | Few-shot classification prompt: all four ingredients, `{{EXAMPLES}}` and `{{INPUT}}`, JSON output with category, severity, escalate | [x] |
| M2 | prompts/improved/t2_reply.md | Role + persona reply prompt: all four ingredients, the desk's priority order, word limit, what must never appear | [x] |
| M3 | prompts/improved/t3_summary.md | Zero-shot summary prompt: all four ingredients, strict JSON with the summary fields, numbers only from the policy text | [x] |
| M4 | prompt_lint.py | `lint()`, following the rules in its docstring | [x] |
| M5 | compare.py | `main()`: score weak and improved outputs, print the before/after table, write output/comparison.csv and output/comparison.md | [x] |
| M6 | tests/test_lab.py | Tests for lint() on the six worksheet snippets and on your three improved prompts (4/4 each, right strategy), for the checks you fixed, and for data hygiene | [x] |
