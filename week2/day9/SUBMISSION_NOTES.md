# Individual Submission Notes

This submission keeps the assignment's required behavior but uses an original, evidence-first design.

## Distinct Choices

- The classification prompt uses a first-pass triage voice and separates escalation signals from ordinary category selection.
- The reply prompt uses Nisha as the case-owner persona. The persona emphasizes warmth without unauthorized promises.
- The policy prompt calls its result a compact policy digest and explicitly treats the policy text as the complete evidence base.
- The output contracts remain strict so that the automated checks can still prove correctness.

## Why These Choices Matter

The wording makes the three prompts feel like parts of one bank workflow while giving each task a different operating mindset: triage, case ownership, and evidence-based policy lookup. These are deliberate design decisions for this submission, not changes to the required scoring interface.