# Homework comparison - Q1: Contract clause analysis (reasoning + arithmetic + careful reading)

## Fair-test rules
- New chat for each tool; identical pasted text; synthetic data only.
- Record the model name and plan each app shows.

## Prompt used
```
You are helping a procurement analyst. Using ONLY the clauses below, answer:
1. In one month availability was 98.6%. What service credit is owed in money? Show the calculation.
2. The Customer terminates after 8 months. What is the early-termination charge in money?
3. Can the Supplier process customer data in India without asking? Quote the clause.
Keep the answer under 150 words.

<clauses>
SERVICES AGREEMENT - EXTRACT (fictional, for training use)

4.1 Fees. The Customer shall pay the Supplier a fixed monthly fee of 12,400.00 for the
Managed Support Service, invoiced on the first business day of each month.

4.2 Late payment. Invoices unpaid after 30 days incur interest at 1.5% per month on the
overdue amount.

7.1 Service credits. If monthly availability falls below 99.5%, the Supplier shall credit
5% of that month's fee for each full 0.5 percentage points below 99.5%, up to a maximum
credit of 20% of the monthly fee.

9.2 Termination for convenience. Either party may terminate on 90 days' written notice.
If the Customer terminates in the first 12 months, an early-termination charge equal to
two months' fees applies.

11.4 Data location. Customer personal data shall be processed only within the European
Economic Area unless the Customer gives prior written consent.

</clauses>
```

## Reference answer (check yours against this)
- Q1: 99.5 - 98.6 = 0.9 points -> 1 full 0.5-point step -> 5% of 12,400.00 = 620.00
- Q2: two months' fees = 24,800.00 (terminated within first 12 months)
- Q3: No - clause 11.4 requires prior written consent for processing outside the EEA

## Results

| Question | ChatGPT | Claude.ai | Gemini |
|---|---|---|---|
| Model / plan shown in the app |   |   |   |
| Credit amount correct (620.00)? |   |   |   |
| Termination charge correct (24,800)? |   |   |   |
| Quoted clause 11.4 for the data question? |   |   |   |
| Stayed under 150 words? |   |   |   |
| Time to answer (seconds, roughly) |   |   |   |
| Did it add anything NOT in the clauses? |   |   |   |

## Privacy settings check (do this once per tool)
- Where is the setting that controls whether chats are used to improve the model? Is it on or off by default?
- Is the account personal/free or enterprise? What does that change about what you may paste?

## Reflection (3-5 sentences)
Which answer would you trust without checking, and why? What would you verify first?
