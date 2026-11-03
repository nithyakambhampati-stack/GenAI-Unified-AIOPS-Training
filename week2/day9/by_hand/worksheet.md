# By-hand worksheet: Day 9

Read each prompt snippet below (they are also in `by_hand/snippets.json`) and decide, on paper:

- which of the four ingredients it has: **context, constraints, priority, output**
- its shot type: **zero-shot, one-shot or few-shot**
- whether it is **role**-based (a line starting "You are") and whether it has a **persona**

Use the strict rule from `prompt_lint.py`: an ingredient counts only if it has its own markdown heading
with real content under it. Then fill `by_hand/my_answers.json` (true or false for each ingredient, role and
persona; "zero-shot", "one-shot" or "few-shot" for shots) and run `python check_by_hand.py`.
Where you and the linter disagree, decide who is wrong, and whether the rule itself is fair.

## S1
```
Summarise the attached statement.
```

## S2
```
## Context
You are a credit analyst at a retail bank. The input is a personal loan application.

## Output
Return JSON with the keys decision and reason.
```

## S3
```
## Context
The input is a customer complaint from the bank's app.

## Constraints
Use only these categories: card_fraud, loan_emi, other.

## Priority
## Output
Return only JSON with the key category.

Input: My card was used in Singapore without my knowledge.
Output: {"category": "card_fraud"}

Input: My EMI date changed.
Output: {"category": "loan_emi"}
```

## S4
```
Persona: Asha, a calm senior customer care officer.

## Context
<!-- describe the customer and the case here -->

## Constraints
Never write a full card or account number.

## Weightage
Compliance first, then empathy, then brevity.

## Desired output
A reply of at most 120 words that ends with the complaint reference.
```

## S5
```
You are a fraud analyst.
Context: card transactions are listed below.
Input: Rs 4,500 at a hotel in Goa that the customer did not make.
Output: {"category": "card_fraud"}
```

## S6
```
# Priority
Accuracy over speed.

# Output
One line, no more than 20 words.

{{EXAMPLES}}
```
